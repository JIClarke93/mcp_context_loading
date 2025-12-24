# MCP Context Loading

A benchmarking project to evaluate the cost and efficiency trade-offs between Model Context Protocol (MCP) tool calling and direct context loading for database queries in AI agent applications.

## Overview

This project implements two distinct patterns for AI agents to access database information and measures their performance characteristics. The goal is to provide empirical data on token usage, latency, and accuracy when choosing between MCP tools versus context stuffing.

## Problem Statement

When building AI agents that need to query databases, developers face a fundamental choice:

1. **Context Loading**: Pre-fetch data and inject it directly into the agent's context window
2. **Tool Calling (MCP)**: Provide the agent with tools to query data on-demand via the Model Context Protocol

Each approach has theoretical trade-offs in terms of token consumption, response latency, and information accuracy. This project measures these trade-offs empirically.

## Architecture

### Core Components

**Database Layer**
- SQLite database with a moderately complex schema
- Alembic for database migrations and version control
- Netflix Dispatch pattern for clean separation of concerns (models, services, routers)

**API Layer**
- FastAPI web framework serving the application
- RESTful endpoints for agent interaction
- Chat message persistence for conversation history

**Agent Layer**
- PydanticAI-powered conversational agent
- Dual-mode operation: context loading vs MCP tool calling
- FastMCP integration for tool-based data access

**Benchmarking Layer**
- Token usage tracking for both approaches
- Performance metrics collection
- Comparative analysis tooling

### Data Flow

#### Context Loading Mode
```
User Query -> Agent (with pre-loaded context) -> Response
                      �
                Database (pre-fetch)
```

#### MCP Tool Mode
```
User Query -> Agent -> Tool Call -> Service Layer -> Database
                  �
              Response
```

## Technology Stack

- **Python 3.11+**: Core language
- **FastAPI**: Web framework
- **SQLite**: Database
- **Alembic**: Database migrations
- **PydanticAI**: Agent framework
- **FastMCP**: Model Context Protocol implementation
- **uv**: Package management

## Benchmarking Methodology

This project employs a lightweight, purpose-built benchmarking approach tailored for research and comparative analysis. While enterprise-grade solutions such as MLflow, Weights & Biases, or LangSmith offer comprehensive experiment tracking and production monitoring capabilities, this implementation prioritizes simplicity and cost-effectiveness for the following reasons:

### Design Philosophy

**Research-Oriented**: The primary objective is comparative analysis between two specific patterns rather than production deployment monitoring. A streamlined benchmarking framework reduces operational overhead and maintains focus on the core research questions.

**Cost Constraints**: Enterprise MLOps platforms introduce infrastructure costs and complexity that exceed the requirements of this investigation. A custom implementation using standard Python libraries provides adequate measurement capabilities without additional service dependencies.

**Educational Value**: Building benchmarking instrumentation from first principles offers deeper insight into the metrics being measured and their implications, which aligns with the project's research objectives.

**Reproducibility**: The self-contained nature of the benchmarking code ensures the project remains easily reproducible across different environments without requiring access to external platforms or commercial services.

### Measurement Approach

The benchmarking layer captures:
- Token counts via API response metadata
- Latency measurements using standard Python timing instrumentation
- Query accuracy through deterministic validation sets
- Cost projections based on current LLM pricing models

Results are persisted to structured files (JSON/CSV) for analysis using standard data science tools (pandas, matplotlib) rather than specialized platforms.

### Scope and Limitations

This approach is explicitly designed for comparative research rather than production model monitoring. For production deployments requiring experiment versioning, model registry, hyperparameter optimization, or distributed training coordination, enterprise solutions remain the appropriate choice.

## Project Goals

1. Build a realistic database schema with meaningful relationships
2. Implement both context loading and MCP tool patterns
3. Create a conversational interface for testing
4. Measure and compare:
   - Token consumption per query
   - Response latency
   - Information retrieval accuracy
   - Cost implications at scale
5. Document findings and recommendations

## Expected Outcomes

This benchmark will provide data-driven insights into:

- When to use context loading vs tool calling
- Cost implications of each approach
- Performance characteristics under different query patterns
- Best practices for hybrid implementations

## Development Roadmap

- [ ] Database schema design and implementation
- [ ] FastAPI application structure (models, services, routers)
- [ ] Alembic migration setup
- [ ] Context loading implementation
- [ ] PydanticAI agent setup
- [ ] FastMCP tool integration
- [ ] Benchmarking framework
- [ ] Comparative analysis
- [ ] Documentation and findings

## License

See LICENSE file for details.
