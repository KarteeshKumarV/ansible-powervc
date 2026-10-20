from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.providers.base import (
    BaseLLMProvider
)


class MockDiagnosticProvider(BaseLLMProvider):
    """
    Local provider used for testing and demonstration.

    This simulates an LLM making multi-step diagnostic decisions
    without requiring an external API.
    """

    def get_next_action(self, context):

        error_context = context.get(
            "error_context",
            {}
        )

        tool_results = context.get(
            "tool_results",
            []
        )

        host = error_context.get(
            "host",
            "localhost"
        )

        if not host:
            host = "localhost"

        # First decision: verify DNS.
        if len(tool_results) == 0:

            return {
                "type": "tool_call",
                "tool_name": "check_dns",
                "arguments": {
                    "host": host
                }
            }

        # Second decision: verify connectivity.
        if len(tool_results) == 1:

            return {
                "type": "tool_call",
                "tool_name": "check_connectivity",
                "arguments": {
                    "host": host,
                    "port": 22
                }
            }

        dns_result = tool_results[0].get(
            "result",
            {}
        )

        connectivity_result = tool_results[1].get(
            "result",
            {}
        )

        if not dns_result.get("success"):

            root_cause = (
                "DNS resolution failed for the NovaLink host"
            )

            recommended_action = (
                "Verify the hostname or DNS configuration "
                "for the NovaLink host"
            )

        elif not connectivity_result.get("success"):

            root_cause = (
                "TCP connectivity to the NovaLink host failed"
            )

            recommended_action = (
                "Verify network connectivity, firewall rules, "
                "and SSH service availability"
            )

        else:

            root_cause = (
                "DNS and TCP connectivity checks succeeded"
            )

            recommended_action = (
                "Review the PowerVC API response and NovaLink "
                "service logs"
            )

        return {
            "type": "final",
            "diagnosis": {
                "root_cause": root_cause,
                "evidence": tool_results,
                "recommended_action": recommended_action,
                "retry_recommended": False
            }
        }
