import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import package
import cloud
import github_release

REV = 'a' * 40


class MemoryCOS:
    def __init__(self):
        self.data = {'legacy.html': b'old page', 'images/old.png': b'old image'}
        self.writes = []
        self.fail = None

    def get(self, key):
        return self.data.get(key)

    def put(self, key, data, content_type, immutable=False):
        if key == self.fail:
            raise RuntimeError('upload failed')
        self.writes.append((key, immutable))
        self.data[key] = data


class FakeCDN:
    def __init__(self):
        self.refreshes = []

    def check(self):
        pass

    def refresh(self, keys):
        self.refreshes.append(keys)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'config').mkdir()
        self.spec = {'schema': 1, 'files': []}
        self.add('index.html', b'<link href="style.css"><img src="photo.png"><a href="mobile.html">mobile</a>', 'route')
        self.add('mobile.html', b'<a href="index.html">desktop</a>', 'route')
        self.add('style.css', b'body{background:url(photo.png)}', 'asset')
        self.add('photo.png', b'image bytes', 'asset')
        (self.root / '.env').write_text('secret=do-not-publish')
        self.out = self.root / 'bundle'

    def add(self, path, data, kind):
        (self.root / path).write_bytes(data)
        self.spec['files'].append({'source': path, 'target': path, 'kind': kind})
        self.save_spec()

    def save_spec(self):
        (self.root / 'config/site-manifest.json').write_bytes(package.encoded(self.spec))

    def build(self, version='v1.0.0', revision=REV):
        return package.build(self.root, self.out, version, revision)

    def deploy(self, cos=None, live=None, rollback=False):
        return cloud.deploy(self.out, cos or MemoryCOS(), FakeCDN(), rollback=rollback,
                            live=live or (lambda files: None), entry=lambda: None)

    def test_reproducible_complete_versioned_bundle(self):
        self.build()
        _, files = package.verify(self.out)
        self.assertNotIn('.env', files)
        self.assertIn(f'/_site/v1.0.0-{REV}/photo.png'.encode(), files['index.html'])
        self.assertIn(f'/_site/v1.0.0-{REV}/photo.png'.encode(), files[f'_site/v1.0.0-{REV}/style.css'])
        other = self.root / 'second'
        package.build(self.root, other, 'v1.0.0', REV)
        for name in ('site.zip', 'manifest.json', 'SHA256SUMS'):
            self.assertEqual((self.out / name).read_bytes(), (other / name).read_bytes())

    def test_missing_link_blocks_build(self):
        (self.root / 'index.html').write_text('<a href="missing.html">missing</a>')
        with self.assertRaisesRegex(ValueError, 'missing.html'):
            self.build()

    def test_javascript_mobile_redirect_checked(self):
        (self.root / 'index.html').write_text('<script>location.href="missing-mobile.html";</script>')
        with self.assertRaisesRegex(ValueError, 'missing-mobile.html'):
            self.build()

    def test_srcset_not_silently_missed(self):
        (self.root / 'index.html').write_text('<img srcset="missing.png 1x, photo.png 2x">')
        with self.assertRaisesRegex(ValueError, 'missing.png'):
            self.build()

    def test_symlink_source_rejected(self):
        (self.root / 'photo.png').unlink()
        (self.root / 'photo.png').symlink_to('/etc/passwd')
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            self.build()

    def test_path_escape_and_duplicate_rejected(self):
        for value in ('../index.html', '/index.html', 'a/../index.html', '.env', 'ops/secret.pem'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                package.safe_path(value)
        self.spec['files'].append(self.spec['files'][0])
        self.save_spec()
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.build()

    def test_artifact_corruption_and_identity_fail_closed(self):
        self.build()
        with self.assertRaisesRegex(ValueError, 'identity'):
            package.verify(self.out, 'v2.0.0', REV)
        with (self.out / 'site.zip').open('ab') as f:
            f.write(b'tampered')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            package.verify(self.out)

    def test_existing_output_never_overwritten(self):
        self.build()
        with self.assertRaisesRegex(ValueError, 'empty'):
            self.build()

    def test_assets_precede_routes_legacy_objects_survive(self):
        self.build()
        cos = MemoryCOS()
        self.deploy(cos)
        self.assertEqual(cos.data['legacy.html'], b'old page')
        self.assertEqual(cos.data['images/old.png'], b'old image')
        self.assertTrue(cos.writes[0][1])
        self.assertEqual(cos.writes[-1][0], package.MARKER)
        self.assertEqual(cos.writes[-2][0], 'index.html')
        self.assertTrue((self.out / 'verified-deployment.json').exists())

    def test_conflicting_immutable_asset_stops_before_routes(self):
        self.build()
        cos = MemoryCOS()
        cos.data[f'_site/v1.0.0-{REV}/photo.png'] = b'conflict'
        with self.assertRaisesRegex(RuntimeError, 'conflict'):
            self.deploy(cos)
        self.assertNotIn('index.html', cos.data)

    def test_upload_failure_never_marks_success(self):
        self.build()
        cos = MemoryCOS()
        cos.fail = 'mobile.html'
        with self.assertRaisesRegex(RuntimeError, 'upload failed'):
            self.deploy(cos)
        self.assertNotIn(package.MARKER, cos.data)
        self.assertFalse((self.out / 'verified-deployment.json').exists())

    def test_stale_edge_never_marks_success(self):
        self.build()
        cos = MemoryCOS()
        def fail(files):
            raise RuntimeError('stale edge')
        with self.assertRaisesRegex(RuntimeError, 'stale edge'):
            self.deploy(cos, fail)
        self.assertNotIn(package.MARKER, cos.data)
        self.assertFalse((self.out / 'verified-deployment.json').exists())

    def test_marker_verification_failure_has_no_receipt(self):
        self.build()
        def check(files):
            if package.MARKER in files:
                raise RuntimeError('marker stale')
        with self.assertRaisesRegex(RuntimeError, 'marker stale'):
            self.deploy(live=check)
        self.assertFalse((self.out / 'verified-deployment.json').exists())

    def test_removing_managed_routes_requires_migration(self):
        self.build()
        cos = MemoryCOS()
        cos.data[package.MARKER] = package.encoded({'routes': ['gone.html']})
        with self.assertRaisesRegex(ValueError, 'migration'):
            self.deploy(cos)
        self.assertFalse(cos.writes)

    def test_rollback_requires_exact_successful_receipt(self):
        self.build()
        (self.out / 'deployed.json').write_text('{"result":"verified"}')
        with self.assertRaisesRegex(ValueError, 'receipt'):
            self.deploy(rollback=True)
        self.deploy()
        (self.out / 'deployed.json').write_bytes((self.out / 'verified-deployment.json').read_bytes())
        self.deploy(rollback=True)

    def test_live_check_detects_wrong_bytes_even_when_http_200(self):
        with self.assertRaisesRegex(RuntimeError, 'index.html'):
            cloud.verify_live({'index.html': b'new'}, getter=lambda k: b'old', attempts=1)

    def test_probe_refreshes_only_probe_and_verifies_its_actual_bytes(self):
        cos, cdn = MemoryCOS(), FakeCDN()
        cos.data['index.html'] = b'production homepage'
        observed = []
        def live(files):
            observed.extend(files)
            for key, data in files.items():
                self.assertEqual(cos.get(key), data)
        cloud.probe(cos, cdn, live=live, entry=lambda: None)
        self.assertEqual(cos.data['index.html'], b'production homepage')
        self.assertEqual(observed, ['_site/connectivity-probe.txt'])
        self.assertEqual(cdn.refreshes, [observed])

    def test_probe_stale_edge_fails(self):
        def fail(files):
            cloud.verify_live(files, getter=lambda key: b'old probe', attempts=1)
        with self.assertRaisesRegex(RuntimeError, 'connectivity-probe'):
            cloud.probe(MemoryCOS(), FakeCDN(), live=fail, entry=lambda: None)

    @patch('github_release.release')
    def test_draft_release_cannot_deploy(self, release):
        release.return_value = {'draft': True}
        with self.assertRaisesRegex(ValueError, 'published'):
            github_release.prepare('v1.0.0', 'deploy', self.out)

    @patch('github_release.subprocess.run')
    @patch('github_release.run')
    @patch('github_release.release')
    def test_partial_remote_artifact_never_rebuilt(self, release, run, subprocess_run):
        release.return_value = {'draft': False, 'prerelease': False, 'tag_name': 'v1.0.0', 'assets': [{'name': 'site.zip'}]}
        run.side_effect = [REV, '1.0.0']
        with self.assertRaisesRegex(ValueError, 'Partial'):
            github_release.prepare('v1.0.0', 'deploy', self.out)


if __name__ == '__main__':
    unittest.main()
