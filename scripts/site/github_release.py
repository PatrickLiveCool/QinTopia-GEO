#!/usr/bin/env python3
"""Resolve published GitHub releases; reuse artifacts and verified receipts."""
import argparse
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

from package import ROOT, build, encoded, identity, sha, verify

ASSETS = {'site.zip', 'manifest.json', 'SHA256SUMS'}


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def release(tag):
    return json.loads(run('gh', 'api', f'repos/{os.environ["GITHUB_REPOSITORY"]}/releases/tags/{tag}'))


def prepare(tag, operation, output):
    if operation not in ('deploy', 'rollback'):
        raise ValueError('Unsupported operation')
    # Validate before passing the tag to git or constructing API URLs.
    identity(tag, '0' * 40)
    meta = release(tag)
    if meta['draft'] or meta['prerelease'] or meta['tag_name'] != tag:
        raise ValueError('Only published stable releases can deploy or roll back')
    revision = run('git', 'rev-parse', f'refs/tags/{tag}^{{commit}}')
    identity(tag, revision)
    subprocess.run(['git', 'merge-base', '--is-ancestor', revision, 'origin/main'], check=True)
    if run('git', 'show', f'{revision}:version.txt') != tag[1:]:
        raise ValueError('Tag and committed version.txt disagree')
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('Artifact download directory must be empty')
    names = [a['name'] for a in meta['assets']]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate release asset names')
    present = ASSETS.intersection(names)
    if present and present != ASSETS:
        raise ValueError('Partial release artifact: inspect interrupted upload; never rebuild over it')
    if present:
        for name in sorted(ASSETS):
            subprocess.run(['gh', 'release', 'download', tag, '--pattern', name, '--dir', str(output)], check=True)
        verify(output, tag, revision)
    elif operation == 'rollback':
        raise ValueError('Rollback artifact is missing')
    else:
        # Source is data from the immutable tag; execute only trusted main's tool.
        archive = subprocess.check_output(['git', 'archive', '--format=tar', revision])
        with tempfile.TemporaryDirectory() as tmp:
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                tar.extractall(tmp, filter='data')
            build(Path(tmp), output, tag, revision)
        subprocess.run(['gh', 'release', 'upload', tag, *(str(output / n) for n in sorted(ASSETS))], check=True)
        # Read back GitHub assets before granting cloud credentials in next step.
        with tempfile.TemporaryDirectory() as tmp:
            for name in sorted(ASSETS):
                subprocess.run(['gh', 'release', 'download', tag, '--pattern', name, '--dir', tmp], check=True)
                if (Path(tmp) / name).read_bytes() != (output / name).read_bytes():
                    raise ValueError('GitHub artifact read-back mismatch')
    if operation == 'rollback':
        if 'deployed.json' not in names:
            raise ValueError('This release has no verified successful deployment')
        subprocess.run(['gh', 'release', 'download', tag, '--pattern', 'deployed.json', '--dir', str(output)], check=True)
    print(f'Ready: {tag} {revision}; immutable bundle verified')


def record(tag, directory):
    manifest, _ = verify(directory, tag)
    receipt = json.loads((directory / 'verified-deployment.json').read_text())
    expected = {'version': tag, 'revision': manifest['revision'],
                'manifest_sha256': sha((directory / 'manifest.json').read_bytes()), 'result': 'verified'}
    if any(receipt.get(k) != v for k, v in expected.items()):
        raise ValueError('Invalid verified receipt')
    meta = release(tag)
    if 'deployed.json' in [a['name'] for a in meta['assets']]:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(['gh', 'release', 'download', tag, '--pattern', 'deployed.json', '--dir', tmp], check=True)
            old = json.loads((Path(tmp) / 'deployed.json').read_text())
            if any(old.get(k) != v for k, v in expected.items()):
                raise ValueError('Existing successful receipt conflicts with this artifact')
    else:
        (directory / 'deployed.json').write_bytes(encoded(receipt))
        subprocess.run(['gh', 'release', 'upload', tag, str(directory / 'deployed.json')], check=True)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as f:
            f.write(f"Verified {tag} (`{manifest['revision']}`). COS read-back, CDN purge, HTTPS redirect, public bytes and version marker passed.\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('prepare', 'record'))
    p.add_argument('--tag', required=True)
    p.add_argument('--operation', choices=('deploy', 'rollback'), default='deploy')
    p.add_argument('--directory', type=Path, default=ROOT / 'dist/release')
    args = p.parse_args()
    if args.command == 'prepare':
        prepare(args.tag, args.operation, args.directory)
    else:
        record(args.tag, args.directory)


if __name__ == '__main__':
    main()
