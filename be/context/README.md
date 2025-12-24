# Context Module

The context module implements a dispatch pattern for accessing service layer functions across all business areas. It enables context loading by providing a centralized interface for pre-fetching database information to inject into AI agent context windows.

## Architecture

### `protocols.py`
Defines Protocol interfaces for each business area (users, products, categories, orders, reviews). Protocols provide type-safe contracts ensuring dispatch implementations match service layer signatures.

### `dispatch.py`
Central dispatch system mapping business areas to their service functions. The `DISPATCH` dictionary provides a unified interface for accessing all data retrieval operations.

### `loader.py`
Context loading utilities that use the dispatch system to pre-fetch related data across multiple business areas. Includes domain-specific loaders and a full context loader.

## Usage

### Direct Dispatch Access

```python
from be.context import DISPATCH
from be.dependencies import get_db

async with get_db() as db:
    # Access any business area's service functions
    users = await DISPATCH["users"].list_users(db, skip=0, limit=10)
    products = await DISPATCH["products"].list_products(db, category_id=some_id)

    # Get specific entities
    user = await DISPATCH["users"].get_user_by_id(db, user_id)
```

### Context Loading

```python
from be.context import load_user_context, load_product_context, load_full_context
from be.dependencies import get_db

async with get_db() as db:
    # Load user with related orders and reviews
    user_ctx = await load_user_context(
        db,
        user_id=some_id,
        include_orders=True,
        include_reviews=True
    )

    # Load product with reviews
    product_ctx = await load_product_context(
        db,
        product_id=product_id,
        include_reviews=True
    )

    # Load all data (warning: can be very large)
    full_ctx = await load_full_context(db, limit_per_entity=50)
```

## Design Philosophy

The dispatch pattern provides several benefits:

**Centralized Access**: Single entry point for all service layer functions across business areas.

**Type Safety**: Protocol definitions ensure implementations match service signatures.

**Flexibility**: Context loaders can combine data from multiple business areas with custom filtering.

**Separation of Concerns**: Context loading logic is isolated from business logic and HTTP handling.

**Testability**: Dispatch can be mocked for testing context loading without database dependencies.

## Benchmarking Use Case

This module is specifically designed for comparing context loading vs MCP tool calling:

- **Context Loading Mode**: Use loader functions to pre-fetch all relevant data and inject into agent prompt
- **MCP Tool Mode**: Provide agent with tools that call dispatch functions on-demand

The dispatch abstraction allows measuring the same operations in both modes for fair comparison.
