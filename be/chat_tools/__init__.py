"""Chat agent with tool-based access.

This module implements a PydanticAI agent that accesses data on-demand
through tool calls to service layer functions.
"""

from .agent import run_tools_chat, tools_agent

__all__ = ["tools_agent", "run_tools_chat"]
