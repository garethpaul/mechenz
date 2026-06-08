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


class MainTests(unittest.TestCase):
    def test_extract_actions_reads_first_span_from_each_action(self):
        html = """
        <div class="action"><span>First</span><span>Ignored</span></div>
        <div class="other"><span>Skipped</span></div>
        <div class="action"><span>Second</span></div>
        """

        self.assertEqual(main.extract_actions(html), ["First", "Second"])

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


if __name__ == "__main__":
    unittest.main()
