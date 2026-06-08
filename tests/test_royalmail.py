from types import SimpleNamespace
import unittest

import RoyalMail


class FakeSMTP:
    def __init__(self):
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()

    def connect(self, server):
        self.calls.append(("connect", server))

    def ehlo(self):
        self.calls.append(("ehlo",))

    def starttls(self):
        self.calls.append(("starttls",))

    def login(self, username, password):
        self.calls.append(("login", username, password))

    def sendmail(self, from_addr, to, message):
        self.calls.append(("sendmail", from_addr, to, message))

    def close(self):
        self.calls.append(("close",))


class RoyalMailTests(unittest.TestCase):
    def test_send_mail_uses_settings_and_tls(self):
        smtp = FakeSMTP()
        settings = SimpleNamespace(smtp_login="sender@example.com")
        setattr(settings, "smtp_password", "test-password")

        RoyalMail.sendMail(
            ["to@example.com"],
            "Subject",
            "Body",
            settings_module=settings,
            smtp_factory=lambda *args, **kwargs: smtp,
        )

        self.assertIn(("starttls",), smtp.calls)
        self.assertIn(("login", "sender@example.com", "test-password"), smtp.calls)
        send_call = [call for call in smtp.calls if call[0] == "sendmail"][0]
        self.assertEqual(send_call[1], "sender@example.com")
        self.assertEqual(send_call[2], ["to@example.com"])
        self.assertIn("Subject", send_call[3])


if __name__ == "__main__":
    unittest.main()
