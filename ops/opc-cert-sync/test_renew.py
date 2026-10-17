import copy
import json
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import renew

NOW = renew.epoch('2026-12-20 12:00:00')
OLD = {'CertificateId': 'old', 'Domain': renew.DOMAIN, 'Status': 1, 'Deployable': True,
       'CertBeginTime': '2026-10-17 13:00:00', 'CertEndTime': '2027-01-15 12:59:59'}
NEW = dict(OLD, CertificateId='new', CertBeginTime='2026-12-20 11:00:00',
           CertEndTime='2027-03-20 10:59:59')


class FakeAPI:
    def __init__(self, rows=None, apply_error=False, deploy_error=False):
        self.rows = copy.deepcopy([OLD] if rows is None else rows)
        self.binding = 'old'
        self.writes = []
        self.apply_error = apply_error
        self.deploy_error = deploy_error
        self.reads = 0
        self.processing_reads = 0

    def call(self, service, action, payload):
        if action == 'DescribeDomainsConfig':
            self.reads += 1
            cert = next(c for c in self.rows if c['CertificateId'] == self.binding)
            return {'Domains': [{'Domain': renew.DOMAIN, 'Cname': renew.EDGE,
                    'Status': 'processing' if self.reads <= self.processing_reads else 'online',
                    'HttpsBilling': {'Switch': 'off'}, 'Origin': {'BasePath': '/opc'},
                    'Https': {'Switch': 'on', 'CertInfo': {
                        'CertId': self.binding, 'ExpireTime': cert['CertEndTime']}}}]}
        if action == 'DescribeCertificates':
            return {'Certificates': self.rows, 'TotalCount': len(self.rows)}
        if action == 'DescribeCertificate':
            return next(copy.deepcopy(c) for c in self.rows if c['CertificateId'] == payload['CertificateId'])
        if action == 'ApplyCertificate':
            self.writes.append((action, payload))
            pending = {'CertificateId': 'pending', 'Domain': renew.DOMAIN, 'Status': 4}
            self.rows.append(pending)
            if self.apply_error:
                raise OSError('response lost after creating order')
            return {'CertificateId': 'pending'}
        if action == 'ModifyDomainConfig':
            self.writes.append((action, payload))
            if self.deploy_error:
                raise RuntimeError('Rejected binding write')
            self.binding = json.loads(payload['Value'])['update']
            return {'RequestId': 'fake'}
        raise AssertionError(action)


class RenewalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name)
        self.clock = patch('renew.time.time', return_value=NOW)
        self.clock.start()
        self.addCleanup(self.clock.stop)
        self.verify = patch('renew.verify', return_value={
            'served_expiry': 'verified', 'verification_mode': 'cdn_edge_tls_unpublished'}).start()
        self.addCleanup(patch.stopall)

    def run_service(self, api, apply=True):
        return renew.run(api, self.state, apply, 0)

    def test_not_due_does_not_issue_or_change_binding(self):
        with patch('renew.time.time', return_value=renew.epoch('2026-10-17 14:00:00')):
            api = FakeAPI()
            result = self.run_service(api)
        self.assertEqual(result['result'], 'healthy_no_change')
        self.assertEqual(result['renewal'], 'not_due')
        self.assertEqual(api.writes, [])

    def test_due_requests_free_dns_auto_renewal_once(self):
        api = FakeAPI()
        result = self.run_service(api)
        self.assertEqual(result['result'], 'renewal_pending')
        self.assertEqual(api.writes, [('ApplyCertificate', renew.renewal_payload('old'))])
        intent = json.loads((self.state / 'renewal.json').read_text())
        self.assertEqual(intent['certificate_id'], 'pending')
        self.assertEqual(self.run_service(api)['renewal'], 'pending')
        self.assertEqual(len(api.writes), 1)

    def test_dry_run_cannot_request_or_deploy(self):
        api = FakeAPI()
        self.assertEqual(self.run_service(api, False)['renewal'], 'would_request')
        self.assertFalse((self.state / 'renewal.json').exists())
        api.rows.append(NEW)
        self.assertEqual(self.run_service(api, False)['result'], 'would_deploy')
        self.assertEqual(api.writes, [])

    def test_complete_renewal_lifecycle_reuses_order_and_deploys_after_issuance(self):
        api = FakeAPI()
        self.assertEqual(self.run_service(api)['renewal'], 'requested')
        self.assertEqual(self.run_service(api)['renewal'], 'pending')
        api.rows[-1] = dict(NEW, CertificateId='pending')
        self.assertEqual(self.run_service(api)['result'], 'deployed_and_verified')
        self.assertEqual(api.binding, 'pending')
        self.assertEqual(self.run_service(api)['result'], 'healthy_no_change')
        self.assertEqual([action for action, _ in api.writes], ['ApplyCertificate', 'ModifyDomainConfig'])

    def test_lost_application_response_reconciles_pending_order(self):
        api = FakeAPI(apply_error=True)
        with self.assertRaises(OSError):
            self.run_service(api)
        self.assertEqual(json.loads((self.state / 'renewal.json').read_text())['phase'], 'requesting')
        self.assertEqual(self.run_service(api)['renewal'], 'pending')
        self.assertEqual(len(api.writes), 1)

    def test_unknown_application_without_visible_order_does_not_retry(self):
        renew.save(self.state / 'renewal.json', {
            'old_certificate': 'old', 'phase': 'requesting', 'requested_at': NOW})
        api = FakeAPI()
        with self.assertRaisesRegex(RuntimeError, 'outcome unknown'):
            self.run_service(api)
        self.assertEqual(api.writes, [])

    def test_rejected_or_stuck_order_fails_without_new_order(self):
        renew.save(self.state / 'renewal.json', {
            'old_certificate': 'old', 'certificate_id': 'pending',
            'phase': 'pending', 'requested_at': NOW - 3 * renew.DAY})
        pending = {'CertificateId': 'pending', 'Domain': renew.DOMAIN, 'Status': 4}
        api = FakeAPI([OLD, pending])
        with self.assertRaisesRegex(RuntimeError, '48 hours'):
            self.run_service(api)
        pending['Status'] = 2
        api.rows = [OLD, pending]
        with self.assertRaisesRegex(RuntimeError, 'rejected/cancelled'):
            self.run_service(api)
        self.assertEqual(api.writes, [])

    def test_existing_manual_pending_order_is_reused(self):
        api = FakeAPI([OLD, {'CertificateId': 'manual', 'Domain': renew.DOMAIN, 'Status': 0}])
        self.assertEqual(self.run_service(api)['renewal_certificate'], 'manual')
        self.assertEqual(api.writes, [])

    def test_newer_certificate_deploys_only_binding_then_is_idempotent(self):
        api = FakeAPI([OLD, NEW])
        result = self.run_service(api)
        self.assertEqual(result['result'], 'deployed_and_verified')
        self.assertEqual(result['certificate_id'], 'new')
        self.assertEqual(api.writes, [('ModifyDomainConfig', {
            'Domain': renew.DOMAIN, 'Route': 'Https.CertInfo.CertId', 'Value': '{"update": "new"}'})])
        self.assertEqual(self.run_service(api)['result'], 'healthy_no_change')
        self.assertEqual(len(api.writes), 1)

    def test_rejected_write_and_failed_edge_verification_never_mark_success(self):
        api = FakeAPI([OLD, NEW], deploy_error=True)
        with self.assertRaisesRegex(RuntimeError, 'Rejected'):
            self.run_service(api)
        self.assertEqual(api.binding, 'old')
        self.assertEqual(json.loads((self.state / 'status.json').read_text())['result'], 'deployment_requested')
        api.deploy_error = False
        self.verify.side_effect = RuntimeError('stale edge')
        with self.assertRaisesRegex(RuntimeError, 'stale edge'):
            self.run_service(api)
        self.assertNotIn('deployed_and_verified', (self.state / 'status.json').read_text())
        self.verify.side_effect = None
        self.assertEqual(self.run_service(api)['result'], 'healthy_no_change')

    def test_wait_for_configuration_before_writing(self):
        api = FakeAPI([OLD, NEW])
        api.processing_reads = 1
        with patch('renew.time.sleep'):
            result = renew.run(api, self.state, False, 5)
        self.assertEqual(result['result'], 'would_deploy')
        self.assertEqual(api.reads, 2)
        self.assertEqual(api.writes, [])

    def test_revoked_wrong_future_shorter_or_non_deployable_certificates_are_rejected(self):
        for change in [
            {'Status': 10}, {'Domain': 'www.qintopia.cn'},
            {'CertBeginTime': '2027-01-01 00:00:00'},
            {'CertEndTime': '2027-01-01 00:00:00'}, {'Deployable': False},
        ]:
            with self.subTest(change=change):
                api = FakeAPI([OLD, dict(NEW, **change)])
                self.assertIsNone(renew.candidate(api, api.rows, renew.epoch(OLD['CertEndTime']), NOW))

    def test_critical_expiry_is_not_healthy_even_with_pending_order(self):
        api = FakeAPI([OLD, {'CertificateId': 'pending', 'Domain': renew.DOMAIN, 'Status': 4}])
        with patch('renew.time.time', return_value=renew.epoch('2027-01-12 12:00:00')):
            with self.assertRaisesRegex(RuntimeError, 'within 7 days'):
                self.run_service(api)
        self.assertEqual(api.writes, [])

    def test_pagination_does_not_skip_later_certificate(self):
        class Paginated(FakeAPI):
            def call(self, service, action, payload):
                if action == 'DescribeCertificates':
                    return {'Certificates': [OLD] if payload['Offset'] == 0 else [NEW], 'TotalCount': 2}
                return super().call(service, action, payload)
        self.assertEqual([c['CertificateId'] for c in renew.certificates(Paginated())], ['old', 'new'])


class BoundaryTests(unittest.TestCase):
    def test_disallowed_cloud_writes_are_rejected_before_network(self):
        api = object.__new__(renew.API)
        with patch('renew.urllib.request.urlopen') as network:
            for service, action, payload in [
                ('cdn', 'ModifyDomainConfig', {'Domain': 'www.qintopia.cn', 'Route': 'Https.CertInfo.CertId', 'Value': '{"update":"x"}'}),
                ('cdn', 'ModifyDomainConfig', {'Domain': renew.DOMAIN, 'Route': 'Origin', 'Value': '{}'}),
                ('cdn', 'UpdateDomainConfig', {'Domain': renew.DOMAIN}),
                ('ssl', 'ApplyCertificate', dict(renew.renewal_payload(), DomainName='www.qintopia.cn')),
                ('ssl', 'ApplyCertificate', dict(renew.renewal_payload(), PackageType='paid')),
                ('ssl', 'ApplyCertificate', dict(renew.renewal_payload(), DvAuthMethod='FILE')),
                ('ssl', 'DeleteCertificate', {'CertificateId': 'old'}),
                ('dnspod', 'ModifyRecordStatus', {}),
            ]:
                with self.subTest(action=action, payload=payload):
                    with self.assertRaises(RuntimeError):
                        api.call(service, action, payload)
            network.assert_not_called()

    def test_unpublished_verification_checks_edge_tls_without_public_dns_or_http(self):
        context = MagicMock()
        context.wrap_socket.return_value.__enter__.return_value.getpeercert.return_value = {
            'notAfter': 'Jan 15 04:59:59 2027 GMT'}
        expected = ssl.cert_time_to_seconds('Jan 15 04:59:59 2027 GMT')
        with patch('renew.ssl.create_default_context', return_value=context), \
                patch('renew.socket.create_connection') as connect, \
                patch('renew.urllib.request.urlopen') as http:
            result = renew.verify({'HttpsBilling': {'Switch': 'off'}}, expected)
            self.assertEqual(result['verification_mode'], 'cdn_edge_tls_unpublished')
            connect.assert_called_once_with((renew.EDGE, 443), timeout=20)
            self.assertEqual(context.wrap_socket.call_args.kwargs['server_hostname'], renew.DOMAIN)
            http.assert_not_called()
            with self.assertRaisesRegex(RuntimeError, 'expected certificate expiry'):
                renew.verify({'HttpsBilling': {'Switch': 'off'}}, expected + renew.DAY)

    def test_published_verification_requires_homepage_response(self):
        context = MagicMock()
        context.wrap_socket.return_value.__enter__.return_value.getpeercert.return_value = {
            'notAfter': 'Jan 15 04:59:59 2027 GMT'}
        expected = ssl.cert_time_to_seconds('Jan 15 04:59:59 2027 GMT')
        response = MagicMock(status=200, url='https://'+renew.DOMAIN+'/')
        response.read.return_value = b'OPC'
        with patch('renew.ssl.create_default_context', return_value=context), \
                patch('renew.socket.create_connection') as connect, \
                patch('renew.urllib.request.urlopen') as http:
            http.return_value.__enter__.return_value = response
            self.assertEqual(renew.verify({'HttpsBilling': {'Switch': 'on'}}, expected)[
                'verification_mode'], 'public_tls_and_homepage')
            connect.assert_called_once_with((renew.DOMAIN, 443), timeout=20)
            response.url = 'https://www.qintopia.cn/'
            with self.assertRaisesRegex(RuntimeError, 'homepage response'):
                renew.verify({'HttpsBilling': {'Switch': 'on'}}, expected)


if __name__ == '__main__':
    unittest.main()
