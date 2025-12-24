"""PydanticAI agent with full context loading.

This module implements an agent that receives all database context upfront
in the system prompt, enabling it to answer questions without tool calls.
"""

import json
from typing import Any

from pydantic_ai import Agent

from .deps import ContextDeps

context_agent = Agent(
    "anthropic:claude-3-5-sonnet-20241022",
    deps_type=ContextDeps,
    system_prompt=(
        "You are a helpful e-commerce assistant with access to the complete database.\n\n"
        "You have been provided with comprehensive context about:\n"
        "- Users: customer accounts and profiles\n"
        "- Products: available items for purchase\n"
        "- Categories: product categorization hierarchy\n"
        "- Orders: customer order history\n"
        "- Reviews: product reviews and ratings\n\n"
        "The complete database context is available in your context. "
        "Use this information to answer questions accurately and helpfully.\n"
        "If the information is not in the context, say so clearly."
    ),
)


@context_agent.system_prompt
async def add_context_to_prompt(ctx: ContextDeps) -> str:
    """Add the full context to the system prompt.

    Args:
        ctx: Context dependencies containing pre-loaded data.

    Returns:
        Formatted context as a string for injection into system prompt.
    """
    context_json = json.dumps(ctx.context, indent=2, default=str)

    return f"""
COMPLETE DATABASE CONTEXT:
{context_json}

Use the above context to answer user questions. The data includes:
- {len(ctx.context.get('users', []))} users
- {len(ctx.context.get('products', []))} products
- {len(ctx.context.get('categories', []))} categories
- {len(ctx.context.get('orders', []))} orders
- {len(ctx.context.get('reviews', []))} reviews
"""


async def run_context_chat(message: str, deps: ContextDeps) -> str:
    """Run a chat interaction with the context-loaded agent.

    Args:
        message: User's message/question.
        deps: Context dependencies with pre-loaded data.

    Returns:
        Agent's response as a string.
    """
    result = await context_agent.run(message, deps=deps)
    return result.data
