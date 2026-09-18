class Diagnosis:
    """
    Standard diagnosis returned by the Agentic AI system.
    """

    REQUIRED_FIELDS = [
        "root_cause",
        "evidence",
        "recommended_action",
        "retry_recommended"
    ]

    @classmethod
    def validate(cls, diagnosis):
        """
        Validate the diagnosis returned by an LLM provider.
        """

        if not isinstance(diagnosis, dict):
            return False

        for field in cls.REQUIRED_FIELDS:
            if field not in diagnosis:
                return False

        if not isinstance(
            diagnosis["retry_recommended"],
            bool
        ):
            return False

        if not isinstance(
            diagnosis["evidence"],
            list
        ):
            return False

        return True
