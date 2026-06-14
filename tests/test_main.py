from datetime import date
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import main


class FakeCache:
    def __init__(self, value=None):
        self.value = value
        self.set_calls = []

    def get(self, key):
        return self.value

    def set(self, key, value):
        self.set_calls.append((key, value))
        self.value = value


class FakeResponse:
    def __init__(self, body=b'<div class="action"><span>Expected</span></div>'):
        self.body = body
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        return self.body if size < 0 else self.body[:size]


class FakeBrowser:
    def __init__(self):
        self.opens = []
        self.form = {}
        self.response = FakeResponse()

    def set_handle_robots(self, value):
        self.robots = value

    def open(self, target, timeout):
        self.opens.append((target, timeout))
        return self.response

    def select_form(self, nr):
        self.form_number = nr

    def click(self):
        return "submitted-request"


class MainTests(unittest.TestCase):
    def test_create_cache_treats_single_server_string_as_one_endpoint(self):
        memcache = SimpleNamespace(Client=lambda servers, debug: (servers, debug))
        settings = SimpleNamespace(memcache_servers=" cache.example:11211 ")

        with patch("main.importlib.import_module", return_value=memcache):
            client = main.create_cache({}, settings)

        self.assertEqual(client, (["cache.example:11211"], 0))

    def test_create_cache_normalizes_server_sequence(self):
        memcache = SimpleNamespace(Client=lambda servers, debug: (servers, debug))
        settings = SimpleNamespace(memcache_servers=[" cache-a:11211 ", "cache-b:11211"])

        with patch("main.importlib.import_module", return_value=memcache):
            client = main.create_cache({}, settings)

        self.assertEqual(client, (["cache-a:11211", "cache-b:11211"], 0))

    def test_create_cache_uses_nonblank_environment_override(self):
        memcache = SimpleNamespace(Client=lambda servers, debug: (servers, debug))
        settings = SimpleNamespace(memcache_servers=["configured:11211"])

        with patch("main.importlib.import_module", return_value=memcache):
            client = main.create_cache({"MEMCACHE_SERVER": " override:11211 "}, settings)

        self.assertEqual(client, (["override:11211"], 0))

    def test_create_cache_ignores_blank_environment_override(self):
        memcache = SimpleNamespace(Client=lambda servers, debug: (servers, debug))
        settings = SimpleNamespace(memcache_servers=["configured:11211"])

        with patch("main.importlib.import_module", return_value=memcache):
            client = main.create_cache({"MEMCACHE_SERVER": "  "}, settings)

        self.assertEqual(client, (["configured:11211"], 0))

    def test_create_cache_rejects_blank_or_unsupported_server_settings(self):
        invalid_values = ([], ["cache:11211", " "], {"cache": "11211"}, b"cache:11211")

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "memcache_servers"):
                    main.create_cache({}, SimpleNamespace(memcache_servers=value))

    def test_fetch_actions_bounds_every_network_open(self):
        browser = FakeBrowser()
        settings = main.ScrapeSettings(
            name="sample",
            recipient="to@example.com",
            site="https://example.com",
            form_url="https://example.com/results",
            form={"q": "value"},
            fake_user_agent="agent",
            fake_referer="referer",
        )

        actions = main.fetch_actions(settings, browser_factory=lambda: browser)

        self.assertEqual(actions, ["Expected"])
        self.assertEqual(browser.opens, [
            ("https://example.com", main.SCRAPE_REQUEST_TIMEOUT),
            ("submitted-request", main.SCRAPE_REQUEST_TIMEOUT),
            ("https://example.com/results", main.SCRAPE_REQUEST_TIMEOUT),
        ])
        self.assertEqual(browser.form, {"q": "value"})
        self.assertEqual(browser.form_number, 0)
        self.assertTrue(browser.robots)
        self.assertEqual(browser.addheaders, [
            ("User-agent", "agent"),
            ("Referer", "referer"),
        ])
        self.assertEqual(browser.response.read_sizes, [main.MAX_SCRAPE_RESPONSE_BYTES + 1])

    def test_fetch_actions_uses_bounded_submission_response_without_result_url(self):
        browser = FakeBrowser()
        settings = main.ScrapeSettings(
            name="sample",
            recipient="to@example.com",
            site="https://example.com",
            form_url="",
            form={},
            fake_user_agent="agent",
            fake_referer="referer",
        )

        self.assertEqual(
            main.fetch_actions(settings, browser_factory=lambda: browser),
            ["Expected"],
        )
        self.assertEqual(browser.opens, [
            ("https://example.com", main.SCRAPE_REQUEST_TIMEOUT),
            ("submitted-request", main.SCRAPE_REQUEST_TIMEOUT),
        ])

    def test_read_bounded_response_accepts_exact_limit(self):
        response = FakeResponse(b"x" * main.MAX_SCRAPE_RESPONSE_BYTES)

        self.assertEqual(len(main._read_bounded_response(response)), main.MAX_SCRAPE_RESPONSE_BYTES)
        self.assertEqual(response.read_sizes, [main.MAX_SCRAPE_RESPONSE_BYTES + 1])

    def test_read_bounded_response_rejects_one_byte_over_limit(self):
        response = FakeResponse(b"x" * (main.MAX_SCRAPE_RESPONSE_BYTES + 1))

        with self.assertRaisesRegex(ValueError, "configured size limit"):
            main._read_bounded_response(response)

        self.assertEqual(response.read_sizes, [main.MAX_SCRAPE_RESPONSE_BYTES + 1])

    def test_extract_actions_reads_first_span_from_each_action(self):
        html = """
        <div class="action"><span>First</span><span>Ignored</span></div>
        <div class="other"><span>Skipped</span></div>
        <div class="action"><span>Second</span></div>
        """

        self.assertEqual(main.extract_actions(html), ["First", "Second"])

    def test_extract_actions_keeps_action_open_across_nested_div(self):
        html = """
        <div class="action">
          <div class="metadata">Metadata</div>
          <span>Expected</span>
        </div>
        """

        self.assertEqual(main.extract_actions(html), ["Expected"])

    def test_extract_actions_collects_nested_markup_inside_first_span(self):
        html = """
        <div class="action">
          <span>Expected <strong>nested</strong> value</span>
          <span>Ignored</span>
        </div>
        """

        self.assertEqual(main.extract_actions(html), ["Expected nested value"])

    def test_notify_if_changed_skips_duplicate_cache_value(self):
        sent = []
        cache = FakeCache(["First"])

        changed = main.notify_if_changed(
            ["First"],
            cache,
            "sample",
            "to@example.com",
            lambda to, subject, body: sent.append((to, subject, body)),
        )

        self.assertFalse(changed)
        self.assertEqual(sent, [])
        self.assertEqual(cache.set_calls, [])

    def test_notify_if_changed_sends_then_updates_cache(self):
        sent = []
        cache = FakeCache(["Old"])

        changed = main.notify_if_changed(
            ["New"],
            cache,
            "sample",
            "to@example.com",
            lambda to, subject, body: sent.append((to, subject, body)),
            today=lambda: date(2026, 6, 8),
        )

        self.assertTrue(changed)
        self.assertEqual(cache.set_calls, [("sample", ["New"])])
        self.assertEqual(sent[0][0], ["to@example.com"])
        self.assertEqual(sent[0][1], "Mechenz | 2026-06-08 | sample")
        self.assertIn("New", sent[0][2])

    def test_load_scrape_settings_respects_robots_by_default(self):
        module = SimpleNamespace(
            name="sample",
            to="to@example.com",
            site="https://example.com",
            form_url="https://example.com/results",
            form={"q": "value"},
            fake_user_agent="Mechenz",
            fake_referer="https://example.com",
        )

        settings = main.load_scrape_settings(module)

        self.assertTrue(settings.respect_robots)
        self.assertEqual(settings.form, {"q": "value"})

    def test_load_scrape_settings_rejects_blank_required_values(self):
        module = SimpleNamespace(
            name=" ",
            to="",
            site="https://example.com",
            form_url="",
            form={"q": "value"},
            fake_user_agent="Mechenz",
            fake_referer=" ",
        )

        with self.assertRaisesRegex(ValueError, "empty required settings: name, to, fake_referer"):
            main.load_scrape_settings(module)

    def test_load_scrape_settings_rejects_invalid_scrape_urls(self):
        module = SimpleNamespace(
            name="sample",
            to="to@example.com",
            site="file:///tmp/private.html",
            form_url="not-a-url",
            form={"q": "value"},
            fake_user_agent="Mechenz",
            fake_referer="https://example.com",
        )

        with self.assertRaisesRegex(ValueError, "invalid scrape settings: site, form_url"):
            main.load_scrape_settings(module)

        try:
            main.load_scrape_settings(module)
        except ValueError as error:
            self.assertNotIn("file:///tmp/private.html", str(error))
            self.assertNotIn("not-a-url", str(error))

    def test_load_scrape_settings_can_explicitly_ignore_robots(self):
        module = SimpleNamespace(
            name="sample",
            to="to@example.com",
            site="https://example.com",
            form_url="https://example.com/results",
            form={"q": "value"},
            fake_user_agent="Mechenz",
            fake_referer="https://example.com",
        )

        settings = main.load_scrape_settings(module, {"MECHENZ_IGNORE_ROBOTS": "1"})

        self.assertFalse(settings.respect_robots)

    def test_load_scrape_settings_accepts_valid_encoding(self):
        module = SimpleNamespace(
            name="sample",
            to="to@example.com",
            site="https://example.com",
            form_url="https://example.com/results",
            form={"q": "value"},
            fake_user_agent="Mechenz",
            fake_referer="https://example.com",
            encoding=" latin-1 ",
        )

        settings = main.load_scrape_settings(module)

        self.assertEqual(settings.encoding, "latin-1")

    def test_load_scrape_settings_rejects_invalid_encoding(self):
        module = SimpleNamespace(
            name="sample",
            to="to@example.com",
            site="https://example.com",
            form_url="https://example.com/results",
            form={"q": "value"},
            fake_user_agent="Mechenz",
            fake_referer="https://example.com",
            encoding="not-a-codec",
        )

        with self.assertRaisesRegex(ValueError, "invalid encoding"):
            main.load_scrape_settings(module)

        try:
            main.load_scrape_settings(module)
        except ValueError as error:
            self.assertNotIn("not-a-codec", str(error))

    def test_load_scrape_settings_rejects_ambiguous_respect_robots_value(self):
        module = SimpleNamespace(
            name="sample",
            to="to@example.com",
            site="https://example.com",
            form_url="https://example.com/results",
            form={"q": "value"},
            fake_user_agent="Mechenz",
            fake_referer="https://example.com",
            respect_robots="treu",
        )

        with self.assertRaisesRegex(ValueError, "invalid respect_robots"):
            main.load_scrape_settings(module)

        try:
            main.load_scrape_settings(module)
        except ValueError as error:
            self.assertNotIn("treu", str(error))

    def test_load_scrape_settings_rejects_ambiguous_ignore_robots_value(self):
        module = SimpleNamespace(
            name="sample",
            to="to@example.com",
            site="https://example.com",
            form_url="https://example.com/results",
            form={"q": "value"},
            fake_user_agent="Mechenz",
            fake_referer="https://example.com",
        )

        with self.assertRaisesRegex(ValueError, "invalid MECHENZ_IGNORE_ROBOTS"):
            main.load_scrape_settings(module, {"MECHENZ_IGNORE_ROBOTS": "treu"})

        try:
            main.load_scrape_settings(module, {"MECHENZ_IGNORE_ROBOTS": "treu"})
        except ValueError as error:
            self.assertNotIn("treu", str(error))


if __name__ == "__main__":
    unittest.main()
