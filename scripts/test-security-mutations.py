#!/usr/bin/env python3
"""Verify security regression tests reject representative guard removals."""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MUTATIONS = (
    (
        "main.py",
        "if _http_origin(_navigation_url(target)) not in allowed_origins:",
        "if False:",
        "navigation origin guard",
    ),
    (
        "main.py",
        "if self._action_depth >= MAX_ACTION_DIV_NESTING:",
        "if False:",
        "action nesting guard",
    ),
    (
        "main.py",
        "return [_normalize_memcache_server(server.strip()) for server in candidates]",
        "return [server.strip() for server in candidates]",
        "memcache endpoint parser",
    ),
    (
        "main.py",
        "if not _valid_header_value(required_values[\"fake_user_agent\"]):",
        "if False:",
        "request header validation",
    ),
    (
        "main.py",
        "        except BaseException:\n            pass\n        raise\n    else:\n        response.close()",
        "        except BaseException:\n            raise\n        raise\n    else:\n        response.close()",
        "HTTP cleanup precedence",
    ),
    (
        "RoyalMail.py",
        "        if refused:\n            raise smtplib.SMTPRecipientsRefused(refused)",
        "        if False:\n            raise smtplib.SMTPRecipientsRefused(refused)",
        "partial SMTP refusal handling",
    ),
    (
        "RoyalMail.py",
        "        except BaseException:\n            pass\n        raise\n    else:\n        server.close()",
        "        except BaseException:\n            raise\n        raise\n    else:\n        server.close()",
        "SMTP cleanup precedence",
    ),
)


def main() -> int:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    with tempfile.TemporaryDirectory(prefix="mechenz-mutations-") as directory:
        base = Path(directory) / "repo"
        shutil.copytree(
            ROOT,
            base,
            ignore=shutil.ignore_patterns(
                ".git",
                ".venv*",
                "__pycache__",
                "*.pyc",
                "*.pyo",
            ),
        )
        for relative_path, original, replacement, label in MUTATIONS:
            mutation = Path(directory) / label.replace(" ", "-")
            shutil.copytree(base, mutation)
            path = mutation / relative_path
            source = path.read_text(encoding="utf-8")
            if source.count(original) != 1:
                print(f"mutation anchor drifted: {label}", file=sys.stderr)
                return 1
            path.write_text(source.replace(original, replacement, 1), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                cwd=mutation,
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if result.returncode == 0:
                print(f"hostile mutation survived: {label}", file=sys.stderr)
                return 1
    print(f"Rejected {len(MUTATIONS)} isolated hostile mutations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
