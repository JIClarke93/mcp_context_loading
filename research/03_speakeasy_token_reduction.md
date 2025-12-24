# Reducing MCP Token Usage by 100x with Dynamic Toolsets

**Source**: [Speakeasy Blog](https://www.speakeasy.com/blog/how-we-reduced-token-usage-by-100x-dynamic-toolsets-v2)

## Overview

Speakeasy achieved dramatic token reductions (up to 160x) through a dynamic toolset approach that separates tool discovery from schema loading, addressing the fundamental tension between LLM discoverability and context efficiency.

## The Three-Function Approach

Instead of exposing all tools upfront, the system provides three core functions:

1. **search_tools**: Semantic search with embeddings, categorical overviews, and tag filtering
2. **describe_tools**: Lazy loading of detailed schemas only when needed
3. **execute_tool**: Executes discovered tools

## Key Innovation

**Separation of discovery from schema loading** is critical because input schemas often represent 60-80% of token usage in static toolsets. This lazy retrieval pattern prevents unnecessary context consumption.

## Benchmarking Results

Testing across configurations with 40-400 tools:

### Token Reduction
- **Simple tasks**: 96.7% input reduction, 96.4% total reduction
- **Complex workflows**: 91.2% input reduction, 90.7% total reduction

### Trade-offs
- **Success rate**: 100% across all toolset sizes
- **Tool calls**: 2-3x increase in call volume
- **Execution time**: ~50% longer

### Average Performance
- 96% reduction for inputs
- 90% reduction for total token consumption

## Why It Works

Previous approaches had critical limitations:
- Semantic search alone left LLMs unaware of available tools, reducing search attempts
- Progressive search depended on input data quality

The hybrid approach preserves discoverability while maintaining efficiency, making comprehensive AI agent development practical without context window limitations.

## Relevance to This Project

This dynamic approach may offer a middle ground between pure context loading and static tool calling. We should consider implementing a similar pattern for database access and measure whether the 2-3x increase in calls is offset by token savings.
