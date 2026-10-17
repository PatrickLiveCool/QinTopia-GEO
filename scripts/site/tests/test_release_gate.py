import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_gate import pending_drafts


class ReleaseGateTests(unittest.TestCase):
    def test_draft_on_later_page_blocks_next_version(self):
        pages = [[{'tag_name': 'v1.0.0', 'draft': False}], [{'tag_name': 'v1.1.0', 'draft': True}]]
        self.assertEqual(pending_drafts(pages), ['v1.1.0'])

    def test_published_releases_and_empty_repo_do_not_block(self):
        self.assertEqual(pending_drafts([[]]), [])
        self.assertEqual(pending_drafts([[{'tag_name': 'v1.0.0', 'draft': False}]]), [])

    def test_malformed_api_data_fails_closed(self):
        with self.assertRaises(KeyError):
            pending_drafts([[{'tag_name': 'v1.0.0'}]])
