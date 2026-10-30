import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from contextlib import contextmanager

from scripts import briefing as b

NOW = datetime(2026, 10, 30, 23, 0, tzinfo=timezone.utc)
URL = 'https://example.com/news'
RSS = b'<rss><channel><item><title>Release</title><link>https://example.com/news?utm_source=rss</link><pubDate>Fri, 30 Oct 2026 12:00:00 GMT</pubDate><description>Public update</description></item></channel></rss>'
ATOM = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Release</title><link href="https://example.com/news"/><updated>2026-10-30T12:00:00Z</updated><summary>Update</summary></entry></feed>'


def item():
    return b.parse_feed(RSS, 'test')[0]


def summary():
    return {'items': [{'id': item()['id'], 'summary': '공개 업데이트가 발표되었습니다.', 'importance': '개발 흐름을 개선할 수 있습니다.', 'application': '별도 브랜치에서 타입 검사를 수행하세요.'}], 'experiment': '테스트 프로젝트에서 10분간 변경 사항을 비교하세요.'}


class CollectionTests(unittest.TestCase):
    def test_feed_formats_and_identity(self):
        self.assertEqual(b.parse_feed(RSS, 'test')[0]['url'], URL)
        self.assertEqual(b.parse_feed(ATOM, 'other')[0]['id'], item()['id'])

    def test_url_rejects_credentials_and_non_https(self):
        for url in ['http://example.com', 'https://user:secret@example.com', 'file:///etc/passwd']:
            with self.assertRaises(ValueError):
                b.canonical_url(url)

    def test_release_filters_drafts_and_prereleases(self):
        release = {'id': 123, 'html_url': 'https://github.com/openai/codex/releases/tag/v1', 'name': 'v1', 'published_at': '2026-10-30T12:00:00Z', 'body': 'Update', 'draft': False, 'prerelease': False}
        self.assertEqual(len(b.parse_releases(json.dumps([release]).encode(), 'codex')), 1)
        self.assertEqual(len(b.parse_releases(json.dumps(release).encode(), 'codex')), 1)
        release['prerelease'] = True
        self.assertEqual(b.parse_releases(json.dumps([release]).encode(), 'codex'), [])

    def test_collection_window_dedup_and_partial_failure(self):
        def fetch(url, **kwargs):
            if 'bad' in url:
                raise RuntimeError('private server details')
            return RSS
        config = [{'name': 'a', 'url': 'https://example.com/rss', 'kind': 'rss'}, {'name': 'b', 'url': 'https://example.com/bad', 'kind': 'rss'}]
        items, failed = b.collect(config, NOW, fetch)
        self.assertEqual(len(items), 1)
        self.assertEqual(failed, ['b'])
        self.assertEqual(b.collect(config[:1], datetime(2026, 11, 10, tzinfo=timezone.utc), fetch)[0], [])
        self.assertEqual(b.collect(config[:1], datetime(2026, 10, 29, tzinfo=timezone.utc), fetch)[0], [])
        with self.assertRaises(RuntimeError):
            b.collect(config[1:], NOW, fetch)

    def test_missing_dates_are_not_fresh_news(self):
        self.assertEqual(b.parse_feed(b'<rss><channel><item><title>x</title><link>https://example.com</link></item></channel></rss>', 'x'), [])

    def test_network_blocks_private_and_redirects(self):
        with patch('scripts.briefing.socket.getaddrinfo', return_value=[(2, 1, 6, '', ('127.0.0.1', 443))]):
            with self.assertRaises(ValueError):
                b.request_bytes('https://example.com/rss')
        with self.assertRaises(Exception):
            b.NoRedirect().redirect_request(None, None, 302, 'redirect', {}, 'https://127.0.0.1')

    def test_network_retry_limit_and_redacted_error(self):
        class BrokenOpener:
            calls = 0
            def open(self, request, timeout):
                self.calls += 1
                raise HTTPError(request.full_url, 429, 'secret-response', {}, None)
        opener = BrokenOpener()
        with patch.object(b.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('8.8.8.8', 443))]), patch.object(b, 'build_opener', return_value=opener), patch.object(b.time, 'sleep'):
            with self.assertRaises(RuntimeError) as error:
                b.request_bytes('https://example.com/rss')
        self.assertEqual(opener.calls, 3)
        self.assertNotIn('secret-response', str(error.exception))

    def test_network_auth_is_not_retried(self):
        class Unauthorized:
            calls = 0
            def open(self, request, timeout):
                self.calls += 1
                raise HTTPError(request.full_url, 401, 'secret', {}, None)
        opener = Unauthorized()
        with patch.object(b.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('8.8.8.8', 443))]), patch.object(b, 'build_opener', return_value=opener):
            with self.assertRaises(RuntimeError):
                b.request_bytes('https://example.com/rss')
        self.assertEqual(opener.calls, 1)

    def test_network_size_limit(self):
        class HugeResponse:
            def read(self, count):
                return b'x' * count
        class Opener:
            @contextmanager
            def open(self, request, timeout):
                yield HugeResponse()
        with patch.object(b.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('8.8.8.8', 443))]), patch.object(b, 'build_opener', return_value=Opener()):
            with self.assertRaises(ValueError):
                b.request_bytes('https://example.com/rss')


class GenerationTests(unittest.TestCase):
    def test_validation_rejects_untrusted_output(self):
        self.assertEqual(b.validate_summary(summary(), [item()])['items'][0]['id'], item()['id'])
        for mutate in [lambda s: s['items'][0].update(id='fake'), lambda s: s['items'].append(dict(s['items'][0])), lambda s: s.update(experiment='https://evil.example'), lambda s: s['items'][0].update(summary='English only'), lambda s: s.update(experiment='<script>악성</script>'), lambda s: s.update(experiment='![[비밀 노트]]')]:
            value = summary()
            mutate(value)
            with self.assertRaises(ValueError):
                b.validate_summary(value, [item()])

    def test_kst_and_rerun_skips_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            def generate(items):
                calls.append(1)
                return summary()
            result = b.run(Path(tmp), NOW, lambda: ([item()], []), generate)
            self.assertEqual(result.name, '2026-10-31.md')
            self.assertIn(URL, result.read_text())
            self.assertEqual(b.run(Path(tmp), NOW, lambda: self.fail('collection called'), generate), result)
            self.assertEqual(len(calls), 1)

    def test_cross_day_dedup_and_no_news(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            b.run(root, NOW, lambda: ([item()], []), lambda items: summary())
            result = b.run(root, datetime(2026, 11, 1, tzinfo=timezone.utc), lambda: ([item()], []), lambda items: self.fail('duplicate sent to Gemini'))
            self.assertIn('새로운 소식 없음', result.read_text())

    def test_failures_never_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                b.run(root, NOW, lambda: ([item()], []), lambda items: {'items': []})
            self.assertEqual(list((root / '01-Daily').glob('*.md')), [])

    def test_gemini_finish_reason_and_secret_header(self):
        seen = []
        def fetch(url, **kwargs):
            seen.append((url, kwargs))
            return json.dumps({'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': json.dumps(summary())}]}}]}).encode()
        self.assertEqual(b.generate([item()], 'secret-key', 'gemini-2.5-flash-lite', fetch)['experiment'], summary()['experiment'])
        self.assertNotIn('secret-key', seen[0][0])
        self.assertEqual(seen[0][1]['headers']['x-goog-api-key'], 'secret-key')
        with self.assertRaises(ValueError):
            b.generate([item()], 'key', 'gemini-2.5-flash-lite', lambda *a, **k: b'{"candidates":[{"finishReason":"MAX_TOKENS"}]}')


if __name__ == '__main__':
    unittest.main()
