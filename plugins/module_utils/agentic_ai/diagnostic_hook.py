import logging
import re

from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.factory import (
    create_diagnostic_agent
)


LOG = logging.getLogger(__name__)


SENSITIVE_KEYS = [
    "password",
    "passwd",
    "token",
    "auth_token",
    "authorization",
    "api_key",
    "secret",
    "ssh_key",
    "private_key"
]


def sanitize_diagnostic_data(data):
    """
    Remove sensitive values before sending diagnostic data
    to an AI provider.
    """

    if isinstance(data, dict):

        sanitized = {}

        for key, value in data.items():

            if key.lower() in SENSITIVE_KEYS:
                sanitized[key] = "REDACTED"

            else:
                sanitized[key] = sanitize_diagnostic_data(value)

        return sanitized

    if isinstance(data, list):

        return [
            sanitize_diagnostic_data(item)
            for item in data
        ]

    if isinstance(data, str):

        return _sanitize_string(data)

    return data


def _sanitize_string(value):
    """
    Remove common secrets from strings.
    """

    patterns = [
        (
            r"(?i)(password\s*[=:]\s*)[^\s,]+",
            r"\1REDACTED"
        ),
        (
            r"(?i)(token\s*[=:]\s*)[^\s,]+",
            r"\1REDACTED"
        ),
        (
            r"(?i)(api[_-]?key\s*[=:]\s*)[^\s,]+",
            r"\1REDACTED"
        ),
        (
            r"(?i)(authorization\s*[=:]\s*)[^\s,]+",
            r"\1REDACTED"
        )
    ]

    sanitized_value = value

    for pattern, replacement in patterns:

        sanitized_value = re.sub(
            pattern,
            replacement,
            sanitized_value
        )

    return sanitized_value


def build_error_context(
    operation,
    host,
    error_message,
    status_code=None
):
    """
    Build a safe diagnostic context.

    Secrets such as passwords, tokens, API keys, and SSH keys
    must never be included in the diagnostic context.
    """

    context = {
        "module": "novalink",
        "operation": operation,
        "host": host,
        "error": error_message
    }

    if status_code is not None:
        context["status_code"] = status_code

    return sanitize_diagnostic_data(context)


def run_diagnostics(error_context, agent=None):
    """
    Run Agentic AI diagnostics.

    Diagnostic failures must never affect the original
    PowerVC module operation.
    """

    try:

        sanitized_context = sanitize_diagnostic_data(
            error_context
        )

        if agent is None:
            agent = create_diagnostic_agent()

        return agent.diagnose(
            sanitized_context
        )

    except Exception as error:

        LOG.debug(
            "Agentic diagnostic failed: %s",
            str(error)
        )

        return None
