"""Benchmark script comparing context vs tools using real database.

This script evaluates the context window and data loading pressure
using actual database queries.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
import tiktoken
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from be.dependencies import AsyncSessionLocal
from rdb.models import Category, Order, Product, Review, User


def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens for.
        model: Tiktoken encoding model name.

    Returns:
        Number of tokens.
    """
    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))


async def load_all_data(db: AsyncSession, limit: int = 100) -> dict:
    """Load all data from database (context loading approach).

    Args:
        db: Database session.
        limit: Maximum entities per type.

    Returns:
        Dictionary with all data.
    """
    # Load users
    result = await db.execute(select(User).limit(limit))
    users = result.scalars().all()

    # Load categories
    result = await db.execute(select(Category).limit(limit))
    categories = result.scalars().all()

    # Load products
    result = await db.execute(select(Product).limit(limit))
    products = result.scalars().all()

    # Load orders
    result = await db.execute(select(Order).limit(limit))
    orders = result.scalars().all()

    # Load reviews
    result = await db.execute(select(Review).limit(limit))
    reviews = result.scalars().all()

    # Convert to dict
    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "full_name": u.full_name,
                "is_active": u.is_active,
                "created_at": str(u.created_at),
            }
            for u in users
        ],
        "categories": [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "parent_id": c.parent_id,
                "created_at": str(c.created_at),
            }
            for c in categories
        ],
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": str(p.price),
                "category_id": p.category_id,
                "stock_quantity": p.stock_quantity,
                "sku": p.sku,
                "is_available": p.is_available,
                "created_at": str(p.created_at),
            }
            for p in products
        ],
        "orders": [
            {
                "id": o.id,
                "user_id": o.user_id,
                "total_amount": str(o.total_amount),
                "status": o.status.value,
                "created_at": str(o.created_at),
            }
            for o in orders
        ],
        "reviews": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "product_id": r.product_id,
                "rating": r.rating,
                "comment": r.comment,
                "is_verified_purchase": r.is_verified_purchase,
                "created_at": str(r.created_at),
            }
            for r in reviews
        ],
    }


async def benchmark_context_loading(db: AsyncSession, limit: int = 100) -> dict:
    """Benchmark context loading approach.

    Args:
        db: Database session.
        limit: Maximum entities per type.

    Returns:
        Benchmark results.
    """
    print("Benchmarking context loading agent...")

    # Load all data
    data = await load_all_data(db, limit)

    # Convert to JSON
    context_json = json.dumps(data, indent=2)

    # Measure
    context_size_chars = len(context_json)
    context_size_tokens = count_tokens(context_json)

    results = {
        "approach": "context_loading",
        "context_size_chars": context_size_chars,
        "context_size_tokens": context_size_tokens,
        "entities_loaded": {
            "users": len(data["users"]),
            "products": len(data["products"]),
            "categories": len(data["categories"]),
            "orders": len(data["orders"]),
            "reviews": len(data["reviews"]),
            "total": sum(len(v) for v in data.values()),
        },
        "tool_calls": 0,
        "queries_to_db": 5,
    }

    print(f"  Context size: {context_size_chars:,} chars, {context_size_tokens:,} tokens")
    print(f"  Total entities loaded: {results['entities_loaded']['total']}")

    return results


async def benchmark_tool_calling(db: AsyncSession, limit: int = 10) -> dict:
    """Benchmark tool calling approach.

    Args:
        db: Database session.
        limit: Entities to fetch per tool call.

    Returns:
        Benchmark results.
    """
    print("\nBenchmarking tool calling agent...")

    tool_calls = []
    total_tokens = 0
    total_chars = 0

    # Simulate tool calls - fetch limited data per call

    # 1. List users
    result = await db.execute(select(User).limit(limit))
    users = result.scalars().all()
    users_data = [
        {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "created_at": str(u.created_at),
        }
        for u in users
    ]
    users_json = json.dumps(users_data)
    users_tokens = count_tokens(users_json)
    tool_calls.append({"tool": "list_users", "chars": len(users_json), "tokens": users_tokens})
    total_chars += len(users_json)
    total_tokens += users_tokens

    # 2. List products
    result = await db.execute(select(Product).limit(limit))
    products = result.scalars().all()
    products_data = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": str(p.price),
            "category_id": p.category_id,
            "stock_quantity": p.stock_quantity,
            "sku": p.sku,
            "is_available": p.is_available,
            "created_at": str(p.created_at),
        }
        for p in products
    ]
    products_json = json.dumps(products_data)
    products_tokens = count_tokens(products_json)
    tool_calls.append(
        {"tool": "list_products", "chars": len(products_json), "tokens": products_tokens}
    )
    total_chars += len(products_json)
    total_tokens += products_tokens

    # 3. List categories
    result = await db.execute(select(Category).limit(limit))
    categories = result.scalars().all()
    categories_data = [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "parent_id": c.parent_id,
            "created_at": str(c.created_at),
        }
        for c in categories
    ]
    categories_json = json.dumps(categories_data)
    categories_tokens = count_tokens(categories_json)
    tool_calls.append(
        {"tool": "list_categories", "chars": len(categories_json), "tokens": categories_tokens}
    )
    total_chars += len(categories_json)
    total_tokens += categories_tokens

    # 4. List orders
    result = await db.execute(select(Order).limit(limit))
    orders = result.scalars().all()
    orders_data = [
        {
            "id": o.id,
            "user_id": o.user_id,
            "total_amount": str(o.total_amount),
            "status": o.status.value,
            "created_at": str(o.created_at),
        }
        for o in orders
    ]
    orders_json = json.dumps(orders_data)
    orders_tokens = count_tokens(orders_json)
    tool_calls.append({"tool": "list_orders", "chars": len(orders_json), "tokens": orders_tokens})
    total_chars += len(orders_json)
    total_tokens += orders_tokens

    # 5. List reviews
    result = await db.execute(select(Review).limit(limit))
    reviews = result.scalars().all()
    reviews_data = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "product_id": r.product_id,
            "rating": r.rating,
            "comment": r.comment,
            "is_verified_purchase": r.is_verified_purchase,
            "created_at": str(r.created_at),
        }
        for r in reviews
    ]
    reviews_json = json.dumps(reviews_data)
    reviews_tokens = count_tokens(reviews_json)
    tool_calls.append(
        {"tool": "list_reviews", "chars": len(reviews_json), "tokens": reviews_tokens}
    )
    total_chars += len(reviews_json)
    total_tokens += reviews_tokens

    results = {
        "approach": "tool_calling",
        "context_size_chars": total_chars,
        "context_size_tokens": total_tokens,
        "tool_calls": len(tool_calls),
        "queries_to_db": len(tool_calls),
        "tool_call_details": tool_calls,
        "entities_loaded": {
            "users": len(users),
            "products": len(products),
            "categories": len(categories),
            "orders": len(orders),
            "reviews": len(reviews),
            "total": len(users)
            + len(products)
            + len(categories)
            + len(orders)
            + len(reviews),
        },
    }

    print(f"  Total data retrieved: {total_chars:,} chars, {total_tokens:,} tokens")
    print(f"  Tool calls made: {len(tool_calls)}")
    print(f"  Total entities loaded: {results['entities_loaded']['total']}")

    return results


def generate_visualizations(context_results: dict, tools_results: dict, output_dir: Path):
    """Generate matplotlib visualizations.

    Args:
        context_results: Context loading results.
        tools_results: Tool calling results.
        output_dir: Output directory.
    """
    print("\nGenerating visualizations...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Context Loading vs Tool Calling: Real Database Performance",
        fontsize=16,
        fontweight="bold",
    )

    approaches = ["Context\nLoading", "Tool\nCalling"]
    colors = ["#3498db", "#e74c3c"]

    # 1. Token Usage
    ax1 = axes[0, 0]
    tokens = [context_results["context_size_tokens"], tools_results["context_size_tokens"]]
    bars1 = ax1.bar(approaches, tokens, color=colors, alpha=0.7, edgecolor="black")
    ax1.set_ylabel("Tokens", fontsize=12)
    ax1.set_title("Token Usage", fontsize=13, fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)
    for bar in bars1:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{int(height):,}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # 2. Entities Loaded
    ax2 = axes[0, 1]
    entities = [
        context_results["entities_loaded"]["total"],
        tools_results["entities_loaded"]["total"],
    ]
    bars2 = ax2.bar(approaches, entities, color=colors, alpha=0.7, edgecolor="black")
    ax2.set_ylabel("Number of Entities", fontsize=12)
    ax2.set_title("Total Entities Loaded", fontsize=13, fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)
    for bar in bars2:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{int(height):,}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # 3. Entity Breakdown
    ax3 = axes[1, 0]
    entity_types = ["users", "products", "categories", "orders", "reviews"]
    context_counts = [context_results["entities_loaded"][e] for e in entity_types]
    tools_counts = [tools_results["entities_loaded"][e] for e in entity_types]

    x = range(len(entity_types))
    width = 0.35
    ax3.bar(
        [i - width / 2 for i in x],
        context_counts,
        width,
        label="Context Loading",
        color=colors[0],
        alpha=0.7,
        edgecolor="black",
    )
    ax3.bar(
        [i + width / 2 for i in x],
        tools_counts,
        width,
        label="Tool Calling",
        color=colors[1],
        alpha=0.7,
        edgecolor="black",
    )

    ax3.set_xlabel("Entity Type", fontsize=12)
    ax3.set_ylabel("Count", fontsize=12)
    ax3.set_title("Entities Loaded by Type", fontsize=13, fontweight="bold")
    ax3.set_xticks(x)
    ax3.set_xticklabels([e.capitalize() for e in entity_types], rotation=45, ha="right")
    ax3.legend()
    ax3.grid(axis="y", alpha=0.3)

    # 4. DB Queries & Tool Calls
    ax4 = axes[1, 1]
    metrics = ["DB Queries", "Tool Calls"]
    context_vals = [context_results["queries_to_db"], context_results["tool_calls"]]
    tools_vals = [tools_results["queries_to_db"], tools_results["tool_calls"]]

    x = range(len(metrics))
    bars4a = ax4.bar(
        [i - width / 2 for i in x],
        context_vals,
        width,
        label="Context Loading",
        color=colors[0],
        alpha=0.7,
        edgecolor="black",
    )
    bars4b = ax4.bar(
        [i + width / 2 for i in x],
        tools_vals,
        width,
        label="Tool Calling",
        color=colors[1],
        alpha=0.7,
        edgecolor="black",
    )

    ax4.set_ylabel("Count", fontsize=12)
    ax4.set_title("Database Queries & Tool Calls", fontsize=13, fontweight="bold")
    ax4.set_xticks(x)
    ax4.set_xticklabels(metrics)
    ax4.legend()
    ax4.grid(axis="y", alpha=0.3)

    for bars in [bars4a, bars4b]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax4.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{int(height)}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

    plt.tight_layout()

    viz_path = output_dir / "agent_comparison_db.png"
    plt.savefig(viz_path, dpi=300, bbox_inches="tight")
    print(f"  Saved visualization: {viz_path}")

    plt.close()


async def main():
    """Main benchmarking function."""
    print("=" * 60)
    print("Agent Performance Benchmark (Real Database)")
    print("=" * 60)

    output_dir = Path("benchmarks/results")
    output_dir.mkdir(exist_ok=True, parents=True)

    async with AsyncSessionLocal() as db:
        # Benchmark both approaches
        context_results = await benchmark_context_loading(db, limit=100)
        tools_results = await benchmark_tool_calling(db, limit=10)

    # Create comparison
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "context_loading": context_results,
        "tool_calling": tools_results,
        "summary": {
            "token_reduction_pct": round(
                (
                    1
                    - tools_results["context_size_tokens"]
                    / context_results["context_size_tokens"]
                )
                * 100,
                2,
            ),
            "entity_reduction_pct": round(
                (
                    1
                    - tools_results["entities_loaded"]["total"]
                    / context_results["entities_loaded"]["total"]
                )
                * 100,
                2,
            ),
        },
    }

    # Save results
    results_path = output_dir / "benchmark_results_db.json"
    with open(results_path, "w") as f:
        json.dump(comparison, f, indent=2)
    print(f"\nSaved results: {results_path}")

    # Generate visualizations
    generate_visualizations(context_results, tools_results, output_dir)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Context Loading: {context_results['context_size_tokens']:,} tokens")
    print(f"Tool Calling:    {tools_results['context_size_tokens']:,} tokens")
    print(f"Token Reduction: {comparison['summary']['token_reduction_pct']}%")
    print(f"\nContext Loading: {context_results['entities_loaded']['total']} entities")
    print(f"Tool Calling:    {tools_results['entities_loaded']['total']} entities")
    print(f"Entity Reduction: {comparison['summary']['entity_reduction_pct']}%")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
