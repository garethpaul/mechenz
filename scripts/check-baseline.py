#!/usr/bin/env python3
"""Static baseline checks for the Mechenz sample."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MAKEFILE = """ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check clean compile fmt lint static-check test

check: clean lint test build

lint: static-check

test:
\tcd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests

build: compile

compile:
\tcd "$(ROOT)" && python3 -c "from pathlib import Path; [compile(path.read_text(), str(path), 'exec') for path in [Path('RoyalMail.py'), Path('main.py'), *Path('tests').glob('*.py')]]"

static-check:
\tpython3 "$(ROOT)/scripts/check-baseline.py"

clean:
\tfind "$(ROOT)" -type f \\( -name '*.pyc' -o -name '*.pyo' \\) -delete
\tfind "$(ROOT)" -type d -name '__pycache__' -prune -exec rm -rf {} +

fmt:
\tcd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
"""
REQUIRED = [
    ".gitignore",
    ".github/workflows/check.yml",
    "CHANGES.md",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "constraints.txt",
    "requirements.txt",
    "settings.py.example",
    "docs/plans/2026-06-08-mechenz-baseline.md",
    "docs/plans/2026-06-08-mechenz-modernization.md",
    "docs/plans/2026-06-08-python3-scraper-baseline.md",
    "docs/plans/2026-06-08-scrape-settings-validation.md",
    "docs/plans/2026-06-09-mail-settings-validation.md",
    "docs/plans/2026-06-09-mail-recipient-normalization.md",
    "docs/plans/2026-06-09-make-gate-targets.md",
    "docs/plans/2026-06-09-robot-setting-validation.md",
    "docs/plans/2026-06-09-scrape-url-validation.md",
    "docs/plans/2026-06-09-smtp-header-validation.md",
    "docs/plans/2026-06-10-scrape-encoding-validation.md",
    "docs/plans/2026-06-10-hosted-python-validation.md",
    "docs/plans/2026-06-10-smtp-numeric-bounds.md",
    "docs/plans/2026-06-12-python-dependency-constraints.md",
    "docs/plans/2026-06-12-checkout-credential-boundary.md",
    "docs/plans/2026-06-13-nested-action-parser.md",
    "docs/plans/2026-06-13-location-independent-make.md",
    "docs/plans/2026-06-14-scrape-request-timeout.md",
    "docs/plans/2026-06-14-memcache-server-normalization.md",
    "docs/plans/2026-06-14-scrape-response-body-limit.md",
    "docs/plans/2026-06-15-scrape-short-read-handling.md",
    "docs/plans/2026-06-15-scrape-response-closure.md",
    "docs/plans/2026-06-15-landing-response-closure.md",
    "docs/plans/2026-06-16-smtp-starttls-verification.md",
    "tests/test_main.py",
    "tests/test_royal_mail.py",
    "tests/test_royalmail.py",
]
SECRET_PATTERNS = [
    re.compile(r"smtp_password\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"SMTP_PASSWORD\s*=\s*[^ \n]+"),
]


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        for path in missing:
            print(f"missing required file: {path}", file=sys.stderr)
        return 1

    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.suffix in {".pyc", ".pyo"}:
            print(f"compiled Python artifact found: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        if path.is_dir() or "__pycache__" in path.parts:
            continue
        if path.suffix not in {".py", ".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                print(f"possible committed SMTP secret in {path.relative_to(ROOT)}", file=sys.stderr)
                return 1

    main_source = (ROOT / "main.py").read_text(encoding="utf-8")
    mail_source = (ROOT / "RoyalMail.py").read_text(encoding="utf-8")
    test_main = (ROOT / "tests/test_main.py").read_text(encoding="utf-8")
    test_mail = (ROOT / "tests/test_royal_mail.py").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    vision = (ROOT / "VISION.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    changes = (ROOT / "CHANGES.md").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    settings_plan = (ROOT / "docs/plans/2026-06-08-scrape-settings-validation.md").read_text(encoding="utf-8")
    mail_plan = (ROOT / "docs/plans/2026-06-09-mail-settings-validation.md").read_text(encoding="utf-8")
    recipient_plan = (ROOT / "docs/plans/2026-06-09-mail-recipient-normalization.md").read_text(encoding="utf-8")
    make_gates_plan = (ROOT / "docs/plans/2026-06-09-make-gate-targets.md").read_text(encoding="utf-8")
    robot_plan = (ROOT / "docs/plans/2026-06-09-robot-setting-validation.md").read_text(encoding="utf-8")
    url_plan = (ROOT / "docs/plans/2026-06-09-scrape-url-validation.md").read_text(encoding="utf-8")
    header_plan = (ROOT / "docs/plans/2026-06-09-smtp-header-validation.md").read_text(encoding="utf-8")
    encoding_plan = (ROOT / "docs/plans/2026-06-10-scrape-encoding-validation.md").read_text(encoding="utf-8")
    hosted_validation_plan = (ROOT / "docs/plans/2026-06-10-hosted-python-validation.md").read_text(encoding="utf-8")
    numeric_bounds_plan = (ROOT / "docs/plans/2026-06-10-smtp-numeric-bounds.md").read_text(encoding="utf-8")
    constraints_plan = (ROOT / "docs/plans/2026-06-12-python-dependency-constraints.md").read_text(encoding="utf-8")
    checkout_plan = (
        ROOT / "docs/plans/2026-06-12-checkout-credential-boundary.md"
    ).read_text(encoding="utf-8")
    parser_plan = (
        ROOT / "docs/plans/2026-06-13-nested-action-parser.md"
    ).read_text(encoding="utf-8")
    location_independent_make_plan = (
        ROOT / "docs/plans/2026-06-13-location-independent-make.md"
    ).read_text(encoding="utf-8")
    scrape_timeout_plan = (
        ROOT / "docs/plans/2026-06-14-scrape-request-timeout.md"
    ).read_text(encoding="utf-8")
    memcache_plan = (
        ROOT / "docs/plans/2026-06-14-memcache-server-normalization.md"
    ).read_text(encoding="utf-8")
    response_limit_plan = (
        ROOT / "docs/plans/2026-06-14-scrape-response-body-limit.md"
    ).read_text(encoding="utf-8")
    short_read_plan = (
        ROOT / "docs/plans/2026-06-15-scrape-short-read-handling.md"
    ).read_text(encoding="utf-8")
    response_closure_plan = (
        ROOT / "docs/plans/2026-06-15-scrape-response-closure.md"
    ).read_text(encoding="utf-8")
    landing_response_plan = (
        ROOT / "docs/plans/2026-06-15-landing-response-closure.md"
    ).read_text(encoding="utf-8")
    smtp_tls_plan = (
        ROOT / "docs/plans/2026-06-16-smtp-starttls-verification.md"
    ).read_text(encoding="utf-8")
    constraints = (ROOT / "constraints.txt").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/check.yml").read_text(encoding="utf-8")
    workflow_files = [
        *sorted((ROOT / ".github/workflows").glob("*.yml")),
        *sorted((ROOT / ".github/workflows").glob("*.yaml")),
    ]

    numeric_bounds_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", numeric_bounds_plan)
    numeric_bounds_work = markdown_section(numeric_bounds_plan, "Work Completed")
    numeric_bounds_verification = markdown_section(
        numeric_bounds_plan, "Verification Completed"
    )
    constraints_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", constraints_plan)
    constraints_work = markdown_section(constraints_plan, "Work Completed")
    constraints_verification = markdown_section(
        constraints_plan, "Verification Completed"
    )
    checkout_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", checkout_plan)
    checkout_work = markdown_section(checkout_plan, "Work Completed")
    checkout_verification = markdown_section(
        checkout_plan, "Verification Completed"
    )
    parser_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", parser_plan)
    parser_work = markdown_section(parser_plan, "Work Completed")
    parser_verification = markdown_section(parser_plan, "Verification Completed")
    memcache_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", memcache_plan)
    memcache_verification = markdown_section(memcache_plan, "Verification Completed")
    memcache_verification_text = " ".join(memcache_verification.split())
    response_limit_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", response_limit_plan)
    response_limit_verification = markdown_section(response_limit_plan, "Verification Completed")
    response_limit_verification_text = " ".join(response_limit_verification.split())
    short_read_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", short_read_plan)
    short_read_verification = markdown_section(short_read_plan, "Verification Completed")
    short_read_verification_text = " ".join(short_read_verification.split())
    response_closure_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", response_closure_plan
    )
    response_closure_verification = markdown_section(
        response_closure_plan, "Verification Completed"
    )
    response_closure_verification_text = " ".join(
        response_closure_verification.split()
    )
    landing_response_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", landing_response_plan
    )
    landing_response_verification = markdown_section(
        landing_response_plan, "Verification Completed"
    )
    landing_response_verification_text = " ".join(
        landing_response_verification.split()
    )
    smtp_tls_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", smtp_tls_plan)
    smtp_tls_work = markdown_section(smtp_tls_plan, "Work Completed")
    smtp_tls_verification = markdown_section(smtp_tls_plan, "Verification Completed")
    smtp_tls_verification_text = " ".join(smtp_tls_verification.split())
    expected_constraints = """# Reviewed CI resolution for Python 3.12.
html5lib==1.1
mechanize==0.4.10
python-memcached==1.62
six==1.17.0
webencodings==0.5.1
"""
    expected_requirements = """mechanize>=0.4.10,<0.5
python-memcached>=1.59,<2
"""
    constrained_install = (
        "python -m pip install --requirement requirements.txt "
        "--constraint constraints.txt"
    )
    dependency_cache = """          cache-dependency-path: |
            requirements.txt
            constraints.txt"""
    checkout_action = (
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10"
    )
    checkout_blocks = re.findall(
        rf"(?m)^(?P<indent> *)- +uses: +{re.escape(checkout_action)}[^\n]*\n"
        rf"(?P=indent)  with:\n"
        rf"(?P=indent)    persist-credentials: +false *$",
        workflow,
    )
    checkout_actions = re.findall(
        r"(?m)^\s*-\s+uses:\s+actions/checkout@",
        workflow,
    )

    checks = [
        ("status: completed" in hosted_validation_plan and "make check" in hosted_validation_plan,
         "hosted Python validation plan must be marked completed"),
        ("permissions:\n  contents: read" in workflow
         and "cancel-in-progress: true" in workflow
         and "runs-on: ubuntu-24.04" in workflow
         and "timeout-minutes: 10" in workflow
         and checkout_action in workflow
         and "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405" in workflow
         and 'python-version: "3.12"' in workflow
         and workflow.count(dependency_cache) == 1
         and workflow.count(constrained_install) == 1
         and "python -m pip check" in workflow
         and "run: make check" in workflow,
         "Check workflow must stay pinned, read-only, bounded, and dependency-aware"),
        (len(workflow_files) == 1
         and workflow.count("permissions:") == 1
         and workflow.count("contents: read") == 1
         and not re.search(r"(?m)^\s*[A-Za-z-]+:\s*write\s*$", workflow)
         and len(checkout_actions) == 1
         and workflow.count(checkout_action) == 1
         and len(checkout_blocks) == 1
         and workflow.count("persist-credentials: false") == 1
         and "persist-credentials: true" not in workflow,
         "Check workflow must keep one read-only permission block and one "
         "pinned, credential-free checkout"),
        (checkout_status == ["completed"]
         and bool(checkout_work)
         and "make check" in checkout_verification,
         "checkout credential plan must record one completed status, completed "
         "work, and make check verification"),
        ('if tag == "div":' in main_source
         and "if self._action_depth:" in main_source
         and "self._action_depth += 1" in main_source
         and 'elif "action" in attributes.get("class", "").split():' in main_source,
         "ActionParser must balance ordinary nested div depth inside actions"),
        ("test_extract_actions_keeps_action_open_across_nested_div" in test_main
         and "test_extract_actions_collects_nested_markup_inside_first_span" in test_main
         and "Metadata" in test_main
         and "Expected nested value" in test_main,
         "tests must cover nested action containers and inline span markup"),
        ("nested action parser depth" in readme.lower()
         and "nested action parser depth" in vision.lower()
         and "nested action parser depth" in security.lower()
         and "nested action parser depth" in changes.lower(),
         "docs must record nested action parser depth protection"),
        (parser_status == ["completed"] and bool(parser_work),
         "nested action parser plan must record one completed status and completed work"),
        (bool(parser_verification)
         and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", parser_verification)
         and all(evidence in parser_verification for evidence in [
             "make lint",
             "make test",
             "make build",
             "make check",
             "test_extract_actions_keeps_action_open_across_nested_div",
             "test_extract_actions_collects_nested_markup_inside_first_span",
             "git diff --check",
         ]),
         "nested action parser plan must preserve completed verification evidence"),
        (requirements == expected_requirements,
         "requirements.txt must preserve the reviewed direct compatibility ranges"),
        (constraints == expected_constraints,
         "constraints.txt must match the reviewed Python 3.12 graph exactly"),
        ("constraints.txt" in readme
         and "constraints.txt" in security
         and "constraints" in changes.lower()
         and "do not authenticate" in readme.lower()
         and "not artifact authentication" in security.lower(),
         "docs must describe constrained resolution and its hash boundary"),
        (constraints_status == ["completed"] and bool(constraints_work),
         "dependency constraints plan must record one completed status and completed work"),
        (bool(constraints_verification)
         and not re.search(
             r"(?i)\b(?:pending|todo|tbd|not run|will be recorded)\b",
             constraints_verification,
         )
         and all(evidence in constraints_verification for evidence in [
             "Official PyPI metadata",
             "Python 3.12 resolver dry run",
             "mechanize 0.4.10",
             "python-memcached 1.62",
             "html5lib 1.1",
             "six 1.17.0",
             "webencodings 0.5.1",
             "63e91f82cbebd09e26770d820c942f7f03814c93",
             "27437261487",
             "27437266988",
             "27437265086",
             "all five exact-head checks successful",
             "zero open PR-scoped",
         ]),
         "dependency constraints plan must preserve finished exact-head verification evidence"),
        (makefile == EXPECTED_MAKEFILE,
         "Makefile must exactly preserve rooted lint, test, build, check, clean, and fmt gates"),
        ("make -f /path/to/mechenz/Makefile check" in readme,
         "README must document location-independent Makefile invocation"),
        ("status: completed" in location_independent_make_plan
         and "root and external-directory" in location_independent_make_plan
         and "eight isolated hostile mutations" in location_independent_make_plan,
         "location-independent Make plan must record completed root, external, and mutation verification"),
        ("SCRAPE_REQUEST_TIMEOUT = 15" in main_source
         and main_source.count("timeout=SCRAPE_REQUEST_TIMEOUT") == 3
         and "submission_request = browser.click()" in main_source
         and "browser.open(submission_request, timeout=SCRAPE_REQUEST_TIMEOUT)" in main_source
         and "browser.submit()" not in main_source,
         "fetch_actions must apply one finite timeout to all three mechanize opens"),
        ("test_fetch_actions_bounds_every_network_open" in test_main
         and "test_fetch_actions_uses_bounded_submission_response_without_result_url" in test_main
         and test_main.count("main.SCRAPE_REQUEST_TIMEOUT") >= 3
         and 'return "submitted-request"' in test_main
         and 'self.assertEqual(browser.form, {"q": "value"})' in test_main
         and "self.assertTrue(browser.robots)" in test_main,
         "offline tests must verify bounded opens while preserving browser configuration"),
        ("landing_response = browser.open(settings.site, timeout=SCRAPE_REQUEST_TIMEOUT)" in main_source
         and "submission_request = browser.click()" in main_source
         and "landing_response.close()" in main_source
         and main_source.find("landing_response.close()")
             < main_source.find("browser.open(submission_request, timeout=SCRAPE_REQUEST_TIMEOUT)"),
         "fetch_actions must close the landing response before opening the submitted request"),
        ("test_fetch_actions_closes_landing_response_when_form_selection_fails" in test_main
         and test_main.count("browser.landing_response.close_calls, 1") == 2
         and "self.assertEqual(len(browser.opens), 1)" in test_main,
         "tests must cover landing response closure on success and form-selection failure"),
        ("Landing response closure releases" in readme
         and "Landing-page responses should close" in security
         and "Keep landing response closure deterministic" in vision
         and "Closed landing-page responses" in changes,
         "project guidance must document deterministic landing response closure"),
        ("def _normalize_memcache_servers(value) -> list[str]:" in main_source
         and "candidates = [value] if isinstance(value, str) else value" in main_source
         and "not isinstance(candidates, Sequence)" in main_source
         and "isinstance(candidates, (bytes, bytearray))" in main_source
         and "not server.strip()" in main_source
         and "return [server.strip() for server in candidates]" in main_source
         and main_source.find("servers = _normalize_memcache_servers(configured_servers)")
             < main_source.find('memcache = importlib.import_module("memcache")'),
         "create_cache must normalize and validate memcache endpoints before client import"),
        ("test_create_cache_treats_single_server_string_as_one_endpoint" in test_main
         and "test_create_cache_normalizes_server_sequence" in test_main
         and "test_create_cache_uses_nonblank_environment_override" in test_main
         and "test_create_cache_ignores_blank_environment_override" in test_main
         and "test_create_cache_rejects_blank_or_unsupported_server_settings" in test_main,
         "tests must cover memcache endpoint normalization and rejection"),
        ("memcache server normalization" in readme.lower()
         and "memcache server normalization" in vision.lower()
         and "memcache server normalization" in security.lower()
         and "memcache server normalization" in changes.lower(),
         "project guidance must document memcache server normalization"),
        (memcache_status == ["completed"]
         and "all four Make gates passed" in memcache_verification_text
         and "external directory" in memcache_verification_text
         and "Six isolated hostile mutations were rejected" in memcache_verification_text
         and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", memcache_verification),
         "memcache server normalization plan must record completed status and actual verification"),
        ("status: completed" in scrape_timeout_plan
         and "hostile mutations" in scrape_timeout_plan
         and "27 offline tests" in scrape_timeout_plan,
         "scrape request timeout plan must record completed test and mutation evidence"),
        ("scrape request timeout" in readme.lower()
         and "scrape request timeout" in vision.lower()
         and "scrape request timeout" in security.lower()
         and "scrape request timeout" in changes.lower(),
         "README, VISION, SECURITY, and CHANGES must document bounded scrape requests"),
        ("MAX_SCRAPE_RESPONSE_BYTES = 1024 * 1024" in main_source
         and "def _read_bounded_response(response) -> bytes:" in main_source
         and "remaining = MAX_SCRAPE_RESPONSE_BYTES + 1" in main_source
         and "while remaining > 0:" in main_source
         and "chunk = response.read(remaining)" in main_source
         and "if not chunk:" in main_source
         and "remaining -= len(chunk)" in main_source
         and 'body = b"".join(chunks)' in main_source
         and "len(body) > MAX_SCRAPE_RESPONSE_BYTES" in main_source,
         "scrape responses must accumulate short reads within one byte past a fixed 1 MiB limit"),
        (main_source.find("response_body = _read_bounded_response(response)") >= 0
         and main_source.find("return extract_actions(response_body, encoding=settings.encoding)")
             > main_source.find("response_body = _read_bounded_response(response)"),
         "fetch_actions must bound the selected response before decoding and parsing"),
        ("if settings.form_url:\n        response.close()\n        response = browser.open(" in main_source
         and "try:\n        response_body = _read_bounded_response(response)\n    finally:\n        response.close()" in main_source,
         "fetch_actions must close superseded and selected scrape responses"),
        ("test_read_bounded_response_accepts_exact_limit" in test_main
         and "test_read_bounded_response_rejects_one_byte_over_limit" in test_main
         and "test_read_bounded_response_assembles_short_reads" in test_main
         and "test_read_bounded_response_rejects_oversize_across_short_reads" in test_main
         and "max_chunk_size=4096" in test_main
         and "response.read_sizes" in test_main
         and "MAX_SCRAPE_RESPONSE_BYTES + 1" in test_main,
         "offline tests must cover response boundaries, short reads, and the total read budget"),
        ("test_fetch_actions_closes_selected_response_when_read_fails" in test_main
         and "browser.submission_response.close_calls" in test_main
         and "browser.response.close_calls" in test_main
         and "raise self.read_error" in test_main,
         "offline tests must cover direct, replaced, and exceptional response closure"),
        ("scrape response body limit" in readme.lower()
         and "Keep the scrape response body limit ahead of decoding and parser execution." in readme
         and "scrape response body limit" in vision.lower()
         and "scrape response body limit" in security.lower()
         and "scrape response body limit" in changes.lower(),
         "project guidance must document the scrape response body limit"),
        ("scrape short-read handling" in readme.lower()
         and "scrape short-read handling" in vision.lower()
         and "scrape short-read handling" in security.lower()
         and "scrape short-read handling" in changes.lower(),
         "project guidance must document scrape short-read handling"),
        (short_read_status == ["completed"]
         and "36 offline tests passed" in short_read_verification_text
         and "All four Make gates passed" in short_read_verification_text
         and "external directory" in short_read_verification_text
         and "Seven isolated hostile mutations were rejected" in short_read_verification_text
         and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", short_read_verification),
         "scrape short-read handling plan must record completed status and actual verification"),
        ("scrape response closure" in readme.lower()
         and "scrape response closure" in vision.lower()
         and "scrape response closure" in security.lower()
         and "scrape response closure" in changes.lower(),
         "project guidance must document deterministic scrape response closure"),
        (response_closure_status == ["completed"]
         and "37 offline tests passed" in response_closure_verification_text
         and "All four Make gates passed" in response_closure_verification_text
         and "external directory" in response_closure_verification_text
         and "Six isolated hostile mutations were rejected" in response_closure_verification_text
         and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", response_closure_verification),
         "scrape response closure plan must record completed status and actual verification"),
        (landing_response_status == ["completed"]
         and "All 38 offline tests passed" in landing_response_verification_text
         and "external directory" in landing_response_verification_text
         and "Six isolated hostile mutations were rejected" in landing_response_verification_text
         and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", landing_response_verification),
         "landing response closure plan must record completed status and actual verification"),
        (response_limit_status == ["completed"]
         and "All four Make gates passed" in response_limit_verification_text
         and "external directory" in response_limit_verification_text
         and "Seven isolated hostile mutations were rejected" in response_limit_verification_text
         and "34 offline tests passed" in response_limit_verification_text
         and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", response_limit_verification),
         "scrape response body limit plan must record completed status and actual verification"),
        ("make lint" in readme and "make test" in readme and "make build" in readme,
         "README must document standard Make gates"),
        ("make lint" in vision and "make test" in vision and "make build" in vision,
         "VISION must document standard Make gates"),
        ("make lint" in changes and "make test" in changes and "make build" in changes,
         "CHANGES must record standard Make gates"),
        ("status: completed" in make_gates_plan,
         "Make gate targets plan must be marked completed"),
        ("empty required settings" in main_source and "required_values" in main_source,
         "load_scrape_settings must reject blank required settings"),
        ("test_load_scrape_settings_rejects_blank_required_values" in test_main,
         "tests must cover blank scrape settings validation"),
        ("scrape settings validation" in readme.lower()
         and "scrape settings validation" in vision.lower()
         and "scrape settings validation" in security.lower(),
         "docs must mention scrape settings validation"),
        ("scrape settings validation" in changes.lower(),
         "CHANGES must record scrape settings validation"),
        ("status: completed" in settings_plan,
         "scrape settings validation plan must be marked completed"),
        ("_valid_http_url" in main_source and "invalid scrape settings" in main_source,
         "load_scrape_settings must validate scrape URL schemes"),
        ("test_load_scrape_settings_rejects_invalid_scrape_urls" in test_main
         and "file:///tmp/private.html" in test_main
         and "not-a-url" in test_main,
         "tests must cover invalid scrape URL validation"),
        ("scrape url validation" in readme.lower()
         and "scrape url validation" in vision.lower()
         and "scrape url validation" in security.lower(),
         "docs must mention scrape URL validation"),
        ("scrape url validation" in changes.lower(),
         "CHANGES must record scrape URL validation"),
        ("status: completed" in url_plan,
         "scrape URL validation plan must be marked completed"),
        ("_parse_encoding_setting" in main_source
         and "codecs.lookup(encoding)" in main_source
         and "test_load_scrape_settings_rejects_invalid_encoding" in test_main
         and "not-a-codec" in test_main,
         "load_scrape_settings must validate configured scrape encodings"),
        ("scrape encoding validation" in readme.lower()
         and "scrape encoding validation" in vision.lower()
         and "scrape encoding validation" in security.lower(),
         "docs must mention scrape encoding validation"),
        ("scrape encoding validation" in changes.lower(),
         "CHANGES must record scrape encoding validation"),
        ("status: completed" in encoding_plan,
         "scrape encoding validation plan must be marked completed"),
        ("_parse_int_setting" in mail_source and "_parse_float_setting" in mail_source,
         "RoyalMail must sanitize numeric SMTP setting parsing"),
        ("maximum=65535" in mail_source
         and "maximum=300.0" in mail_source
         and "math.isfinite(parsed)" in mail_source,
         "RoyalMail must bound SMTP ports and require finite bounded timeouts"),
        ("invalid SMTP_PORT" in test_mail and "invalid SMTP_TIMEOUT" in test_mail,
         "tests must cover invalid numeric SMTP settings"),
        ("test_load_mail_settings_rejects_port_outside_tcp_range" in test_mail
         and "test_load_mail_settings_rejects_unbounded_timeout" in test_mail
         and "test_load_mail_settings_accepts_numeric_upper_bounds" in test_mail
         and '"65536"' in test_mail
         and '"nan", "inf", "301"' in test_mail,
         "tests must cover SMTP port and timeout upper bounds"),
        ("smtp numeric setting validation" in readme.lower()
         and "smtp numeric setting validation" in vision.lower()
         and "smtp numeric setting validation" in security.lower(),
         "docs must mention SMTP numeric setting validation"),
        ("smtp numeric setting validation" in changes.lower(),
         "CHANGES must record SMTP numeric setting validation"),
        ("status: completed" in mail_plan,
         "SMTP numeric setting validation plan must be marked completed"),
        (numeric_bounds_status == ["completed"] and bool(numeric_bounds_work),
         "SMTP numeric bounds plan must record one completed status and completed work"),
        (bool(numeric_bounds_verification)
         and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", numeric_bounds_verification),
         "SMTP numeric bounds plan must record finished verification without pending markers"),
        (all(evidence in numeric_bounds_verification for evidence in [
            "make check",
            "make lint",
            "make test",
            "make build",
            "python3 -m py_compile scripts/check-baseline.py",
            "git diff --check",
            "27287526596",
            "27402325084",
            "d4555441451142239ee680c722adddd9d98f7f0a",
            "maximum=65535",
            "maximum=300.0",
            "math.isfinite(parsed)",
            "test_load_mail_settings_rejects_port_outside_tcp_range",
            "test_load_mail_settings_rejects_unbounded_timeout",
         ]),
         "SMTP numeric bounds plan must preserve exact completed verification evidence"),
        ("str(address).strip()" in mail_source and "if not recipients" in mail_source,
         "RoyalMail must normalize and reject blank SMTP recipients"),
        ("test_send_mail_normalizes_recipients" in test_mail
         and "test_send_mail_rejects_blank_recipients" in test_mail,
         "tests must cover SMTP recipient normalization"),
        ("smtp recipient normalization" in readme.lower()
         and "smtp recipient normalization" in vision.lower()
         and "smtp recipient normalization" in security.lower(),
         "docs must mention SMTP recipient normalization"),
        ("smtp recipient normalization" in changes.lower(),
         "CHANGES must record SMTP recipient normalization"),
        ("status: completed" in recipient_plan,
         "SMTP recipient normalization plan must be marked completed"),
        ("_parse_bool_setting" in main_source
         and "invalid respect_robots" in test_main
         and "invalid MECHENZ_IGNORE_ROBOTS" in test_main,
         "tests must cover robot setting validation"),
        ("robot setting validation" in readme.lower()
         and "robot setting validation" in vision.lower()
         and "robot setting validation" in security.lower(),
         "docs must mention robot setting validation"),
        ("robot setting validation" in changes.lower(),
         "CHANGES must record robot setting validation"),
        ("status: completed" in robot_plan,
         "robot setting validation plan must be marked completed"),
        ("_validate_header_value" in mail_source
         and '_validate_header_value("SMTP_LOGIN", settings.login)' in mail_source
         and '_validate_header_value("SMTP_SUBJECT", subject)' in mail_source
         and '_validate_header_value("SMTP_RECIPIENT", recipient)' in mail_source
         and 'raise ValueError(f"invalid {name}")' in mail_source,
         "RoyalMail must reject CRLF in SMTP header values"),
        ("test_send_mail_rejects_header_newlines_before_smtp" in test_mail
         and "invalid SMTP_SUBJECT" in test_mail
         and "invalid SMTP_RECIPIENT" in test_mail
         and "invalid SMTP_LOGIN" in test_mail,
         "tests must cover SMTP header validation"),
        ("smtp header validation" in readme.lower()
         and "smtp header validation" in vision.lower()
         and "smtp header validation" in security.lower(),
         "docs must mention SMTP header validation"),
        ("smtp header validation" in changes.lower(),
         "CHANGES must record SMTP header validation"),
        ("status: completed" in header_plan,
         "SMTP header validation plan must be marked completed"),
        ("import ssl" in mail_source
         and "tls_context = ssl.create_default_context()" in mail_source
         and "server.starttls(context=tls_context)" in mail_source
         and mail_source.find("tls_context = ssl.create_default_context()")
             < mail_source.find("server = smtp_factory(")
         and mail_source.find("server.starttls(context=tls_context)")
             < mail_source.find("server.login(settings.login, settings.password)"),
         "RoyalMail must create and apply a verifying STARTTLS context before authentication"),
        ("test_send_mail_passes_default_context_to_starttls_before_login" in test_mail
         and 'mock.patch.object(' in test_mail
         and 'RoyalMail.ssl,' in test_mail
         and '"create_default_context"' in test_mail
         and 'return_value=tls_context' in test_mail
         and 'context_factory.assert_called_once_with()' in test_mail
         and 'self.assertIn(("starttls", tls_context), smtp.calls)' in test_mail,
         "tests must preserve exact STARTTLS context creation, identity, and ordering"),
        ("smtp starttls certificate verification" in readme.lower()
         and "smtp starttls certificate verification" in vision.lower()
         and "smtp starttls certificate verification" in security.lower(),
         "project guidance must document SMTP STARTTLS certificate verification"),
        ("smtp starttls certificate verification" in changes.lower(),
         "CHANGES must record SMTP STARTTLS certificate verification"),
        ("# SMTP STARTTLS Certificate Verification" in smtp_tls_plan,
         "SMTP STARTTLS verification plan must remain tracked"),
        (smtp_tls_status == ["completed"] and bool(smtp_tls_work),
         "SMTP STARTTLS verification plan must record completed status and work"),
        (all(evidence in smtp_tls_verification_text for evidence in [
            "39 offline tests",
            "All five repository Make gates passed",
            "external directory",
            "Seven isolated hostile mutations were rejected",
            "git diff --check",
            "No live SMTP service was contacted",
         ])
         and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", smtp_tls_verification),
         "SMTP STARTTLS verification plan must preserve completed verification evidence"),
    ]
    for passed, message in checks:
        if not passed:
            print(message, file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
