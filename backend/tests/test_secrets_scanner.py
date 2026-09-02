"""Tests use obviously-fake, synthetic strings only - never a real secret."""
from app.services.secrets_scanner import scan_text


def test_detects_aws_access_key():
    matches = scan_text("aws_key = 'AKIAIOSFODNN7EXAMPLE'")
    assert len(matches) == 1
    assert matches[0].secret_type.value == "aws_access_key"


def test_detects_slack_token():
    # Deliberately not a real-looking token shape (GitHub push protection
    # flags realistic Slack token formats even in test fixtures) - this
    # still matches our own looser detection pattern.
    matches = scan_text("token: xoxb-NOT-A-REAL-TOKEN-PLACEHOLDER-VALUE")
    assert any(m.secret_type.value == "slack_token" for m in matches)


def test_detects_private_key_header():
    text = "-----BEGIN RSA PRIVATE KEY-----\nMIIExampleFakeKeyData\n-----END RSA PRIVATE KEY-----"
    matches = scan_text(text)
    assert any(m.secret_type.value == "private_key" for m in matches)


def test_detects_generic_api_key_assignment():
    matches = scan_text('API_KEY = "example-placeholder-value-not-real-1234567890"')
    assert any(m.secret_type.value == "generic_api_key" for m in matches)


def test_detects_password_assignment():
    matches = scan_text('password = "SuperSecret123!"')
    assert any(m.secret_type.value == "password_assignment" for m in matches)


def test_no_false_positive_on_clean_code():
    matches = scan_text("def add(a, b):\n    return a + b\n\nresult = add(1, 2)\nprint(result)")
    assert matches == []


def test_reports_correct_line_number():
    text = "line one\nline two\napi_key = \"abcdefghijklmnopqrstuvwx\"\nline four"
    matches = scan_text(text)
    assert matches[0].line_number == 3


def test_redacts_the_matched_secret():
    matches = scan_text("aws_key = 'AKIAIOSFODNN7EXAMPLE'")
    assert "AKIAIOSFODNN7EXAMPLE" not in matches[0].redacted_snippet
    assert "*" in matches[0].redacted_snippet


def test_multiple_secrets_in_multiline_text_all_detected():
    text = "\n".join(
        [
            "aws_key = 'AKIAIOSFODNN7EXAMPLE'",
            "password = \"AnotherSecret1\"",
        ]
    )
    matches = scan_text(text)
    assert len(matches) == 2
