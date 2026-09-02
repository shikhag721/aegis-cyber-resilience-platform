# ADR 0007: Added `/app-security` route (not in the original nav list)

## Status
Accepted

## Context
Section 13 (Application/API Security) and Section 14 (Secrets and Key
Management) describe real, important findings categories, but the
project's original route list (Section 6) has no dedicated page for
either - the closest fits (`/vulnerabilities`, `/cloud`) are scoped to
CVE-based findings and cloud configuration respectively, and neither is a
good home for OWASP-style application findings (broken auth, injection,
missing rate limiting) or secret-scanning results.

## Decision
Add a new route, `/app-security`, backed by two new models
(`AppSecFinding`, `SecretFinding`) and a small, real regex-based secret
scanner (`app/services/secrets_scanner.py`) - not just static seed data.

## Why
Section 6 explicitly permits this: "The exact routing structure may
evolve if you identify a better secure architecture. Document significant
architectural decisions." Forcing these findings into `/vulnerabilities`
or `/cloud` would misrepresent what they are (a CVE against a piece of
software vs. a design/configuration weakness in Northstar's own
applications vs. a leaked credential) - three different remediation
workflows that deserve to stay visibly distinct.

## The secret scanner specifically
`scan_text()` matches well-known, public secret patterns (AWS access key
ID format, Slack token format, PEM private key headers, generic
`api_key=`/`password=` assignments) - the same category of patterns tools
like gitleaks/TruffleHog use by default. It is purely detection: it reads
text and reports matches with the matched span redacted in output, never
generates, stores, or reproduces a real credential. Tested only against
synthetic, obviously-fake strings (see `tests/test_secrets_scanner.py`).

## Consequences
Documented here rather than silently deviating from the brief's Section 6
list, per Section 44's "if a safe assumption can be made, make it and
document it."
