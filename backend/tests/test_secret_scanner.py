from app.core.secret_scanner import scan_and_redact


def test_scan_no_secrets():
    text = "This is a normal log line with no secrets."
    redacted, found = scan_and_redact(text)
    assert not found
    assert redacted == text


def test_scan_github_token():
    text = "Here is the token: ghp_abc123XYZabc123XYZabc123XYZabc123XYZabc"
    redacted, found = scan_and_redact(text)
    assert found
    assert "ghp_" not in redacted
    assert "<REDACTED>" in redacted


def test_scan_aws_key():
    text = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE and secret is wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    redacted, found = scan_and_redact(text)
    assert found
    assert "AKIAIOSFODNN7EXAMPLE" not in redacted
    assert "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" not in redacted
    assert "<REDACTED>" in redacted


def test_scan_connection_string():
    text = "Connecting to postgresql://admin:super_secret_password@localhost:5432/db"
    redacted, found = scan_and_redact(text)
    assert found
    assert "super_secret_password" not in redacted
    assert "admin:<REDACTED>" in redacted
    assert "localhost:5432/db" in redacted
