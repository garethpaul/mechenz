#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

git -C "$ROOT_DIR" ls-files --error-unmatch settings.py >/dev/null

for name in \
  MECHENZ_NAME \
  MECHENZ_TO_EMAIL \
  MECHENZ_FAKE_USER_AGENT \
  MECHENZ_FAKE_REFERER \
  MECHENZ_SITE_URL \
  MECHENZ_FORM_URL \
  MECHENZ_FORM_JSON \
  MECHENZ_SMTP_LOGIN \
  MECHENZ_SMTP_PASSWORD
do
  grep -q "$name" "$ROOT_DIR/settings.py"
  grep -q "$name" "$ROOT_DIR/README.md"
done

grep -q "Missing required configuration" "$ROOT_DIR/settings.py"

printf '%s\n' "mechenz settings baseline checks passed."
