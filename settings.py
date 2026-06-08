#!/usr/bin/env python

"""Environment-backed runtime settings for mechenz."""

import json
import os


class MissingConfiguration(RuntimeError):
    """Raised when required runtime configuration is absent or invalid."""


class FormSettings(dict):
    def iteritems(self):
        return self.items()


def required_value(name, env_name):
    value = os.environ.get(env_name)
    if value not in (None, ""):
        return value

    raise MissingConfiguration(
        "Missing required configuration for {0}. Set {1} before running "
        "mechenz.".format(name, env_name)
    )


def required_form(name, env_name):
    raw_value = required_value(name, env_name)
    try:
        value = json.loads(raw_value)
    except ValueError as exc:
        raise MissingConfiguration(
            "{0} must be a JSON object in {1}: {2}".format(name, env_name, exc)
        )

    if not isinstance(value, dict):
        raise MissingConfiguration(
            "{0} must be a JSON object in {1}.".format(name, env_name)
        )

    return FormSettings(value)


name = required_value("name", "MECHENZ_NAME")
to = required_value("to", "MECHENZ_TO_EMAIL")
fake_user_agent = required_value("fake_user_agent", "MECHENZ_FAKE_USER_AGENT")
fake_referer = required_value("fake_referer", "MECHENZ_FAKE_REFERER")
site = required_value("site", "MECHENZ_SITE_URL")
form_url = required_value("form_url", "MECHENZ_FORM_URL")
form = required_form("form", "MECHENZ_FORM_JSON")
smtp_login = required_value("smtp_login", "MECHENZ_SMTP_LOGIN")
smtp_password = required_value("smtp_password", "MECHENZ_SMTP_PASSWORD")
