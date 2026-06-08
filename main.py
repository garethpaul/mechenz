"""Scrape configured actions, cache the latest result, and email on changes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
import importlib
import os
from typing import Callable, Iterable, Mapping, Optional, Sequence

import RoyalMail


@dataclass(frozen=True)
class ScrapeSettings:
    name: str
    recipient: str
    site: str
    form_url: str
    form: Mapping[str, str]
    fake_user_agent: str
    fake_referer: str
    respect_robots: bool = True


class ActionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.actions = []
        self._action_depth = 0
        self._capture_span = False
        self._captured_for_action = False
        self._parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "div" and "action" in attributes.get("class", "").split():
            self._action_depth += 1
            self._captured_for_action = False
            return

        if tag == "span" and self._action_depth and not self._captured_for_action:
            self._capture_span = True
            self._parts = []

    def handle_data(self, data):
        if self._capture_span:
            self._parts.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self._capture_span:
            text = "".join(self._parts).strip()
            if text:
                self.actions.append(text)
            self._capture_span = False
            self._captured_for_action = True
            self._parts = []
            return

        if tag == "div" and self._action_depth:
            self._action_depth -= 1
            if self._action_depth == 0:
                self._capture_span = False
                self._captured_for_action = False
                self._parts = []


def extract_actions(html) -> list[str]:
    if isinstance(html, bytes):
        html = html.decode("utf-8", errors="replace")

    parser = ActionParser()
    parser.feed(html)
    return parser.actions


def build_email_body(actions: Sequence[str]) -> str:
    lines = ["Info:", ""]
    lines.extend(actions)
    lines.extend(["", "Thanks!", "Mechenz"])
    return "\n".join(lines)


def notify_if_changed(
    actions: Sequence[str],
    cache,
    name: str,
    recipient: str,
    mailer: Callable[[Iterable[str], str, str], None],
    today: Callable[[], date] = date.today,
) -> bool:
    current = list(actions)
    if current == (cache.get(name) or []):
        return False

    subject = f"Mechenz | {today()} | {name}"
    mailer([recipient], subject, build_email_body(current))
    cache.set(name, current)
    return True


def fetch_actions(settings: ScrapeSettings, browser_factory=None) -> list[str]:
    if browser_factory is None:
        mechanize = importlib.import_module("mechanize")
        browser_factory = mechanize.Browser

    browser = browser_factory()
    browser.addheaders = [
        ("User-agent", settings.fake_user_agent),
        ("Referer", settings.fake_referer),
    ]
    browser.set_handle_robots(settings.respect_robots)
    browser.open(settings.site)
    browser.select_form(nr=0)
    for key, value in settings.form.items():
        browser.form[key] = value
    response = browser.submit()
    if settings.form_url:
        response = browser.open(settings.form_url)
    return extract_actions(response.read())


def load_scrape_settings(settings_module, env: Mapping[str, str] = os.environ) -> ScrapeSettings:
    missing = [
        name
        for name in ("name", "to", "site", "form_url", "form", "fake_user_agent", "fake_referer")
        if not hasattr(settings_module, name)
    ]
    if missing:
        raise ValueError("missing required settings: " + ", ".join(missing))

    form = getattr(settings_module, "form")
    if not isinstance(form, Mapping):
        raise ValueError("settings.form must be a mapping")

    ignore_robots = _truthy(env.get("MECHENZ_IGNORE_ROBOTS") or getattr(settings_module, "ignore_robots", ""))

    return ScrapeSettings(
        name=str(getattr(settings_module, "name")).strip(),
        recipient=str(getattr(settings_module, "to")).strip(),
        site=str(getattr(settings_module, "site")).strip(),
        form_url=str(getattr(settings_module, "form_url")).strip(),
        form={str(key): str(value) for key, value in form.items()},
        fake_user_agent=str(getattr(settings_module, "fake_user_agent")).strip(),
        fake_referer=str(getattr(settings_module, "fake_referer")).strip(),
        respect_robots=not ignore_robots,
    )


def load_settings_module():
    return importlib.import_module("settings")


def create_cache(env: Mapping[str, str] = os.environ):
    memcache = importlib.import_module("memcache")
    server = env.get("MEMCACHE_SERVER", "127.0.0.1:11211")
    return memcache.Client([server], debug=0)


def get_data(data, cache=None, settings_module=None):
    module = settings_module or load_settings_module()
    scrape_settings = load_scrape_settings(module)
    mail_settings = RoyalMail.load_mail_settings(settings_module=module)
    cache = cache or create_cache()
    return notify_if_changed(
        data,
        cache,
        scrape_settings.name,
        scrape_settings.recipient,
        lambda to, subject, body: RoyalMail.send_mail(to, subject, body, mail_settings=mail_settings),
    )


def main():
    settings_module = load_settings_module()
    scrape_settings = load_scrape_settings(settings_module)
    mail_settings = RoyalMail.load_mail_settings(settings_module=settings_module)
    cache = create_cache()
    actions = fetch_actions(scrape_settings)
    notify_if_changed(
        actions,
        cache,
        scrape_settings.name,
        scrape_settings.recipient,
        lambda to, subject, body: RoyalMail.send_mail(to, subject, body, mail_settings=mail_settings),
    )


def _truthy(value) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y", "on"}


if __name__ == "__main__":
    main()
