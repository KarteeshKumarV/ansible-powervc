class BaseLLMProvider:
    """
    Base interface for LLM providers.
    """

    def get_next_action(self, context):
        """
        Determine the next diagnostic action.

        Args:
            context (dict): Error context and previous tool results.

        Returns:
            dict: Either a tool_call or final diagnosis.
        """

        raise NotImplementedError(
            "LLM providers must implement get_next_action"
        )
