import unittest
from datetime import datetime, timezone
from scripts import briefing as b

HTML = b'''<time datetime="2099-01-01T00:00:00Z">page updated</time>
<article data-news-card><time datetime="2026-10-30T06:00:00Z">today</time>
<h2><a href="/news/new-agent/">New &amp; better agent</a></h2>
<p>A short description.</p></article>'''


class HermesTests(unittest.TestCase):
    def test_extracts_article_metadata_not_page_update(self):
        item = b.parse_hermes(HTML, 'Hermes')[0]
        self.assertEqual(item['title'], 'New & better agent')
        self.assertEqual(item['url'], 'https://hermes-ai.net/news/new-agent/')
        self.assertEqual(item['published'], '2026-10-30T06:00:00+00:00')
        self.assertEqual(item['description'], 'A short description.')

    def test_layout_change_or_external_links_fail(self):
        for payload in [b'<html>changed layout</html>', HTML.replace(b'/news/new-agent/', b'https://evil.example/news/x/')]:
            with self.assertRaises(ValueError):
                b.parse_hermes(payload, 'Hermes')

    def test_source_integrates_with_existing_collection(self):
        sources = [{'name': 'Hermes', 'kind': 'hermes_news', 'url': 'https://hermes-ai.net/news/'}]
        items, failed = b.collect(sources, datetime(2026, 10, 30, 7, tzinfo=timezone.utc), lambda *a, **k: HTML)
        self.assertEqual(len(items), 1)
        self.assertEqual(failed, [])
