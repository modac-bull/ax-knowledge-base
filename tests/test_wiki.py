import json
import tempfile
import unittest
from pathlib import Path
from scripts import wiki


class WikiTests(unittest.TestCase):
    def test_user_url_idempotent_and_no_remote_fetch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = wiki.add_url(root, 'https://example.com/article')
            self.assertEqual(p, wiki.add_url(root, 'https://example.com/article'))
            self.assertEqual(len(wiki.pending(root)), 1)
            self.assertIn('https://example.com/article', p.read_text())
            with self.assertRaises(ValueError):
                wiki.add_url(root, 'https://user:secret@example.com')

    def test_mark_requires_evidence_then_content_change_is_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = wiki.add_url(root, 'https://example.com/article')
            (root / 'wiki/topics').mkdir(parents=True)
            out = root / 'wiki/topics/test.md'
            out.write_text('# 검토\n출처 없는 주장')
            for name in ('index.md', 'log.md'):
                (root / 'wiki' / name).write_text('# 기록')
            with self.assertRaises(ValueError):
                wiki.mark(root, [raw.relative_to(root).as_posix()], ['wiki/topics/test.md'])
            out.write_text('# 검토\n[근거](../../' + raw.relative_to(root).as_posix() + ')')
            wiki.mark(root, [raw.relative_to(root).as_posix()], ['wiki/topics/test.md'])
            self.assertEqual(wiki.pending(root), [])
            out.write_text('# 근거 링크가 삭제된 문서')
            self.assertTrue(wiki.check(root))
            out.write_text('# 검토\n[근거](../../' + raw.relative_to(root).as_posix() + ')')
            raw.write_text(raw.read_text() + '\n사용자 추가 메모')
            self.assertEqual(len(wiki.pending(root)), 1)

    def test_paths_and_missing_links_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'wiki').mkdir()
            (root / 'wiki/index.md').write_text('[없는 자료](../raw/missing.md)')
            self.assertTrue(wiki.check(root))
            with self.assertRaises(ValueError):
                wiki.inside(root, '../outside.md', 'raw')

    def test_readme_is_not_source_and_sources_are_not_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'raw/user').mkdir(parents=True)
            (root / 'raw/user/README.md').write_text('사용 안내')
            self.assertEqual(wiki.pending(root), [])

