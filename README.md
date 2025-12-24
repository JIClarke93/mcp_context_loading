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
- SQLAlchemy 2.0 ORM with Pydantic Settings validation

**API Layer (Netflix Dispatch Pattern)**
- FastAPI web framework serving the application
- **Services**: Async business logic and database operations
- **Routers**: API endpoint definitions and request handling
- **Models**: Pydantic models for request/response validation
- **DB**: SQLAlchemy database models
- **Exceptions**: Domain-specific error handling
- RESTful endpoints for agent interaction

**Agent Layer**
- PydanticAI-powered conversational agent
- Dual-mode operation: context loading vs MCP tool calling
- FastMCP integration for tool-based data access

**Benchmarking Layer**
- Token usage tracking for both approaches
- Performance metrics collection
- Comparative analysis tooling

### Design Philosophy

The backend follows the **Netflix Dispatch pattern**, organizing code by business domain (users, products, categories, orders, reviews) rather than technical layer. Each business area is self-contained with a consistent file structure:

**`db.py`** - SQLAlchemy database model defining the table schema, relationships, and constraints. Uses UUID primary keys for security and distribution. Contains only the ORM model, no business logic.

**`model.py`** - Pydantic models for API validation. Defines `Base`, `Create`, `Update`, and `Response` models with field validation and serialization rules. Enforces data integrity at the API boundary.

**`service.py`** - Async business logic layer that is HTTP-agnostic. Contains all database operations, business rules, and validation logic. Raises domain-specific exceptions rather than HTTP errors, enabling reuse across different interfaces (REST, GraphQL, CLI).

**`router.py`** - FastAPI endpoint definitions. Handles HTTP concerns (status codes, request/response formatting). Catches service layer exceptions and translates them to appropriate HTTP responses. Thin layer focused solely on web protocol.

**`exceptions.py`** - Custom exception hierarchy for the domain. Base exception class for the business area with specific exceptions inheriting from it. Provides clear error semantics independent of transport layer.

**`__init__.py`** - Public interface exports. Exposes models and exceptions for consumption by other business areas. Routers are imported explicitly when needed, maintaining loose coupling.

This structure provides clear separation of concerns: database access, validation, business logic, and HTTP handling are isolated in dedicated files. The pattern scales well as business complexity grows and makes testing straightforward since each layer can be tested independently.

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

## Benchmark Results

We conducted comprehensive benchmarking comparing context loading versus tool calling approaches using both mock data and real database queries. The results validate research findings from Speakeasy and demonstrate significant efficiency gains with tool-based architectures.

### Key Findings

**Token Usage Reduction: 91.44%**
- Context Loading: 36,157 tokens (500 entities pre-loaded)
- Tool Calling: 3,094 tokens (50 entities fetched on-demand)

**Entity Efficiency**
- Context Loading: 100 entities per type (users, products, categories, orders, reviews) = 500 total
- Tool Calling: 10 entities per type via 5 tool calls = 50 total
- Entity Reduction: 90%

**Database Operations**
- Both approaches: 5 database queries
- Context Loading: 0 tool calls (all data pre-loaded into system prompt)
- Tool Calling: 5 tool calls (on-demand fetching as needed)

### Validation Against Research

Our findings closely align with industry research:
- **Speakeasy Report**: 91.2% token reduction for complex workflows
- **Our Results**: 91.44% token reduction with real database
- **Consistency**: Mock data benchmark showed 91.21% reduction, confirming reproducibility

### Visualizations

Comprehensive performance comparison charts are available in `benchmarks/results/`:
- `agent_comparison.png` - Mock data benchmark (4-panel comparison)
- `agent_comparison_db.png` - Real database benchmark (4-panel comparison)
- `benchmark_results.json` - Mock data detailed metrics
- `benchmark_results_db.json` - Real database detailed metrics

Each visualization includes:
1. Token usage comparison
2. Total entities loaded
3. Entity breakdown by type (users, products, categories, orders, reviews)
4. Database queries and tool calls count

### Practical Implications

**When to Use Context Loading:**
- Small, static datasets (< 100 entities)
- Queries requiring full dataset visibility
- Scenarios where latency is more critical than token cost
- One-shot tasks without follow-up interactions

**When to Use Tool Calling:**
- Large datasets (> 100 entities)
- Dynamic data that changes frequently
- Multi-turn conversations where data needs evolve
- Cost-sensitive applications (91% token reduction = 91% cost reduction)
- Complex workflows requiring selective data access

**Hybrid Approach:**
Consider combining both patterns:
- Load frequently accessed static data (e.g., category hierarchy, product types) into context
- Use tools for variable/dynamic queries (e.g., user orders, inventory levels, reviews)
- Provides balance between latency and token efficiency

### Benchmark Methodology

**Database Setup:**
- SQLite database seeded with 500 test entities using `rdb/seed.py`
- 5 business areas: users, products, categories, orders, reviews
- Realistic relationships and data distributions

**Agent Implementation:**
- `be/chat_context/`: PydanticAI agent with full database context in system prompt
- `be/chat_tools/`: PydanticAI agent with 10 registered tools wrapping service layer
- Model: Anthropic Claude 3.5 Sonnet (`claude-3-5-sonnet-20241022`)
- Token counting: tiktoken with `cl100k_base` encoding

**Measurement Scripts:**
- `benchmarks/compare_simple.py`: Mock data benchmark (no database required)
- `benchmarks/compare_with_db.py`: Real database benchmark (requires seeded SQLite)
- Both generate JSON metrics and matplotlib visualizations

### Running Benchmarks

```bash
# Seed the database with test data
uv run python rdb/seed.py

# Run real database benchmark
uv run python benchmarks/compare_with_db.py

# Run mock data benchmark (faster, no DB required)
uv run python benchmarks/compare_simple.py
```

Results are saved to `benchmarks/results/` with timestamped JSON data and PNG visualizations.

## Development Roadmap

- [x] Database schema design and implementation
- [x] Alembic migration setup
- [x] FastAPI application structure using Netflix Dispatch pattern (services, routers, models, db, exceptions)
- [x] Context loading implementation (`be/chat_context/`)
- [x] PydanticAI agent setup (both context and tools modes)
- [x] Tool calling implementation (`be/chat_tools/`)
- [x] Benchmarking framework (mock and real database)
- [x] Comparative analysis and visualizations
- [x] Documentation and findings
- [ ] FastMCP integration (optional enhancement)
- [ ] Production deployment considerations

## License

See LICENSE file for details.
