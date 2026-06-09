# SMTP Recipient Normalization Plan

status: completed

## Context

`RoyalMail.send_mail` filters empty recipient strings before creating the SMTP
message. Whitespace-only values are still truthy, so they can pass validation
and open an SMTP connection with an invalid recipient list.

## Objectives

- Strip recipient addresses before building the email message.
- Ignore empty, whitespace-only, and `None` recipient entries.
- Reject all-blank recipient lists before opening an SMTP connection.
- Extend unit tests, docs, and the static baseline for SMTP recipient
  normalization.

## Verification

- `make check`
- `python3 -m unittest discover -s tests`
- `git diff --check`
