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
    def __init__(
        self,
        body=b'<div class="action"><span>Expected</span></div>',
        max_chunk_size=None,
        read_error=None,
        url="https://example.com",
        close_error=None,
    ):
        self.body = body
        self.max_chunk_size = max_chunk_size
        self.read_error = read_error
        self.url = url
        self.close_error = close_error
        self.offset = 0
        self.read_sizes = []
        self.close_calls = 0

    def read(self, size=-1):
        self.read_sizes.append(size)
        if self.read_error is not None:
            raise self.read_error
        if size < 0:
            size = len(self.body) - self.offset
        if self.max_chunk_size is not None:
            size = min(size, self.max_chunk_size)
        start = self.offset
        end = min(start + size, len(self.body))
        self.offset = end
        return self.body[start:end]

    def close(self):
        self.close_calls += 1
        if self.close_error is not None:
            raise self.close_error

    def geturl(self):
        return self.url


class FakeRequest:
    def __init__(self, url):
        self.url = url

    def get_full_url(self):
        return self.url

    def __eq__(self, other):
        return isinstance(other, FakeRequest) and self.url == other.url


class FakeBrowser:
    def __init__(self):
        self.opens = []
        self.form = {}
        self.landing_response = FakeResponse(b"")
        self.submission_response = FakeResponse()
        self.response = FakeResponse()
        self.responses = [
            self.landing_response,
            self.submission_response,
            self.response,
        ]

    def set_handle_robots(self, value):
        self.robots = value

    def open(self, target, timeout):
        self.opens.append((target, timeout))
        return self.responses[len(self.opens) - 1]

    def select_form(self, nr):
        self.form_number = nr

    def click(self):
        return FakeRequest("https://example.com/submitted")


class MainTests(unittest.TestCase):
    def test_create_cache_treats_single_server_string_as_one_endpoint(self):
        memcache = SimpleNamespace(
            Client=lambda servers, debug, socket_timeout: (servers, debug, socket_timeout)
        )
        settings = SimpleNamespace(memcache_servers=" cache.example:11211 ")

        with patch("main.importlib.import_module", return_value=memcache):
            client = main.create_cache({}, settings)

        self.assertEqual(client, (["cache.example:11211"], 0, 5.0))

    def test_create_cache_normalizes_server_sequence(self):
        memcache = SimpleNamespace(
            Client=lambda servers, debug, socket_timeout: (servers, debug, socket_timeout)
        )
        settings = SimpleNamespace(memcache_servers=[" cache-a:11211 ", "cache-b:11211"])

        with patch("main.importlib.import_module", return_value=memcache):
            client = main.create_cache({}, settings)

        self.assertEqual(client, (["cache-a:11211", "cache-b:11211"], 0, 5.0))

    def test_create_cache_normalizes_unix_and_ipv6_endpoints(self):
        memcache = SimpleNamespace(
            Client=lambda servers, debug, socket_timeout: (servers, debug, socket_timeout)
        )
        settings = SimpleNamespace(
            memcache_servers=[" /tmp/mechenz.sock ", " inet6:[::1]:11211 "],
        )

        with patch("main.importlib.import_module", return_value=memcache):
            client = main.create_cache({}, settings)

        self.assertEqual(
            client,
            (["unix:/tmp/mechenz.sock", "inet6:[::1]:11211"], 0, 5.0),
        )

    def test_create_cache_uses_nonblank_environment_override(self):
        memcache = SimpleNamespace(
            Client=lambda servers, debug, socket_timeout: (servers, debug, socket_timeout)
        )
        settings = SimpleNamespace(memcache_servers=["configured:11211"])

        with patch("main.importlib.import_module", return_value=memcache):
            client = main.create_cache({"MEMCACHE_SERVER": " override:11211 "}, settings)

        self.assertEqual(client, (["override:11211"], 0, 5.0))

    def test_create_cache_ignores_blank_environment_override(self):
        memcache = SimpleNamespace(
            Client=lambda servers, debug, socket_timeout: (servers, debug, socket_timeout)
        )
        settings = SimpleNamespace(memcache_servers=["configured:11211"])

        with patch("main.importlib.import_module", return_value=memcache):
            client = main.create_cache({"MEMCACHE_SERVER": "  "}, settings)

        self.assertEqual(client, (["configured:11211"], 0, 5.0))

    def test_create_cache_rejects_blank_or_unsupported_server_settings(self):
        invalid_values = ([], ["cache:11211", " "], {"cache": "11211"}, b"cache:11211")

        for value in invalid_values:
            with self.subTest(value=value):
                with patch("main.importlib.import_module") as import_module:
                    with self.assertRaisesRegex(ValueError, "memcache_servers"):
                        main.create_cache({}, SimpleNamespace(memcache_servers=value))
                import_module.assert_not_called()

    def test_create_cache_rejects_malformed_server_endpoints(self):
        invalid_values = (
            "https://cache.example:11211",
            "cache.example",
            "cache.example:0",
            "cache.example:65536",
            "cache.example:11211\r\nother:11211",
        )

        for value in invalid_values:
            with self.subTest(value=value):
                with patch("main.importlib.import_module") as import_module:
                    with self.assertRaisesRegex(ValueError, "memcache_servers"):
                        main.create_cache({}, SimpleNamespace(memcache_servers=value))
                import_module.assert_not_called()

    def test_create_cache_uses_settings_timeout_and_environment_override(self):
        memcache = SimpleNamespace(
            Client=lambda servers, debug, socket_timeout: (servers, debug, socket_timeout)
        )
        settings = SimpleNamespace(
            memcache_servers=["cache:11211"],
            memcache_timeout="12.5",
        )

        with patch("main.importlib.import_module", return_value=memcache):
            settings_client = main.create_cache({}, settings)
            environment_client = main.create_cache({"MEMCACHE_TIMEOUT": "2"}, settings)
            blank_environment_client = main.create_cache({"MEMCACHE_TIMEOUT": "  "}, settings)
            default_client = main.create_cache(
                {},
                SimpleNamespace(memcache_servers=["cache:11211"], memcache_timeout="  "),
            )

        self.assertEqual(settings_client, (["cache:11211"], 0, 12.5))
        self.assertEqual(environment_client, (["cache:11211"], 0, 2.0))
        self.assertEqual(blank_environment_client, (["cache:11211"], 0, 12.5))
        self.assertEqual(default_client, (["cache:11211"], 0, 5.0))

    def test_create_cache_rejects_invalid_timeout_before_client_import(self):
        invalid_values = ("0", "-1", "nan", "inf", "301", "not-a-number")

        for value in invalid_values:
            with self.subTest(value=value):
                with patch("main.importlib.import_module") as import_module:
                    with self.assertRaisesRegex(ValueError, "invalid MEMCACHE_TIMEOUT") as error:
                        main.create_cache(
                            {"MEMCACHE_TIMEOUT": value},
                            SimpleNamespace(memcache_servers=["cache:11211"]),
                        )

                import_module.assert_not_called()
                self.assertNotIn(value, str(error.exception))

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
            (browser.click(), main.SCRAPE_REQUEST_TIMEOUT),
            ("https://example.com/results", main.SCRAPE_REQUEST_TIMEOUT),
        ])
        self.assertEqual(browser.form, {"q": "value"})
        self.assertEqual(browser.form_number, 0)
        self.assertTrue(browser.robots)
        self.assertEqual(browser.addheaders, [
            ("User-agent", "agent"),
            ("Referer", "referer"),
        ])
        self.assertEqual(
            browser.response.read_sizes,
            [
                main.MAX_SCRAPE_RESPONSE_BYTES + 1,
                main.MAX_SCRAPE_RESPONSE_BYTES + 1 - len(browser.response.body),
            ],
        )
        self.assertEqual(browser.landing_response.close_calls, 1)
        self.assertEqual(browser.submission_response.close_calls, 1)
        self.assertEqual(browser.response.close_calls, 1)

    def test_fetch_actions_applies_literal_fifteen_second_timeout(self):
        browser = FakeBrowser()
        settings = self.scrape_settings()

        main.fetch_actions(settings, browser_factory=lambda: browser)

        self.assertEqual([timeout for _, timeout in browser.opens], [15, 15, 15])

    def test_fetch_actions_closes_landing_response_when_form_selection_fails(self):
        browser = FakeBrowser()

        def fail_selection(nr):
            raise ValueError("form selection failed")

        browser.select_form = fail_selection
        settings = main.ScrapeSettings(
            name="sample",
            recipient="to@example.com",
            site="https://example.com",
            form_url="",
            form={},
            fake_user_agent="agent",
            fake_referer="referer",
        )

        with self.assertRaisesRegex(ValueError, "form selection failed"):
            main.fetch_actions(settings, browser_factory=lambda: browser)

        self.assertEqual(browser.landing_response.close_calls, 1)
        self.assertEqual(len(browser.opens), 1)

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
            (browser.click(), main.SCRAPE_REQUEST_TIMEOUT),
        ])
        self.assertEqual(browser.submission_response.close_calls, 1)

    def test_fetch_actions_rejects_cross_origin_form_action_before_open(self):
        browser = FakeBrowser()
        browser.click = lambda: FakeRequest("http://127.0.0.1/admin")
        settings = self.scrape_settings()

        with self.assertRaisesRegex(ValueError, "unsafe scrape navigation"):
            main.fetch_actions(settings, browser_factory=lambda: browser)

        self.assertEqual(browser.opens, [("https://example.com", main.SCRAPE_REQUEST_TIMEOUT)])
        self.assertEqual(browser.landing_response.close_calls, 1)

    def test_fetch_actions_rejects_cross_origin_redirect_and_closes_response(self):
        browser = FakeBrowser()
        browser.landing_response.url = "http://127.0.0.1/admin"
        settings = self.scrape_settings()

        with self.assertRaisesRegex(ValueError, "unsafe scrape navigation"):
            main.fetch_actions(settings, browser_factory=lambda: browser)

        self.assertEqual(browser.landing_response.close_calls, 1)

    def test_fetch_actions_rejects_cross_origin_submission_redirect(self):
        browser = FakeBrowser()
        browser.submission_response.url = "https://attacker.example/result"
        settings = self.scrape_settings(form_url="")

        with self.assertRaisesRegex(ValueError, "unsafe scrape navigation"):
            main.fetch_actions(settings, browser_factory=lambda: browser)

        self.assertEqual(browser.submission_response.close_calls, 1)

    def test_fetch_actions_preserves_read_error_when_close_also_fails(self):
        browser = FakeBrowser()
        browser.submission_response = FakeResponse(
            read_error=OSError("read failed"),
            close_error=OSError("close failed"),
        )
        browser.responses[1] = browser.submission_response
        settings = self.scrape_settings(form_url="")

        with self.assertRaisesRegex(OSError, "read failed"):
            main.fetch_actions(settings, browser_factory=lambda: browser)

    def test_extract_actions_rejects_excessive_div_nesting(self):
        html = '<div class="action">' + ("<div>" * 300) + "<span>value</span>"

        with self.assertRaisesRegex(ValueError, "HTML nesting"):
            main.extract_actions(html)

    def test_fetch_actions_closes_selected_response_when_read_fails(self):
        browser = FakeBrowser()
        browser.submission_response = FakeResponse(read_error=OSError("read failed"))
        browser.responses[1] = browser.submission_response
        settings = main.ScrapeSettings(
            name="sample",
            recipient="to@example.com",
            site="https://example.com",
            form_url="",
            form={},
            fake_user_agent="agent",
            fake_referer="referer",
        )

        with self.assertRaisesRegex(OSError, "read failed"):
            main.fetch_actions(settings, browser_factory=lambda: browser)

        self.assertEqual(browser.submission_response.close_calls, 1)

    def test_read_bounded_response_accepts_exact_limit(self):
        response = FakeResponse(b"x" * main.MAX_SCRAPE_RESPONSE_BYTES)

        self.assertEqual(len(main._read_bounded_response(response)), main.MAX_SCRAPE_RESPONSE_BYTES)
        self.assertEqual(response.read_sizes, [main.MAX_SCRAPE_RESPONSE_BYTES + 1, 1])

    def test_read_bounded_response_rejects_one_byte_over_limit(self):
        response = FakeResponse(b"x" * (main.MAX_SCRAPE_RESPONSE_BYTES + 1))

        with self.assertRaisesRegex(ValueError, "configured size limit"):
            main._read_bounded_response(response)

        self.assertEqual(response.read_sizes, [main.MAX_SCRAPE_RESPONSE_BYTES + 1])

    def test_read_bounded_response_enforces_literal_one_mebibyte_boundary(self):
        accepted = FakeResponse(b"x" * 1048576)

        self.assertEqual(len(main._read_bounded_response(accepted)), 1048576)

        rejected = FakeResponse(b"x" * 1048577)

        with self.assertRaisesRegex(ValueError, "configured size limit"):
            main._read_bounded_response(rejected)

    def test_read_bounded_response_assembles_short_reads(self):
        response = FakeResponse(b"abcdef", max_chunk_size=2)

        self.assertEqual(main._read_bounded_response(response), b"abcdef")
        self.assertEqual(
            response.read_sizes,
            [
                main.MAX_SCRAPE_RESPONSE_BYTES + 1,
                main.MAX_SCRAPE_RESPONSE_BYTES - 1,
                main.MAX_SCRAPE_RESPONSE_BYTES - 3,
                main.MAX_SCRAPE_RESPONSE_BYTES - 5,
            ],
        )

    def test_read_bounded_response_rejects_oversize_across_short_reads(self):
        response = FakeResponse(
            b"x" * (main.MAX_SCRAPE_RESPONSE_BYTES + 1),
            max_chunk_size=4096,
        )

        with self.assertRaisesRegex(ValueError, "configured size limit"):
            main._read_bounded_response(response)

        self.assertEqual(response.offset, main.MAX_SCRAPE_RESPONSE_BYTES + 1)

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

    def test_load_scrape_settings_rejects_unsafe_http_authorities(self):
        invalid_sites = (
            "http://127.0.0.1/private",
            "http://[::1]/private",
            "http://localhost/private",
            "https://user:secret@example.com/private",
            "https://example.com:bad/private",
        )

        for site in invalid_sites:
            with self.subTest(site=site):
                module = SimpleNamespace(
                    name="sample",
                    to="to@example.com",
                    site=site,
                    form_url="",
                    form={"q": "value"},
                    fake_user_agent="Mechenz",
                    fake_referer="https://example.com",
                )
                with self.assertRaisesRegex(ValueError, "invalid scrape settings: site"):
                    main.load_scrape_settings(module)

    def test_load_scrape_settings_rejects_unsafe_request_headers(self):
        for name, value in (
            ("fake_user_agent", "Mechenz\r\nX-Injected: yes"),
            ("fake_referer", "https://example.com\nX-Injected: yes"),
            ("fake_referer", "file:///tmp/private.html"),
        ):
            with self.subTest(name=name):
                values = {
                    "name": "sample",
                    "to": "to@example.com",
                    "site": "https://example.com",
                    "form_url": "",
                    "form": {"q": "value"},
                    "fake_user_agent": "Mechenz",
                    "fake_referer": "https://example.com",
                }
                values[name] = value
                with self.assertRaisesRegex(ValueError, "invalid scrape settings"):
                    main.load_scrape_settings(SimpleNamespace(**values))

    @staticmethod
    def scrape_settings(form_url="https://example.com/results"):
        return main.ScrapeSettings(
            name="sample",
            recipient="to@example.com",
            site="https://example.com",
            form_url=form_url,
            form={},
            fake_user_agent="agent",
            fake_referer="https://example.com",
        )

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
