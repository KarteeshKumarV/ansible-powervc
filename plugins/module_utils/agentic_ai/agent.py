from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.diagnosis import (
    Diagnosis
)


class AgentController:
    """
    Coordinates LLM decisions and approved diagnostic tools.
    """

    def __init__(self, llm_client, tool_registry, max_iterations=5):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.max_iterations = max_iterations

    def diagnose(self, error_context):

        context = {
            "error_context": error_context,
            "tool_results": []
        }

        for _ in range(self.max_iterations):

            response = self.llm_client.get_next_action(context)

            if response["type"] == "final":

                diagnosis = response.get("diagnosis", {})

                if Diagnosis.validate(diagnosis):
                    return diagnosis

                return self._invalid_diagnosis_response(
                    context
                )

            if response["type"] == "tool_call":

                tool_name = response.get("tool_name")
                arguments = response.get("arguments", {})

                tool_result = self.tool_registry.execute(
                    tool_name,
                    arguments
                )

                context["tool_results"].append({
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": tool_result
                })

                continue

            return self._unsupported_response(context)

        return {
            "root_cause": "Unable to determine root cause",
            "evidence": context["tool_results"],
            "recommended_action": (
                "Maximum diagnostic iterations reached"
            ),
            "retry_recommended": False
        }

    def _invalid_diagnosis_response(self, context):

        return {
            "root_cause": "Unable to validate AI diagnosis",
            "evidence": context["tool_results"],
            "recommended_action": (
                "Review diagnostic information manually"
            ),
            "retry_recommended": False
        }

    def _unsupported_response(self, context):

        return {
            "root_cause": "Unknown",
            "evidence": context["tool_results"],
            "recommended_action": (
                "Agent returned an unsupported response type"
            ),
            "retry_recommended": False
        }
