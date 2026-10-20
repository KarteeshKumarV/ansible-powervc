from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.providers.base import (
    BaseLLMProvider
)


class InternalLLMProvider(BaseLLMProvider):
    """
    Provider for an internal enterprise LLM.

    The actual API integration is intentionally isolated here.
    NovaLink modules and AgentController do not need changes when
    the internal endpoint becomes available.
    """

    def __init__(
        self,
        endpoint=None,
        api_key=None,
        model=None
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model

    def get_next_action(self, context):
        """
        Get the next diagnostic action from the internal LLM.

        This is currently a placeholder until the internal LLM API
        contract, endpoint, authentication, and request format are
        available.
        """

        raise NotImplementedError(
            "Internal LLM provider integration is not configured yet"
        )
