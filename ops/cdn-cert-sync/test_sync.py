import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sync

class FakeAPI:
    def __init__(self, update_error=False):
        self.writes = []
        self.update_error = update_error
        self.id = 'old'
    def call(self, service, action, payload):
        if action == 'DescribeDomainsConfig':
            return {'Domains': [{'Domain': sync.DOMAIN, 'Status': 'online', 'Https': {'Switch': 'on', 'CertInfo': {'CertId': self.id, 'ExpireTime': '2026-09-28 07:00:00' if self.id == 'old' else '2026-11-27 07:00:00'}}}]}
        cert = {'CertificateId': 'new', 'Domain': sync.APEX, 'SubjectAltName': [sync.DOMAIN], 'Status': 1, 'Deployable': True, 'CertBeginTime': '2026-08-29 07:00:00', 'CertEndTime': '2026-11-27 07:00:00'}
        if action == 'DescribeCertificates': return {'Certificates': [cert], 'TotalCount': 1}
        if action == 'DescribeCertificate': return cert
        if action == 'ModifyDomainConfig':
            self.writes.append(payload)
            if self.update_error: raise RuntimeError('Rejected')
            self.id = 'new'
            return {'RequestId': 'test'}
        raise AssertionError(action)

class Tests(unittest.TestCase):
    def test_hostname_boundary(self):
        self.assertTrue(sync.covers('*.qintopia.cn'))
        self.assertFalse(sync.covers('*.cn'))
        self.assertFalse(sync.covers('qintopia.cn'))
        self.assertFalse(sync.covers('*.qintopia.cn', 'a.www.qintopia.cn'))
    def test_reject_wrong_revoked_future_and_shorter(self):
        cert = {'Status': 1, 'Domain': sync.DOMAIN, 'CertBeginTime': '2026-08-29 07:00:00', 'CertEndTime': '2026-11-27 07:00:00'}
        now = sync.epoch('2026-10-11 00:00:00')
        self.assertTrue(sync.eligible(cert, now, now))
        for change in [{'Status':10}, {'Domain':'other.cn'}, {'CertBeginTime':'2027-01-01 00:00:00'}, {'CertEndTime':'2026-09-01 00:00:00'}]:
            self.assertFalse(sync.eligible(dict(cert, **change), now, now))
    @patch('sync.verify', return_value='2026-11-27')
    @patch('sync.time.time', return_value=1791648000)
    def test_minimal_write_and_idempotence(self, *_):
        api = FakeAPI()
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(sync.run(api, Path(d), False, 0)['result'], 'would_deploy')
            self.assertFalse(api.writes)
            self.assertEqual(sync.run(api, Path(d), True, 0)['result'], 'deployed_and_verified')
            self.assertEqual(sync.run(api, Path(d), True, 0)['result'], 'healthy_no_change')
            self.assertEqual(len(api.writes), 1)
            self.assertEqual(api.writes[0], {'Domain':sync.DOMAIN,'Route':'Https.CertInfo.CertId','Value':'{"update": "new"}'})
    @patch('sync.time.sleep')
    @patch('sync.time.time', return_value=1791648000)
    def test_waits_for_processing_before_considering_write(self, *_):
        class ProcessingAPI(FakeAPI):
            reads = 0
            def call(self, service, action, payload):
                result = super().call(service, action, payload)
                if action == 'DescribeDomainsConfig':
                    self.reads += 1
                    if self.reads == 1: result['Domains'][0]['Status'] = 'processing'
                return result
        api = ProcessingAPI()
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(sync.run(api, Path(d), False, 5)['result'], 'would_deploy')
            self.assertEqual(api.reads, 2)
            self.assertFalse(api.writes)

    @patch('sync.time.time', return_value=1791648000)
    def test_failure_never_marked_success(self, *_):
        api = FakeAPI(update_error=True)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(RuntimeError, 'Rejected'):
                sync.run(api, Path(d), True, 0)
            self.assertEqual(api.id, 'old')
            self.assertNotIn('deployed_and_verified', (Path(d)/'status.json').read_text())

if __name__ == '__main__': unittest.main()
