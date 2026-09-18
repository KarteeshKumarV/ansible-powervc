import os
from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.providers.internal_provider import (
    InternalLLMProvider
)
from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.agent import (
    AgentController
)

from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.tool_registry import (
    ToolRegistry
)

from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.providers.mock_provider import (
    MockDiagnosticProvider
)


def create_diagnostic_agent():
    """
    Create the diagnostic agent based on the configured provider.

    Supported providers:
        - mock
        - openai
        - internal
    """

    provider_name = os.getenv(
        "POWERVC_AI_PROVIDER",
        "mock"
    ).lower()

    if provider_name == "mock":

        provider = MockDiagnosticProvider()

    elif provider_name == "openai":

        provider = _create_openai_provider()

    elif provider_name == "internal":

        provider = _create_internal_provider()

    else:

        raise RuntimeError(
            "Unsupported POWERVC_AI_PROVIDER: {0}".format(
                provider_name
            )
        )

    return AgentController(
        llm_client=provider,
        tool_registry=ToolRegistry(),
        max_iterations=5
    )


def _create_openai_provider():
    """
    Create the OpenAI diagnostic provider.

    This is optional and can remain unused.
    """

    from openai import OpenAI

    from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.providers.openai_provider import (
        OpenAIProvider
    )

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:

        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not configured"
        )

    model = os.getenv(
        "POWERVC_OPENAI_MODEL",
        "gpt-4.1-mini"
    )

    client = OpenAI(
        api_key=api_key
    )

    return OpenAIProvider(
        client=client,
        model=model
    )

def _create_internal_provider():
    """
    Create the internal enterprise LLM provider.
    """

    endpoint = os.getenv(
        "POWERVC_INTERNAL_LLM_ENDPOINT"
    )

    api_key = os.getenv(
        "POWERVC_INTERNAL_LLM_API_KEY"
    )

    model = os.getenv(
        "POWERVC_INTERNAL_LLM_MODEL"
    )

    if not endpoint:
        raise RuntimeError(
            "POWERVC_INTERNAL_LLM_ENDPOINT is not configured"
        )

    return InternalLLMProvider(
        endpoint=endpoint,
        api_key=api_key,
        model=model
    )
