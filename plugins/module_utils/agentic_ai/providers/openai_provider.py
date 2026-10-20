import json

from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.providers.base import (
    BaseLLMProvider
)

from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.prompts import (
    SYSTEM_PROMPT
)


TOOLS = [
    {
        "type": "function",
        "name": "check_dns",
        "description": (
            "Resolve a hostname and determine whether DNS resolution "
            "is successful."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string"
                }
            },
            "required": ["host"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "check_connectivity",
        "description": (
            "Check TCP connectivity to a host and port."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string"
                },
                "port": {
                    "type": "integer"
                }
            },
            "required": ["host"],
            "additionalProperties": False
        }
    }
]


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI implementation of the PowerVC diagnostic LLM provider.
    """

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def get_next_action(self, context):
        """
        Ask OpenAI to determine the next diagnostic action.
        """

        response = self.client.responses.create(
            model=self.model,
            instructions=SYSTEM_PROMPT,
            input=json.dumps(context),
            tools=TOOLS
        )

        for item in response.output:

            if item.type == "function_call":

                return {
                    "type": "tool_call",
                    "tool_name": item.name,
                    "arguments": json.loads(item.arguments)
                }

        return {
            "type": "final",
            "diagnosis": self._parse_final_response(
                response.output_text,
                context
            )
        }

    def _parse_final_response(self, output_text, context):
        """
        Convert the LLM final response into our internal format.

        Initially preserve the raw response. Structured output
        will be added next.
        """

        return {
            "root_cause": output_text,
            "evidence": context.get("tool_results", []),
            "recommended_action": output_text,
            "retry_recommended": False
        }
