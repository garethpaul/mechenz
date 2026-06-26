import unittest
from unittest import mock

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

    def starttls(self, *, context):
        self.calls.append(("starttls", context))

    def login(self, login, password):
        self.calls.append(("login", login, password))

    def sendmail(self, sender, recipients, message):
        self.calls.append(("sendmail", sender, recipients, message))
        return {}

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

    def test_load_mail_settings_rejects_invalid_port_without_echoing_value(self):
        with self.assertRaisesRegex(ValueError, "invalid SMTP_PORT"):
            RoyalMail.load_mail_settings(
                {
                    "SMTP_LOGIN": "sender@example.com",
                    "SMTP_PASSWORD": "secret",
                    "SMTP_PORT": "not-a-port",
                }
            )

        try:
            RoyalMail.load_mail_settings(
                {
                    "SMTP_LOGIN": "sender@example.com",
                    "SMTP_PASSWORD": "secret",
                    "SMTP_PORT": "not-a-port",
                }
            )
        except ValueError as error:
            self.assertNotIn("not-a-port", str(error))

    def test_load_mail_settings_rejects_invalid_timeout_without_echoing_value(self):
        with self.assertRaisesRegex(ValueError, "invalid SMTP_TIMEOUT"):
            RoyalMail.load_mail_settings(
                {
                    "SMTP_LOGIN": "sender@example.com",
                    "SMTP_PASSWORD": "secret",
                    "SMTP_TIMEOUT": "not-a-timeout",
                }
            )

        try:
            RoyalMail.load_mail_settings(
                {
                    "SMTP_LOGIN": "sender@example.com",
                    "SMTP_PASSWORD": "secret",
                    "SMTP_TIMEOUT": "not-a-timeout",
                }
            )
        except ValueError as error:
            self.assertNotIn("not-a-timeout", str(error))

    def test_load_mail_settings_rejects_port_outside_tcp_range(self):
        for port in ("0", "65536"):
            with self.subTest(port=port):
                with self.assertRaisesRegex(ValueError, "invalid SMTP_PORT"):
                    RoyalMail.load_mail_settings(
                        {
                            "SMTP_LOGIN": "sender@example.com",
                            "SMTP_PASSWORD": "secret",
                            "SMTP_PORT": port,
                        }
                    )

    def test_load_mail_settings_rejects_unbounded_timeout(self):
        for timeout in ("nan", "inf", "301"):
            with self.subTest(timeout=timeout):
                with self.assertRaisesRegex(ValueError, "invalid SMTP_TIMEOUT"):
                    RoyalMail.load_mail_settings(
                        {
                            "SMTP_LOGIN": "sender@example.com",
                            "SMTP_PASSWORD": "secret",
                            "SMTP_TIMEOUT": timeout,
                        }
                    )

    def test_load_mail_settings_accepts_numeric_upper_bounds(self):
        settings = RoyalMail.load_mail_settings(
            {
                "SMTP_LOGIN": "sender@example.com",
                "SMTP_PASSWORD": "secret",
                "SMTP_PORT": "65535",
                "SMTP_TIMEOUT": "300",
            }
        )

        self.assertEqual(settings.port, 65535)
        self.assertEqual(settings.timeout, 300.0)

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
        self.assertEqual([call[0] for call in smtp.calls].count("starttls"), 1)
        self.assertIn(("login", "sender@example.com", "secret"), smtp.calls)
        sendmail_call = [call for call in smtp.calls if call[0] == "sendmail"][0]
        self.assertEqual(sendmail_call[1], "sender@example.com")
        self.assertEqual(sendmail_call[2], ["to@example.com"])
        self.assertIn("Subject", sendmail_call[3])

    def test_send_mail_passes_default_context_to_starttls_before_login(self):
        tls_context = object()
        settings = RoyalMail.MailSettings(
            login="sender@example.com",
            password="secret",
            host="smtp.example.com",
            port=2525,
            timeout=5,
        )

        with mock.patch.object(
            RoyalMail.ssl,
            "create_default_context",
            return_value=tls_context,
        ) as context_factory:
            RoyalMail.send_mail(
                ["to@example.com"],
                "Subject",
                "Body",
                mail_settings=settings,
                smtp_factory=FakeSMTP,
            )

        smtp = FakeSMTP.instances[0]
        context_factory.assert_called_once_with()
        self.assertIn(("starttls", tls_context), smtp.calls)
        self.assertLess(
            smtp.calls.index(("starttls", tls_context)),
            smtp.calls.index(("login", "sender@example.com", "secret")),
        )

    def test_send_mail_normalizes_recipients(self):
        settings = RoyalMail.MailSettings(
            login="sender@example.com",
            password="secret",
            host="smtp.example.com",
            port=2525,
            timeout=5,
        )

        RoyalMail.send_mail(
            [" to@example.com ", "", " ", None],
            "Subject",
            "Body",
            mail_settings=settings,
            smtp_factory=FakeSMTP,
        )

        sendmail_call = [call for call in FakeSMTP.instances[0].calls if call[0] == "sendmail"][0]
        self.assertEqual(sendmail_call[2], ["to@example.com"])

    def test_send_mail_rejects_blank_recipients(self):
        settings = RoyalMail.MailSettings(
            login="sender@example.com",
            password="secret",
            host="smtp.example.com",
            port=2525,
            timeout=5,
        )

        with self.assertRaisesRegex(ValueError, "at least one recipient"):
            RoyalMail.send_mail(
                [" ", "", None],
                "Subject",
                "Body",
                mail_settings=settings,
                smtp_factory=FakeSMTP,
            )

        self.assertEqual(FakeSMTP.instances, [])

    def test_send_mail_rejects_header_newlines_before_smtp(self):
        settings = RoyalMail.MailSettings(
            login="sender@example.com",
            password="secret",
            host="smtp.example.com",
            port=2525,
            timeout=5,
        )

        with self.assertRaisesRegex(ValueError, "invalid SMTP_SUBJECT"):
            RoyalMail.send_mail(
                ["to@example.com"],
                "Subject\nBcc: other@example.com",
                "Body",
                mail_settings=settings,
                smtp_factory=FakeSMTP,
            )

        with self.assertRaisesRegex(ValueError, "invalid SMTP_RECIPIENT"):
            RoyalMail.send_mail(
                ["to@example.com\nBcc: other@example.com"],
                "Subject",
                "Body",
                mail_settings=settings,
                smtp_factory=FakeSMTP,
            )

        bad_sender_settings = RoyalMail.MailSettings(
            login="sender@example.com\nBcc: other@example.com",
            password="secret",
            host="smtp.example.com",
            port=2525,
            timeout=5,
        )
        with self.assertRaisesRegex(ValueError, "invalid SMTP_LOGIN"):
            RoyalMail.send_mail(
                ["to@example.com"],
                "Subject",
                "Body",
                mail_settings=bad_sender_settings,
                smtp_factory=FakeSMTP,
            )

        self.assertEqual(FakeSMTP.instances, [])

    def test_send_mail_rejects_partial_recipient_refusals(self):
        class PartiallyRefusingSMTP(FakeSMTP):
            def sendmail(self, sender, recipients, message):
                super().sendmail(sender, recipients, message)
                return {"refused@example.com": (550, b"no such user")}

        settings = RoyalMail.MailSettings(
            login="sender@example.com",
            password="secret",
            host="smtp.example.com",
            port=2525,
            timeout=5,
        )

        with self.assertRaises(RoyalMail.smtplib.SMTPRecipientsRefused):
            RoyalMail.send_mail(
                ["accepted@example.com", "refused@example.com"],
                "Subject",
                "Body",
                mail_settings=settings,
                smtp_factory=PartiallyRefusingSMTP,
            )

    def test_send_mail_preserves_primary_error_when_close_fails(self):
        class FailingSMTP(FakeSMTP):
            def login(self, username, password):
                raise OSError("authentication transport failed")

            def close(self):
                raise OSError("close failed")

        settings = RoyalMail.MailSettings(
            login="sender@example.com",
            password="secret",
            host="smtp.example.com",
            port=2525,
            timeout=5,
        )

        with self.assertRaisesRegex(OSError, "authentication transport failed"):
            RoyalMail.send_mail(
                ["to@example.com"],
                "Subject",
                "Body",
                mail_settings=settings,
                smtp_factory=FailingSMTP,
            )

    def test_send_mail_ignores_close_failure_after_successful_delivery(self):
        class CloseFailingSMTP(FakeSMTP):
            def close(self):
                self.calls.append(("close",))
                raise OSError("close failed")

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
            smtp_factory=CloseFailingSMTP,
        )

        smtp = CloseFailingSMTP.instances[0]
        self.assertTrue(any(call[0] == "sendmail" for call in smtp.calls))
        self.assertIn(("close",), smtp.calls)


if __name__ == "__main__":
    unittest.main()
