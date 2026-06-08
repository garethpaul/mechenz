import importlib
import os
import sys
import unittest


REQUIRED_ENV = {
    "MECHENZ_NAME": "Daily Check",
    "MECHENZ_TO_EMAIL": "recipient@example.com",
    "MECHENZ_FAKE_USER_AGENT": "mechenz-test",
    "MECHENZ_FAKE_REFERER": "https://example.com/referrer",
    "MECHENZ_SITE_URL": "https://example.com/login",
    "MECHENZ_FORM_URL": "https://example.com/results",
    "MECHENZ_FORM_JSON": '{"postcode": "SW1A 1AA", "radius": "5"}',
    "MECHENZ_SMTP_LOGIN": "sender@example.com",
    "MECHENZ_SMTP_PASSWORD": "password",
}


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.original_env = dict(
            (name, os.environ.get(name)) for name in REQUIRED_ENV
        )
        sys.modules.pop("settings", None)

    def tearDown(self):
        for name, value in self.original_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        sys.modules.pop("settings", None)

    def clear_env(self):
        for name in REQUIRED_ENV:
            os.environ.pop(name, None)

    def set_env(self):
        for name, value in REQUIRED_ENV.items():
            os.environ[name] = value

    def test_missing_settings_raise_clear_error(self):
        self.clear_env()

        with self.assertRaisesRegex(RuntimeError, "MECHENZ_NAME"):
            importlib.import_module("settings")

    def test_settings_load_from_environment(self):
        self.clear_env()
        self.set_env()

        settings = importlib.import_module("settings")

        self.assertEqual("Daily Check", settings.name)
        self.assertEqual("recipient@example.com", settings.to)
        self.assertEqual("mechenz-test", settings.fake_user_agent)
        self.assertEqual("https://example.com/referrer", settings.fake_referer)
        self.assertEqual("https://example.com/login", settings.site)
        self.assertEqual("https://example.com/results", settings.form_url)
        self.assertEqual("sender@example.com", settings.smtp_login)
        self.assertEqual("password", settings.smtp_password)
        self.assertEqual(
            {"postcode": "SW1A 1AA", "radius": "5"},
            dict(settings.form.iteritems()),
        )

    def test_form_json_must_be_an_object(self):
        self.clear_env()
        self.set_env()
        os.environ["MECHENZ_FORM_JSON"] = "[]"

        with self.assertRaisesRegex(RuntimeError, "MECHENZ_FORM_JSON"):
            importlib.import_module("settings")


if __name__ == "__main__":
    unittest.main()
