import json

from ansible_collections.ibm.powervc.plugins.module_utils.agentic_ai.tools import (
    check_dns,
    check_connectivity
)


class ToolRegistry:
    """
    Registry for Agentic AI diagnostic tools.
    """

    def __init__(self):

        self.tools = {
            "check_dns": check_dns,
            "check_connectivity": check_connectivity
        }

    def execute(self, tool_name, arguments):
        """
        Execute an approved tool.
        """

        if tool_name not in self.tools:

            return {
                "success": False,
                "error": "Tool '{0}' is not allowed".format(tool_name)
            }

        try:

            return self.tools[tool_name](**arguments)

        except Exception as error:

            return {
                "success": False,
                "error": str(error)
            }
