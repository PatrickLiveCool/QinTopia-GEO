#!/usr/bin/env python3
"""Deploy newer Tencent SSL certificates to one CDN domain. Python stdlib only."""
import argparse
import datetime as dt
import fcntl
import hashlib
import hmac
import json
import os
from pathlib import Path
import socket
import ssl
import sys
import time
import urllib.request
from urllib.parse import urlsplit

DOMAIN = 'www.qintopia.cn'
APEX = 'qintopia.cn'
CST = dt.timezone(dt.timedelta(hours=8))


def epoch(value):
    return dt.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=CST).timestamp()


def covers(name, domain=DOMAIN):
    name = name.lower().rstrip('.')
    domain = domain.lower().rstrip('.')
    return name == domain or (name.startswith('*.') and domain.count('.') == name.count('.') and domain.endswith(name[1:]))


def eligible(cert, current_expiry, now):
    names = [cert.get('Domain') or ''] + (cert.get('SubjectAltName') or [])
    try:
        return (cert.get('Status') == 1 and any(covers(n) for n in names)
                and epoch(cert['CertBeginTime']) <= now
                and epoch(cert['CertEndTime']) > max(now, current_expiry))
    except (KeyError, ValueError, TypeError):
        return False


class API:
    def __init__(self, path):
        if Path(path).stat().st_mode & 0o077:
            raise RuntimeError('Credentials must not be accessible to group/others')
        self.creds = json.loads(Path(path).read_text())

    def call(self, service, action, payload):
        if service == 'cdn' and action == 'ModifyDomainConfig':
            if payload.get('Domain') != DOMAIN or payload.get('Route') != 'Https.CertInfo.CertId':
                raise RuntimeError('Refusing a write outside the certificate binding')
        version = {'ssl': '2019-12-05', 'cdn': '2018-06-06'}[service]
        host = service + '.tencentcloudapi.com'
        timestamp = int(time.time())
        date = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).strftime('%Y-%m-%d')
        body = json.dumps(payload, separators=(',', ':')).encode()
        sha = lambda x: hashlib.sha256(x).hexdigest()
        canonical = 'POST\n/\n\ncontent-type:application/json; charset=utf-8\nhost:' + host + '\n\ncontent-type;host\n' + sha(body)
        scope = date + '/' + service + '/tc3_request'
        to_sign = 'TC3-HMAC-SHA256\n' + str(timestamp) + '\n' + scope + '\n' + sha(canonical.encode())
        sign = lambda key, msg: hmac.new(key, msg.encode(), hashlib.sha256).digest()
        key = sign(('TC3' + self.creds['SecretKey']).encode(), date)
        key = sign(sign(key, service), 'tc3_request')
        signature = hmac.new(key, to_sign.encode(), hashlib.sha256).hexdigest()
        auth = 'TC3-HMAC-SHA256 Credential=' + self.creds['SecretId'] + '/' + scope + ', SignedHeaders=content-type;host, Signature=' + signature
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Host': host,
                   'Authorization': auth, 'X-TC-Action': action, 'X-TC-Version': version,
                   'X-TC-Timestamp': str(timestamp)}
        request = urllib.request.Request('https://' + host, data=body, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)['Response']
        if 'Error' in result:
            raise RuntimeError(action + ': ' + result['Error']['Code'] + ': ' + result['Error']['Message'])
        return result


def domain_config(api):
    result = api.call('cdn', 'DescribeDomainsConfig', {'Filters': [{'Name': 'domain', 'Value': [DOMAIN], 'Fuzzy': False}]})
    domains = result.get('Domains') or []
    if len(domains) != 1 or domains[0]['Domain'] != DOMAIN:
        raise RuntimeError('Expected exactly the configured CDN domain')
    return domains[0]


def candidates(api, current_expiry, now):
    found = []
    offset = 0
    while True:
        data = api.call('ssl', 'DescribeCertificates', {'SearchKey': APEX, 'CertificateStatus': [1], 'Offset': offset, 'Limit': 100})
        batch = data.get('Certificates') or []
        found.extend(c for c in batch if eligible(c, current_expiry, now))
        offset += len(batch)
        if not batch or offset >= data.get('TotalCount', offset):
            break
    for cert in sorted(found, key=lambda c: epoch(c['CertEndTime']), reverse=True):
        detail = api.call('ssl', 'DescribeCertificate', {'CertificateId': cert['CertificateId']})
        if detail.get('Deployable') is True and eligible(detail, current_expiry, now):
            return detail
    return None


def verify(expected_expiry):
    context = ssl.create_default_context()
    with socket.create_connection((DOMAIN, 443), timeout=20) as raw:
        with context.wrap_socket(raw, server_hostname=DOMAIN) as tls:
            cert = tls.getpeercert()
    actual = ssl.cert_time_to_seconds(cert['notAfter'])
    if actual < expected_expiry - 300:
        raise RuntimeError('CDN edge has not deployed the expected certificate expiry')
    request = urllib.request.Request('https://' + APEX + '/', headers={'User-Agent': 'QinTopia-CDN-Cert-Check/1.0'})
    with urllib.request.urlopen(request, context=context, timeout=30) as response:
        if response.status != 200 or urlsplit(response.url).hostname != DOMAIN:
            raise RuntimeError('Unexpected final homepage response')
        if not response.read(1024).strip():
            raise RuntimeError('Homepage body is empty')
    return dt.datetime.fromtimestamp(actual, CST).isoformat()


def save(path, data):
    temp = path.with_suffix('.tmp')
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
    os.replace(temp, path)


def run(api, state_dir, apply, wait_seconds):
    deadline = time.monotonic() + wait_seconds
    config = domain_config(api)
    while config['Status'] == 'processing' and time.monotonic() < deadline:
        time.sleep(min(20, max(0, deadline - time.monotonic())))
        config = domain_config(api)
    binding = config['Https']['CertInfo']
    now = time.time()
    expiry = epoch(binding['ExpireTime'])
    record = {'checked_at': dt.datetime.now(CST).isoformat(), 'domain': DOMAIN,
              'cdn_status': config['Status'], 'old_certificate': binding['CertId'],
              'old_expiry': binding['ExpireTime']}
    if config['Status'] != 'online':
        raise RuntimeError('CDN is ' + config['Status'] + '; this service does not start/stop CDN')
    if config['Https']['Switch'] != 'on':
        raise RuntimeError('HTTPS disabled; refusing to change unrelated configuration')
    candidate = candidates(api, expiry, now)
    if candidate:
        target = candidate['CertificateId']
        record.update(target_certificate=target, target_expiry=candidate['CertEndTime'])
        if not apply:
            record['result'] = 'would_deploy'
            return record
        # Only the certificate ID is changed. No private keys/PEMs enter backups.
        save(state_dir / ('before-' + str(int(now)) + '.json'), record)
        save(state_dir / 'status.json', dict(record, result='deployment_requested'))
        api.call('cdn', 'ModifyDomainConfig', {'Domain': DOMAIN, 'Route': 'Https.CertInfo.CertId', 'Value': json.dumps({'update': target})})
        expiry = epoch(candidate['CertEndTime'])
    else:
        target = binding['CertId']
    while True:
        try:
            live = domain_config(api)
            if live['Status'] != 'online' or live['Https']['CertInfo']['CertId'] != target:
                raise RuntimeError('CDN configuration is still propagating')
            record['served_expiry'] = verify(expiry)
            break
        except Exception:
            if time.monotonic() >= deadline:
                raise
            time.sleep(min(20, max(0, deadline - time.monotonic())))
    record['result'] = 'deployed_and_verified' if candidate else 'healthy_no_change'
    if not candidate and expiry - now <= 30 * 86400:
        raise RuntimeError('Certificate expires within 30 days and no newer deployable certificate exists')
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--credentials', default='/etc/qintopia-cdn-cert/credentials.json')
    parser.add_argument('--state-dir', default='/var/lib/qintopia-cdn-cert')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--wait-seconds', type=int, default=600)
    args = parser.parse_args()
    path = Path(args.state_dir)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (path / 'run.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Another certificate sync is running')
            return 0
        try:
            result = run(API(args.credentials), path, args.apply, args.wait_seconds)
            save(path / 'status.json', result)
            print(json.dumps(result, ensure_ascii=False))
            return 0
        except Exception as exc:
            result = {'checked_at': dt.datetime.now(CST).isoformat(), 'domain': DOMAIN,
                      'result': 'failed', 'error': str(exc)}
            save(path / 'status.json', result)
            print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
            return 1


if __name__ == '__main__':
    sys.exit(main())
