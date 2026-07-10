import re

# Common patterns for API keys, passwords, connection strings, etc.
SECRET_PATTERNS = {
    "connection_string": re.compile(
        r"[a-zA-Z0-9\+\-\.]+://[^/\s:]+:[^/\s@]+@[^/\s]+(?:/[^/\s]*)?", re.IGNORECASE
    ),
    "github_token": re.compile(
        r"(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,255}"
    ),
    "aws_access_key": re.compile(
        r"\b(?:AKIA|ASCA|ACCA|ASIA)[A-Z0-9]{16}\b"
    ),
    "aws_secret_key": re.compile(
        r"\b[A-Za-z0-9/+=]{40}\b"
    ),
    "generic_api_key": re.compile(
        r"(?:api_key|apikey|secret|password|passwd|private_key|privatekey)\s*[:=]\s*['\"]([a-zA-Z0-9_\-\.\+=]{8,})['\"]",
        re.IGNORECASE,
    ),
    "bearer_token": re.compile(
        r"bearer\s+([a-zA-Z0-9_\-\.\+=]{10,})", re.IGNORECASE
    ),
}


def scan_and_redact(text: str) -> tuple[str, bool]:
    """
    Scans text for common secret patterns and redacts them.
    Returns:
        tuple[str, bool]: The redacted text, and a boolean indicating if any secrets were found.
    """
    if not text:
        return text, False

    redacted_text = text
    secrets_found = False

    # Redact connection strings first
    matches = SECRET_PATTERNS["connection_string"].findall(redacted_text)
    if matches:
        secrets_found = True
        # Replace password section with <REDACTED>
        for match in matches:
            # We want to replace password with <REDACTED>
            parts = re.split(r"([^/\s:]+:[^/\s@]+)@", match)
            if len(parts) >= 3:
                auth_part = parts[1]
                user_pass = auth_part.split(":", 1)
                if len(user_pass) == 2:
                    redacted_auth = f"{user_pass[0]}:<REDACTED>"
                    redacted_match = match.replace(auth_part, redacted_auth)
                    redacted_text = redacted_text.replace(match, redacted_match)

    # Redact other secrets
    for name, pattern in SECRET_PATTERNS.items():
        if name == "connection_string":
            continue

        def replacer(match):
            nonlocal secrets_found
            secrets_found = True
            # For pattern with group, replace only the group value
            if match.groups():
                full_match = match.group(0)
                group_val = match.group(1)
                return full_match.replace(group_val, "<REDACTED>")
            return "<REDACTED>"

        redacted_text = pattern.sub(replacer, redacted_text)

    return redacted_text, secrets_found
