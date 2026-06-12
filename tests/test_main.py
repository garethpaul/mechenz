from datetime import date
from types import SimpleNamespace
import unittest

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
    def __init__(self, body):
        self.body = body
        self.read_sizes = []
        self.closed = False

    def read(self, size):
        self.read_sizes.append(size)
        return self.body[:size]

    def close(self):
        self.closed = True


class FakeBrowser:
    def __init__(self, submit_response, form_response=None):
        self.submit_response = submit_response
        self.form_response = form_response
        self.addheaders = []
        self.form = {}
        self.robots = None
        self.opened = []

    def set_handle_robots(self, value):
        self.robots = value

    def open(self, url):
        self.opened.append(url)
        if len(self.opened) == 1:
            return FakeResponse(b"")
        return self.form_response

    def select_form(self, nr):
        self.selected_form = nr

    def submit(self):
        return self.submit_response


class MainTests(unittest.TestCase):
    def test_extract_actions_reads_first_span_from_each_action(self):
        html = """
        <div class="action"><span>First</span><span>Ignored</span></div>
        <div class="other"><span>Skipped</span></div>
        <div class="action"><span>Second</span></div>
        """

        self.assertEqual(main.extract_actions(html), ["First", "Second"])

    def test_fetch_actions_bounds_and_closes_submit_response(self):
        response = FakeResponse(b'<div class="action"><span>First</span></div>')
        browser = FakeBrowser(response)
        settings = self.scrape_settings(form_url="")

        actions = main.fetch_actions(settings, browser_factory=lambda: browser)

        self.assertEqual(actions, ["First"])
        self.assertEqual(response.read_sizes, [main.MAXIMUM_SCRAPE_RESPONSE_BYTES + 1])
        self.assertTrue(response.closed)

    def test_fetch_actions_rejects_oversized_response_and_closes_it(self):
        response = FakeResponse(b"x" * (main.MAXIMUM_SCRAPE_RESPONSE_BYTES + 1))
        browser = FakeBrowser(response)

        with self.assertRaisesRegex(ValueError, "scrape response exceeds 1 MiB limit"):
            main.fetch_actions(self.scrape_settings(form_url=""), browser_factory=lambda: browser)

        self.assertTrue(response.closed)

    def test_fetch_actions_closes_submit_response_before_form_url_response(self):
        submit_response = FakeResponse(b"ignored")
        form_response = FakeResponse(b'<div class="action"><span>Final</span></div>')
        browser = FakeBrowser(submit_response, form_response)

        actions = main.fetch_actions(self.scrape_settings(), browser_factory=lambda: browser)

        self.assertEqual(actions, ["Final"])
        self.assertTrue(submit_response.closed)
        self.assertTrue(form_response.closed)

    @staticmethod
    def scrape_settings(form_url="https://example.com/results"):
        return main.ScrapeSettings(
            name="sample",
            recipient="to@example.com",
            site="https://example.com",
            form_url=form_url,
            form={"q": "value"},
            fake_user_agent="Mechenz",
            fake_referer="https://example.com",
        )

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
