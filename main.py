"""Scrape configured actions, cache the latest result, and email on changes."""

from __future__ import annotations

import codecs
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
import importlib
import os
from urllib.parse import urlparse

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
    encoding: str = "utf-8"


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
        if tag == "div":
            if self._action_depth:
                self._action_depth += 1
            elif "action" in attributes.get("class", "").split():
                self._action_depth = 1
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


def extract_actions(html, encoding: str = "utf-8") -> list[str]:
    if isinstance(html, bytes):
        html = html.decode(encoding, errors="replace")

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
    return extract_actions(response.read(), encoding=settings.encoding)


def load_scrape_settings(settings_module, env: Mapping[str, str] = os.environ) -> ScrapeSettings:
    required_names = ("name", "to", "site", "form_url", "form", "fake_user_agent", "fake_referer")
    missing = [name for name in required_names if not hasattr(settings_module, name)]
    if missing:
        raise ValueError("missing required settings: " + ", ".join(missing))

    form = getattr(settings_module, "form")
    if not isinstance(form, Mapping):
        raise ValueError("settings.form must be a mapping")

    required_values = {
        "name": str(getattr(settings_module, "name")).strip(),
        "to": str(getattr(settings_module, "to")).strip(),
        "site": str(getattr(settings_module, "site")).strip(),
        "fake_user_agent": str(getattr(settings_module, "fake_user_agent")).strip(),
        "fake_referer": str(getattr(settings_module, "fake_referer")).strip(),
    }
    empty = [name for name, value in required_values.items() if not value]
    if empty:
        raise ValueError("empty required settings: " + ", ".join(empty))

    form_url = str(getattr(settings_module, "form_url")).strip()
    invalid_urls = []
    if not _valid_http_url(required_values["site"]):
        invalid_urls.append("site")
    if form_url and not _valid_http_url(form_url):
        invalid_urls.append("form_url")
    if invalid_urls:
        raise ValueError("invalid scrape settings: " + ", ".join(invalid_urls))

    respect_robots = _parse_bool_setting("respect_robots", getattr(settings_module, "respect_robots", True), default=True)
    ignore_robots_value = env.get("MECHENZ_IGNORE_ROBOTS")
    if ignore_robots_value is None or not str(ignore_robots_value).strip():
        ignore_robots_value = getattr(settings_module, "ignore_robots", "")
    ignore_robots = _parse_bool_setting("MECHENZ_IGNORE_ROBOTS", ignore_robots_value, default=False)
    if ignore_robots:
        respect_robots = False

    return ScrapeSettings(
        name=required_values["name"],
        recipient=required_values["to"],
        site=required_values["site"],
        form_url=form_url,
        form={str(key): str(value) for key, value in form.items()},
        fake_user_agent=required_values["fake_user_agent"],
        fake_referer=required_values["fake_referer"],
        respect_robots=respect_robots,
        encoding=_parse_encoding_setting("encoding", getattr(settings_module, "encoding", "utf-8")),
    )


def load_settings_module():
    return importlib.import_module("settings")


def create_cache(env: Mapping[str, str] = os.environ, settings_module=None):
    memcache = importlib.import_module("memcache")
    server = env.get("MEMCACHE_SERVER")
    servers = [server] if server else list(getattr(settings_module, "memcache_servers", ["127.0.0.1:11211"]))
    return memcache.Client(servers, debug=0)


def get_data(data, cache=None, settings_module=None):
    module = settings_module or load_settings_module()
    scrape_settings = load_scrape_settings(module)
    mail_settings = RoyalMail.load_mail_settings(settings_module=module)
    cache = cache or create_cache(settings_module=module)
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
    cache = create_cache(settings_module=settings_module)
    actions = fetch_actions(scrape_settings)
    notify_if_changed(
        actions,
        cache,
        scrape_settings.name,
        scrape_settings.recipient,
        lambda to, subject, body: RoyalMail.send_mail(to, subject, body, mail_settings=mail_settings),
    )


def _parse_bool_setting(name: str, value, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()
    if not normalized:
        return default
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False
    raise ValueError(f"invalid {name}")


def _valid_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _parse_encoding_setting(name: str, value, default: str = "utf-8") -> str:
    encoding = str(value).strip() if value is not None else default
    if not encoding:
        return default
    try:
        codecs.lookup(encoding)
    except LookupError:
        raise ValueError(f"invalid {name}") from None
    return encoding


if __name__ == "__main__":
    main()
