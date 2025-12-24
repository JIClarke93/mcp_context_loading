"""Chat agent with full context loading.

This module implements a PydanticAI agent that receives pre-loaded context
from all business areas upfront.
"""

from .agent import context_agent, run_context_chat

__all__ = ["context_agent", "run_context_chat"]
