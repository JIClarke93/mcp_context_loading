"""PydanticAI agent with tool-based data access.

This module implements an agent that uses tool calls to access service
layer functions on-demand, rather than receiving pre-loaded context.
"""

from pydantic_ai import Agent

from .deps import ToolsDeps
from .tools import (
    get_category_by_id_tool,
    get_order_by_id_tool,
    get_product_by_id_tool,
    get_review_by_id_tool,
    get_user_by_id_tool,
    list_categories_tool,
    list_orders_tool,
    list_products_tool,
    list_reviews_tool,
    list_users_tool,
)

tools_agent = Agent(
    "anthropic:claude-3-5-sonnet-20241022",
    deps_type=ToolsDeps,
    system_prompt=(
        "You are a helpful e-commerce assistant with access to database tools.\n\n"
        "You can access information about:\n"
        "- Users: customer accounts and profiles\n"
        "- Products: available items for purchase\n"
        "- Categories: product categorization hierarchy\n"
        "- Orders: customer order history\n"
        "- Reviews: product reviews and ratings\n\n"
        "Use the available tools to retrieve specific data on-demand to answer user questions.\n"
        "Be efficient with tool calls - only request the data you need.\n"
        "If you cannot find information, say so clearly."
    ),
)

# Register all tools with the agent
tools_agent.tool(list_users_tool)
tools_agent.tool(get_user_by_id_tool)
tools_agent.tool(list_products_tool)
tools_agent.tool(get_product_by_id_tool)
tools_agent.tool(list_categories_tool)
tools_agent.tool(get_category_by_id_tool)
tools_agent.tool(list_orders_tool)
tools_agent.tool(get_order_by_id_tool)
tools_agent.tool(list_reviews_tool)
tools_agent.tool(get_review_by_id_tool)


async def run_tools_chat(message: str, deps: ToolsDeps) -> str:
    """Run a chat interaction with the tools-based agent.

    Args:
        message: User's message/question.
        deps: Tools dependencies with database session.

    Returns:
        Agent's response as a string.
    """
    result = await tools_agent.run(message, deps=deps)
    return result.data
