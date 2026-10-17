#!/usr/bin/env python3
"""Deploy a verified bundle, refresh CDN, verify actual served bytes. No deletes."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
import os
from pathlib import Path
import socket
import ssl
import time
import urllib.error
import urllib.request
from urllib.parse import quote

from package import MARKER, encoded, sha, verify

DOMAIN = 'www.qintopia.cn'
APEX = 'qintopia.cn'
BUCKET = 'qintopia-1305166808'
REGION = 'ap-chengdu'


class COS:
    def __init__(self):
        from qcloud_cos import CosConfig, CosS3Client
        from qcloud_cos.cos_exception import CosServiceError
        self.error = CosServiceError
        self.client = CosS3Client(CosConfig(Region=REGION, Scheme='https',
            SecretId=os.environ['COS_SECRET_ID'], SecretKey=os.environ['COS_SECRET_KEY'],
            Token=os.environ.get('COS_SESSION_TOKEN') or None))

    def get(self, key):
        try:
            r = self.client.get_object(Bucket=BUCKET, Key=key)
            stream = r['Body'].get_raw_stream()
            try:
                return stream.read()
            finally:
                stream.close()
        except self.error as e:
            if e.get_status_code() == 404 and e.get_error_code() == 'NoSuchKey':
                return None
            raise

    def put(self, key, data, content_type, immutable=False):
        cache = 'public, max-age=31536000, immutable' if immutable else 'no-cache, max-age=0, must-revalidate'
        self.client.put_object(Bucket=BUCKET, Key=key, Body=data, EnableMD5=True,
                               ContentType=content_type, CacheControl=cache)
        if self.get(key) != data:
            raise RuntimeError('COS read-back mismatch: ' + key)


class CDN:
    def __init__(self):
        from tencentcloud.common import credential
        from tencentcloud.cdn.v20180606 import cdn_client, models
        self.models = models
        self.client = cdn_client.CdnClient(credential.Credential(os.environ['CDN_SECRET_ID'],
            os.environ['CDN_SECRET_KEY'], os.environ.get('CDN_SESSION_TOKEN') or None), '')

    def call(self, action, payload):
        request = getattr(self.models, action + 'Request')()
        request.from_json_string(json.dumps(payload))
        return json.loads(getattr(self.client, action)(request).to_json_string())

    def check(self):
        r = self.call('DescribeDomainsConfig', {'Filters': [{'Name': 'domain', 'Value': [DOMAIN], 'Fuzzy': False}]})
        ds = r.get('Domains') or []
        if len(ds) != 1 or ds[0]['Domain'] != DOMAIN or ds[0]['Status'] != 'online' or ds[0]['Https']['Switch'] != 'on':
            raise RuntimeError('Expected online CDN with HTTPS enabled')

    def refresh(self, keys):
        urls = ['https://' + DOMAIN + '/' + quote(k, safe='/') for k in keys]
        # Small batches avoid record pagination and excessive per-request quotas.
        for start in range(0, len(urls), 20):
            task = self.call('PurgeUrlsCache', {'Urls': urls[start:start + 20]})['TaskId']
            deadline = time.monotonic() + 600
            while True:
                r = self.call('DescribePurgeTasks', {'TaskId': task, 'PurgeType': 'url', 'Limit': 100})
                logs = r.get('PurgeLogs') or []
                if any(x['Status'] == 'fail' for x in logs):
                    raise RuntimeError('CDN refresh failed: ' + task)
                if logs and len(logs) == r['TotalCount'] and all(x['Status'] == 'done' for x in logs):
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError('CDN refresh timed out: ' + task)
                time.sleep(10)


def http_get(key):
    # No cache-busting query: verify the same cache entry that visitors request.
    url = 'https://' + DOMAIN + '/' + quote(key, safe='/')
    req = urllib.request.Request(url, headers={'User-Agent': 'QinTopia-Release/1.0', 'Accept-Encoding': 'identity'})
    with urllib.request.urlopen(req, timeout=40) as r:
        if r.status != 200 or r.url != url:
            raise RuntimeError('Unexpected HTTP status or redirect: ' + key)
        return r.read()


def check_entry():
    for host in (APEX, DOMAIN):
        with socket.create_connection((host, 443), timeout=20) as raw:
            with ssl.create_default_context().wrap_socket(raw, server_hostname=host) as tls:
                if ssl.cert_time_to_seconds(tls.getpeercert()['notAfter']) - time.time() < 14 * 86400:
                    raise RuntimeError('Certificate expires within 14 days: ' + host)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    try:
        urllib.request.build_opener(NoRedirect).open('https://' + APEX + '/', timeout=30)
    except urllib.error.HTTPError as e:
        if e.code not in (301, 308) or e.headers.get('Location') != 'https://' + DOMAIN + '/':
            raise RuntimeError('Unexpected apex redirect') from e
    else:
        raise RuntimeError('Apex must redirect to www')


def verify_live(files, getter=http_get, attempts=6):
    pending = dict(files)
    for attempt in range(attempts):
        def check(item):
            key, expected = item
            try:
                return key, getter(key) == expected
            except Exception:
                return key, False
        with ThreadPoolExecutor(max_workers=6) as pool:
            for key, ok in pool.map(check, list(pending.items())):
                if ok:
                    del pending[key]
        if not pending:
            return
        if attempt + 1 < attempts:
            time.sleep(10)
    raise RuntimeError('Live byte verification failed: ' + ', '.join(sorted(pending)))


def probe(cos, cdn, live=verify_live, entry=check_entry):
    """Exercise both cloud writes and real CDN reads without changing website routes."""
    cdn.check()
    entry()
    key = '_site/connectivity-probe.txt'
    # Vary bytes to detect stale CDN content after an allegedly successful purge.
    data = ('QinTopia release probe ' + dt.datetime.now(dt.timezone.utc).isoformat() + '\n').encode()
    cos.put(key, data, 'text/plain; charset=utf-8')
    cdn.refresh([key])
    live({key: data})
    result = {'result': 'verified', 'scope': key, 'sha256': sha(data)}
    print(json.dumps(result), flush=True)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as f:
            f.write('COS authenticated upload/read-back, CDN purge, served bytes, TLS and apex redirect verified. Only `_site/connectivity-probe.txt` changed.\n')
    return result


def deploy(directory, cos, cdn, rollback=False, live=verify_live, entry=check_entry):
    manifest, files = verify(directory)
    digest = sha((directory / 'manifest.json').read_bytes())
    receipt = {'version': manifest['version'], 'revision': manifest['revision'], 'manifest_sha256': digest}
    if rollback:
        previous = json.loads((directory / 'deployed.json').read_text())
        if any(previous.get(k) != v for k, v in receipt.items()) or previous.get('result') != 'verified':
            raise ValueError('Rollback requires a successful receipt bound to this exact artifact')
    cdn.check()
    entry()
    old_marker = cos.get(MARKER)
    if old_marker and not rollback:
        previous_routes = set(json.loads(old_marker)['routes'])
        new_routes = {r['key'] for r in manifest['files'] if r['kind'] == 'route'}
        if previous_routes - new_routes:
            raise ValueError('Removing managed routes requires a separate URL migration plan')
    # Phase 1: immutable assets. Existing bytes may only be reused unchanged.
    for row in manifest['files']:
        if row['kind'] == 'asset':
            data = files[row['key']]
            old = cos.get(row['key'])
            if old is not None and old != data:
                raise RuntimeError('Immutable object conflict: ' + row['key'])
            if old is None:
                cos.put(row['key'], data, row['content_type'], immutable=True)
    print('Immutable assets uploaded and verified', flush=True)
    # Phase 2: public routes. Object stores do not offer multi-object atomic swaps.
    routes = [r for r in manifest['files'] if r['kind'] == 'route']
    routes.sort(key=lambda r: (r['key'] == 'index.html', r['key']))
    for row in routes:
        cos.put(row['key'], files[row['key']], row['content_type'])
    cdn.refresh([''] + [r['key'] for r in routes])
    entry()
    live(dict(files, **{'': files['index.html']}))
    # The marker records only a version whose routes AND assets have been served.
    marker = dict(receipt, routes=sorted(r['key'] for r in routes))
    cos.put(MARKER, encoded(marker), 'application/json; charset=utf-8')
    cdn.refresh([MARKER])
    live({MARKER: encoded(marker)})
    receipt.update(result='verified', verified_at=dt.datetime.now(dt.timezone.utc).isoformat())
    (directory / 'verified-deployment.json').write_bytes(encoded(receipt))
    print(json.dumps(receipt), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('deploy', 'rollback', 'probe'))
    p.add_argument('--directory', type=Path, default=Path('dist/release'))
    args = p.parse_args()
    cos, cdn = COS(), CDN()
    if args.command == 'probe':
        probe(cos, cdn)
    else:
        deploy(args.directory, cos, cdn, rollback=args.command == 'rollback')


if __name__ == '__main__':
    main()
