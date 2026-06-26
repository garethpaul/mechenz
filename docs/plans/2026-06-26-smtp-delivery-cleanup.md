# SMTP Delivery Cleanup

status: completed

## Problem

After `sendmail()` accepted a message, `RoyalMail.send_mail()` called
`server.close()` without a cleanup guard. A transport error during that final
close escaped as a delivery failure, preventing the caller from updating its
change cache and causing the accepted message to be sent again on the next run.

## Requirements

1. Preserve all SMTP setup, STARTTLS, authentication, and recipient-refusal
   failures.
2. Preserve the primary error when cleanup also fails.
3. Ignore only expected transport/SMTP close errors after successful delivery.
4. Add focused regression, static contract, mutation, and documentation evidence.
5. Do not contact a live SMTP server or change credentials, recipients, or
   message content.

## Work Completed

- Guarded successful-delivery cleanup against `OSError` and `SMTPException`.
- Added a fake SMTP regression proving the message is accepted and cleanup is
  attempted without surfacing the close error.
- Updated the hostile mutation suite and project guidance.

## Verification Completed

- All 53 offline tests passed on supported local Python versions.
- eight isolated hostile mutations were rejected, including removal of the
  successful-delivery cleanup guard.
- `make check` passed from the repository root and an external working directory.
- Syntax compilation, `git diff --check`, strict Git validation,
  generated-artifact checks, and secret/conflict scans passed without live SMTP.
