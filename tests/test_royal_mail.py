import unittest

import RoyalMail


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.calls = []
        FakeSMTP.instances.append(self)

    def ehlo(self):
        self.calls.append(("ehlo",))

    def starttls(self):
        self.calls.append(("starttls",))

    def login(self, login, password):
        self.calls.append(("login", login, password))

    def sendmail(self, sender, recipients, message):
        self.calls.append(("sendmail", sender, recipients, message))

    def close(self):
        self.calls.append(("close",))


class RoyalMailTests(unittest.TestCase):
    def setUp(self):
        FakeSMTP.instances = []

    def test_load_mail_settings_prefers_environment(self):
        settings = RoyalMail.load_mail_settings(
            {
                "SMTP_LOGIN": "sender@example.com",
                "SMTP_PASSWORD": "secret",
                "SMTP_HOST": "smtp.example.com",
                "SMTP_PORT": "2525",
                "SMTP_TIMEOUT": "5",
            }
        )

        self.assertEqual(settings.login, "sender@example.com")
        self.assertEqual(settings.password, "secret")
        self.assertEqual(settings.host, "smtp.example.com")
        self.assertEqual(settings.port, 2525)
        self.assertEqual(settings.timeout, 5.0)

    def test_load_mail_settings_requires_credentials(self):
        with self.assertRaisesRegex(ValueError, "SMTP_LOGIN, SMTP_PASSWORD"):
            RoyalMail.load_mail_settings({})

    def test_send_mail_uses_tls_login_and_recipients(self):
        settings = RoyalMail.MailSettings(
            login="sender@example.com",
            password="secret",
            host="smtp.example.com",
            port=2525,
            timeout=5,
        )

        RoyalMail.send_mail(
            ["to@example.com"],
            "Subject",
            "Body",
            mail_settings=settings,
            smtp_factory=FakeSMTP,
        )

        smtp = FakeSMTP.instances[0]
        self.assertEqual((smtp.host, smtp.port, smtp.timeout), ("smtp.example.com", 2525, 5))
        self.assertIn(("starttls",), smtp.calls)
        self.assertIn(("login", "sender@example.com", "secret"), smtp.calls)
        sendmail_call = [call for call in smtp.calls if call[0] == "sendmail"][0]
        self.assertEqual(sendmail_call[1], "sender@example.com")
        self.assertEqual(sendmail_call[2], ["to@example.com"])
        self.assertIn("Subject", sendmail_call[3])


if __name__ == "__main__":
    unittest.main()
