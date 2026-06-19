"""Scrape configured actions, cache the latest result, and email on changes."""

from __future__ import annotations

import codecs
from collections.abc import Callable, Iterable, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
import importlib
import ipaddress
import math
import os
from urllib.parse import urlparse

import RoyalMail

SCRAPE_REQUEST_TIMEOUT = 15
MAX_SCRAPE_RESPONSE_BYTES = 1024 * 1024
MAX_ACTION_DIV_NESTING = 256
DEFAULT_MEMCACHE_TIMEOUT = 5.0
MAX_MEMCACHE_TIMEOUT = 300.0


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
                if self._action_depth >= MAX_ACTION_DIV_NESTING:
                    raise ValueError("HTML nesting exceeds configured limit")
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
    allowed_origins = {_http_origin(settings.site)}
    if settings.form_url:
        allowed_origins.add(_http_origin(settings.form_url))

    with _closing_response(
        browser.open(settings.site, timeout=SCRAPE_REQUEST_TIMEOUT)
    ) as landing_response:
        _validate_response_navigation(landing_response, allowed_origins)
        browser.select_form(nr=0)
        for key, value in settings.form.items():
            browser.form[key] = value
        submission_request = browser.click()
        _validate_navigation_target(submission_request, allowed_origins)

    response = browser.open(submission_request, timeout=SCRAPE_REQUEST_TIMEOUT)
    if settings.form_url:
        with _closing_response(response) as submission_response:
            _validate_response_navigation(submission_response, allowed_origins)
        response = browser.open(settings.form_url, timeout=SCRAPE_REQUEST_TIMEOUT)
    with _closing_response(response):
        _validate_response_navigation(response, allowed_origins)
        response_body = _read_bounded_response(response)
    return extract_actions(response_body, encoding=settings.encoding)


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

    invalid_headers = []
    if not _valid_header_value(required_values["fake_user_agent"]):
        invalid_headers.append("fake_user_agent")
    if (
        not _valid_header_value(required_values["fake_referer"])
        or not _valid_http_url(required_values["fake_referer"])
    ):
        invalid_headers.append("fake_referer")
    if invalid_headers:
        raise ValueError("invalid scrape settings: " + ", ".join(invalid_headers))

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


def _read_bounded_response(response) -> bytes:
    chunks = []
    remaining = MAX_SCRAPE_RESPONSE_BYTES + 1
    while remaining > 0:
        chunk = response.read(remaining)
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)

    body = b"".join(chunks)
    if len(body) > MAX_SCRAPE_RESPONSE_BYTES:
        raise ValueError("scrape response exceeds configured size limit")
    return body


def load_settings_module():
    return importlib.import_module("settings")


def create_cache(env: Mapping[str, str] = os.environ, settings_module=None):
    server = env.get("MEMCACHE_SERVER")
    configured_servers = server if server is not None and str(server).strip() else getattr(
        settings_module, "memcache_servers", ["127.0.0.1:11211"]
    )
    servers = _normalize_memcache_servers(configured_servers)
    timeout = env.get("MEMCACHE_TIMEOUT")
    configured_timeout = timeout if timeout is not None and str(timeout).strip() else getattr(
        settings_module, "memcache_timeout", DEFAULT_MEMCACHE_TIMEOUT
    )
    if configured_timeout is None or not str(configured_timeout).strip():
        configured_timeout = DEFAULT_MEMCACHE_TIMEOUT
    socket_timeout = _parse_memcache_timeout(configured_timeout)
    memcache = importlib.import_module("memcache")
    return memcache.Client(servers, debug=0, socket_timeout=socket_timeout)


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


def _normalize_memcache_servers(value) -> list[str]:
    candidates = [value] if isinstance(value, str) else value
    if not isinstance(candidates, Sequence) or isinstance(candidates, (bytes, bytearray)):
        raise ValueError("memcache_servers must be a string or sequence of strings")

    if not candidates or any(not isinstance(server, str) or not server.strip() for server in candidates):
        raise ValueError("memcache_servers must contain non-empty strings")

    return [_normalize_memcache_server(server.strip()) for server in candidates]


def _parse_memcache_timeout(value) -> float:
    try:
        timeout = float(value)
    except (TypeError, ValueError):
        raise ValueError("invalid MEMCACHE_TIMEOUT") from None
    if not math.isfinite(timeout) or timeout <= 0 or timeout > MAX_MEMCACHE_TIMEOUT:
        raise ValueError("invalid MEMCACHE_TIMEOUT")
    return timeout


def _valid_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        port = parsed.port
    except ValueError:
        return False
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or any(character.isspace() or ord(character) < 32 for character in value)
    ):
        return False
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname == "localhost" or hostname.endswith(".localhost"):
        return False
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        return False
    return port is None or 0 < port <= 65535


def _http_origin(value: str) -> tuple[str, str, int]:
    if not _valid_http_url(value):
        raise ValueError("unsafe scrape navigation")
    parsed = urlparse(value)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return parsed.scheme, parsed.hostname.rstrip(".").lower(), port


def _navigation_url(target) -> str:
    if isinstance(target, str):
        return target
    get_full_url = getattr(target, "get_full_url", None)
    if not callable(get_full_url):
        raise ValueError("unsafe scrape navigation")
    return get_full_url()


def _validate_navigation_target(target, allowed_origins) -> None:
    if _http_origin(_navigation_url(target)) not in allowed_origins:
        raise ValueError("unsafe scrape navigation")


def _validate_response_navigation(response, allowed_origins) -> None:
    geturl = getattr(response, "geturl", None)
    if not callable(geturl):
        raise ValueError("unsafe scrape navigation")
    _validate_navigation_target(geturl(), allowed_origins)


@contextmanager
def _closing_response(response):
    try:
        yield response
    except BaseException:
        try:
            response.close()
        except BaseException:
            pass
        raise
    else:
        response.close()


def _normalize_memcache_server(server: str) -> str:
    if server.startswith("unix:") or server.startswith("/"):
        path = server[5:] if server.startswith("unix:") else server
        if (
            not path.startswith("/")
            or any(character.isspace() or ord(character) < 32 for character in path)
        ):
            raise ValueError("memcache_servers contains an invalid endpoint")
        return "unix:" + path
    if server.startswith("inet6:"):
        endpoint = server[6:]
        try:
            parsed = urlparse("//" + endpoint)
            port = parsed.port
            address = ipaddress.IPv6Address(parsed.hostname or "")
        except (ValueError, ipaddress.AddressValueError):
            raise ValueError("memcache_servers contains an invalid endpoint") from None
        if port is None or not 0 < port <= 65535 or parsed.path or parsed.query or parsed.fragment:
            raise ValueError("memcache_servers contains an invalid endpoint")
        return f"inet6:[{address.compressed}]:{port}"
    if "://" in server or any(character.isspace() or ord(character) < 32 for character in server):
        raise ValueError("memcache_servers contains an invalid endpoint")
    try:
        parsed = urlparse("//" + server)
        port = parsed.port
    except ValueError:
        raise ValueError("memcache_servers contains an invalid endpoint") from None
    if (
        not parsed.hostname
        or port is None
        or not 0 < port <= 65535
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("memcache_servers contains an invalid endpoint")
    hostname = parsed.hostname.rstrip(".")
    if not hostname:
        raise ValueError("memcache_servers contains an invalid endpoint")
    if ":" in hostname:
        hostname = f"[{hostname}]"
    return f"{hostname}:{port}"


def _parse_encoding_setting(name: str, value, default: str = "utf-8") -> str:
    encoding = str(value).strip() if value is not None else default
    if not encoding:
        return default
    try:
        codecs.lookup(encoding)
    except LookupError:
        raise ValueError(f"invalid {name}") from None
    return encoding


def _valid_header_value(value: str) -> bool:
    return not any(ord(character) < 32 or ord(character) == 127 for character in value)


if __name__ == "__main__":
    main()
