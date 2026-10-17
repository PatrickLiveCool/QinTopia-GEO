#!/usr/bin/env python3
"""Explicit source allowlist -> deterministic, self-verifying static release."""
import argparse
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
import mimetypes
from pathlib import Path, PurePosixPath
import re
from urllib.parse import quote, unquote, urljoin, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HOSTS = {'www.qintopia.cn', 'qintopia.cn', 'qintopia.livecool.com.cn'}
VERSION = re.compile(r'v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\Z')
REVISION = re.compile(r'[0-9a-f]{40}\Z')
QUOTED = re.compile(r'''(["'])([^"'<>\r\n]*?)\1''')
CSS_URL = re.compile(r'''url\(\s*(["']?)(.*?)\1\s*\)''', re.S)
ALLOWED = {'.html', '.txt', '.xml', '.css', '.js', '.jpg', '.jpeg', '.png', '.svg', '.webp', '.gif', '.ico', '.woff', '.woff2'}
MARKER = '.well-known/qintopia-release.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def safe_path(value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '\\' in value or any(x in ('.', '..', '') or x.startswith('.') for x in value.split('/')):
        raise ValueError('Unsafe path: ' + value)
    if str(p) != value or p.suffix.lower() not in ALLOWED:
        raise ValueError('Disallowed file: ' + value)
    return value


def identity(version, revision):
    if not VERSION.fullmatch(version) or not REVISION.fullmatch(revision):
        raise ValueError('Expected vMAJOR.MINOR.PATCH and a full commit SHA')


def local_target(value, page):
    value = unescape(value.strip())
    if not value or value.startswith(('#', 'data:', 'mailto:', 'tel:', 'javascript:')):
        return None
    u = urlsplit(urljoin('https://www.qintopia.cn/' + page, value))
    if u.hostname not in HOSTS or u.scheme not in ('http', 'https'):
        return None
    return unquote(u.path).lstrip('/') or 'index.html'


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []

    def handle_starttag(self, tag, attrs):
        if tag == 'base':
            raise ValueError('base elements are not supported; use explicit public paths')
        for key, value in attrs:
            if value and key in ('src', 'href', 'poster'):
                self.values.append(value)
            if value and key == 'srcset':
                if 'data:' in value:
                    raise ValueError('data URLs in srcset need explicit parser support')
                self.values.extend(x.strip().split()[0] for x in value.split(',') if x.strip())


def references(text, suffix):
    values = []
    if suffix == '.html':
        p = References()
        p.feed(text)
        values.extend(p.values)
    if suffix in ('.html', '.css'):
        values.extend(m.group(2) for m in CSS_URL.finditer(text))
    if suffix in ('.html', '.js'):
        # Includes literal JS mobile redirects. A computed '-mobile.html' suffix
        # is not itself a URL; its full counterpart is checked separately.
        values.extend(m.group(2) for m in QUOTED.finditer(text)
                      if re.fullmatch(r'[^\s]+\.(?:html|png|jpg|svg|css|js)(?:[?#].*)?', m.group(2))
                      and m.group(2) != '-mobile.html')
    return values


def load_sources(root):
    spec = json.loads((root / 'config/site-manifest.json').read_text())
    if spec['schema'] != 1 or not spec['files']:
        raise ValueError('Unsupported or empty source manifest')
    result = {}
    for row in spec['files']:
        src, target = safe_path(row['source']), safe_path(row['target'])
        if row['kind'] not in ('route', 'asset') or target in result:
            raise ValueError('Duplicate target or invalid kind: ' + target)
        if target.startswith('_site/') or target == 'manifest.json':
            raise ValueError('Reserved path: ' + target)
        path = root / src
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError('Source missing or unsafe: ' + src)
        result[target] = (row, path.read_bytes())
    return result


def validate_references(files):
    errors = set()
    for path, data in files.items():
        suffix = PurePosixPath(path).suffix
        if suffix not in ('.html', '.css', '.js'):
            continue
        for value in references(data.decode(), suffix):
            target = local_target(value, path)
            if target is not None and target not in files:
                errors.add(f'{path}: missing {value} -> {target}')
    if errors:
        raise ValueError('\n'.join(sorted(errors)))


def rewrite(text, page, assets):
    def replace_value(value):
        target = local_target(value, page)
        if target not in assets:
            return value
        u = urlsplit(unescape(value))
        return '/' + quote(assets[target], safe='/') + ('?' + u.query if u.query else '') + ('#' + u.fragment if u.fragment else '')
    text = QUOTED.sub(lambda m: m.group(1) + replace_value(m.group(2)) + m.group(1), text)
    return CSS_URL.sub(lambda m: 'url(' + m.group(1) + replace_value(m.group(2)) + m.group(1) + ')', text)


def build(root, output, version, revision):
    identity(version, revision)
    sources = load_sources(root)
    validate_references({k: v[1] for k, v in sources.items()})
    prefix = f'_site/{version}-{revision}/'
    assets = {k: prefix + k for k, (r, _) in sources.items() if r['kind'] == 'asset'}
    files, records = {}, []
    for path, (row, data) in sorted(sources.items()):
        suffix = PurePosixPath(path).suffix
        if suffix in ('.html', '.css', '.js'):
            data = rewrite(data.decode(), path, assets).encode()
        key = assets.get(path, path)
        files[key] = data
        mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        if suffix in ('.html', '.css', '.js', '.txt', '.xml'):
            mime += '; charset=utf-8'
        records.append({'key': key, 'source': row['source'], 'kind': row['kind'], 'sha256': sha(data), 'size': len(data), 'content_type': mime})
    validate_references(files)
    manifest = {'schema': 1, 'version': version, 'revision': revision, 'files': records}
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('Output must be empty; never replace an existing artifact')
    with zipfile.ZipFile(output / 'site.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for key, data in sorted(files.items()):
            info = zipfile.ZipInfo(key, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    (output / 'manifest.json').write_bytes(encoded(manifest))
    sums = ''.join(f'{sha((output / name).read_bytes())}  {name}\n' for name in ('manifest.json', 'site.zip'))
    (output / 'SHA256SUMS').write_text(sums)
    verify(output, version, revision)
    return manifest


def verify(directory, version=None, revision=None):
    expected = ''.join(f'{sha((directory / name).read_bytes())}  {name}\n' for name in ('manifest.json', 'site.zip'))
    if (directory / 'SHA256SUMS').read_text() != expected:
        raise ValueError('Artifact checksum mismatch')
    manifest = json.loads((directory / 'manifest.json').read_text())
    identity(manifest['version'], manifest['revision'])
    if manifest['schema'] != 1 or (version and manifest['version'] != version) or (revision and manifest['revision'] != revision):
        raise ValueError('Artifact identity mismatch')
    records = manifest['files']
    prefix = f"_site/{manifest['version']}-{manifest['revision']}/"
    keys = [safe_path(r['key']) for r in records]
    if not keys or len(set(keys)) != len(keys) or 'index.html' not in keys or 'mobile.html' not in keys:
        raise ValueError('Empty, duplicate or incomplete artifact')
    for r in records:
        if r['kind'] not in ('asset', 'route') or (r['kind'] == 'asset') != r['key'].startswith(prefix):
            raise ValueError('Invalid asset namespace')
        if r['kind'] == 'route' and ('/' in r['key'] or PurePosixPath(r['key']).suffix not in ('.html', '.txt', '.xml')):
            raise ValueError('Unsupported public route')
    with zipfile.ZipFile(directory / 'site.zip') as archive:
        if len(archive.namelist()) != len(keys) or set(archive.namelist()) != set(keys):
            raise ValueError('Archive does not match manifest')
        files = {}
        for row in records:
            data = archive.read(row['key'])
            if sha(data) != row['sha256'] or len(data) != row['size']:
                raise ValueError('Content mismatch: ' + row['key'])
            files[row['key']] = data
    validate_references(files)
    return manifest, files


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('check', 'build', 'verify'))
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--output', type=Path, default=Path('dist/release'))
    p.add_argument('--version')
    p.add_argument('--revision')
    a = p.parse_args()
    if a.command == 'check':
        sources = load_sources(a.root)
        validate_references({k: v[1] for k, v in sources.items()})
        print(f'OK: {len(sources)} explicitly listed source files; local references resolve')
    elif a.command == 'build':
        if not a.version or not a.revision:
            p.error('build requires --version and --revision')
        m = build(a.root, a.output, a.version, a.revision)
        print(f"Built {m['version']} ({m['revision']}): {len(m['files'])} files")
    else:
        m, _ = verify(a.output, a.version, a.revision)
        print(f"Verified {m['version']} ({m['revision']})")


if __name__ == '__main__':
    main()
