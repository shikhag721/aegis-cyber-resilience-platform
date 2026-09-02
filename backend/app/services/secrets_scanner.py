"""Lightweight, regex-based secret scanner (Section 14).

Purely detective: reads text and reports matches with the sensitive span
redacted in the returned snippet - never generates, stores, or reproduces
a real credential. Patterns mirror the well-known, public rule sets used
by tools like gitleaks/TruffleHog (format-detection only, no live
validation against any provider's API - this project never makes an
outbound call to verify whether a matched key is "real").
"""
import re
from dataclasses import dataclass

from app.models.appsec import SecretType

_PATTERNS: list[tuple[SecretType, re.Pattern, str]] = [
    (SecretType.AWS_ACCESS_KEY, re.compile(r"AKIA[0-9A-Z]{16}"), "high"),
    (
        SecretType.SLACK_TOKEN,
        re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
        "high",
    ),
    (
        SecretType.PRIVATE_KEY,
        re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "critical",
    ),
    (
        SecretType.GENERIC_API_KEY,
        re.compile(r"(?i)api[_-]?key[\"']?\s*[:=]\s*[\"']([A-Za-z0-9_\-]{20,})[\"']"),
        "medium",
    ),
    (
        SecretType.PASSWORD_ASSIGNMENT,
        re.compile(r"(?i)password[\"']?\s*[:=]\s*[\"']([^\"'\s]{8,})[\"']"),
        "medium",
    ),
]


@dataclass
class SecretMatch:
    secret_type: SecretType
    severity: str
    line_number: int
    redacted_snippet: str


def _redact(line: str, match: re.Match) -> str:
    start, end = match.span()
    matched = line[start:end]
    if len(matched) <= 8:
        redacted = "*" * len(matched)
    else:
        redacted = matched[:4] + "*" * (len(matched) - 8) + matched[-4:]
    return line[:start] + redacted + line[end:]


def scan_text(text: str) -> list[SecretMatch]:
    """Scans multi-line text and returns every match found, with the
    matched credential span redacted (never the raw secret) in the
    returned snippet.
    """
    matches: list[SecretMatch] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for secret_type, pattern, severity in _PATTERNS:
            found = pattern.search(line)
            if found:
                matches.append(
                    SecretMatch(
                        secret_type=secret_type,
                        severity=severity,
                        line_number=line_number,
                        redacted_snippet=_redact(line, found)[:120],
                    )
                )
    return matches
