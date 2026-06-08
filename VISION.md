## Mechenz Vision

Mechenz is a Python 2-era scraper and email notification script. It uses
mechanize, BeautifulSoup, memcache, and Gmail SMTP to detect changed scraped
data and send a notification email.

The repository is useful as a small automation sample for polling a form-backed
site, caching previous results, and notifying via email.

The goal is to keep the automation understandable while making credentials,
scraping behavior, and email delivery safe.

The current focus is:

Priority:

- Preserve the scrape, cache, compare, and email-notification flow
- Keep site/form settings and SMTP credentials out of git
- Avoid ignoring robots or site terms without explicit documentation
- Maintain security policy for the sample

Next priorities:

- Add README setup for local settings and memcache
- Move credentials into environment or ignored local config
- Port to supported Python and maintained scraping/email libraries
- Add tests around parsing, cache comparison, and email body generation

Contribution rules:

- One PR = one focused scraper, cache, mail, or documentation change.
- Do not commit Gmail credentials, target-site secrets, or scraped private data.
- Verify behavior with fixtures before live scraping.
- Document target-site access assumptions.

## Security And Privacy

Email credentials and scraped data are sensitive. Credentials must stay in local
configuration, and scraped content should not be committed unless it is safe as
a fixture.

## What We Will Not Merge (For Now)

- SMTP passwords or account credentials
- Scraped private data
- Live-only tests as the default path
- Scraping changes without access and rate-limit notes
