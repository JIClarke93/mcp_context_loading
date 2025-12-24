"""Simplified benchmark comparing context vs tools using mock data.

This script evaluates the context window and data loading pressure
without requiring database access.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import matplotlib.pyplot as plt
import tiktoken


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


def create_mock_data(num_entities_per_type: int = 100) -> dict:
    """Create mock database data for benchmarking.

    Args:
        num_entities_per_type: Number of entities to create per type.

    Returns:
        Dictionary with mock data for all business areas.
    """
    # Create users
    users = [
        {
            "id": str(uuid4()),
            "email": f"user{i}@example.com",
            "username": f"user{i}",
            "full_name": f"User Number {i}",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
        }
        for i in range(num_entities_per_type)
    ]

    # Create categories
    categories = [
        {
            "id": str(uuid4()),
            "name": f"Category {i}",
            "description": f"Description for category {i}",
            "parent_id": None if i < 20 else str(uuid4()),
            "created_at": "2024-01-01T00:00:00Z",
        }
        for i in range(num_entities_per_type)
    ]

    # Create products
    products = [
        {
            "id": str(uuid4()),
            "name": f"Product {i}",
            "description": f"Detailed description for product {i}. This is a great product with many features.",
            "price": "29.99",
            "category_id": categories[i % len(categories)]["id"],
            "stock_quantity": 100,
            "sku": f"SKU{i:06d}",
            "is_available": True,
            "created_at": "2024-01-01T00:00:00Z",
        }
        for i in range(num_entities_per_type)
    ]

    # Create orders
    orders = [
        {
            "id": str(uuid4()),
            "user_id": users[i % len(users)]["id"],
            "total_price": "149.95",
            "status": "PENDING",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        for i in range(num_entities_per_type)
    ]

    # Create reviews
    reviews = [
        {
            "id": str(uuid4()),
            "user_id": users[i % len(users)]["id"],
            "product_id": products[i % len(products)]["id"],
            "rating": (i % 5) + 1,
            "comment": f"This is my review for product {i}. Great quality and fast shipping!",
            "created_at": "2024-01-01T00:00:00Z",
        }
        for i in range(num_entities_per_type)
    ]

    return {
        "users": users,
        "categories": categories,
        "products": products,
        "orders": orders,
        "reviews": reviews,
    }


def benchmark_context_loading(data: dict) -> dict:
    """Benchmark context loading approach (all data upfront).

    Args:
        data: Mock database data.

    Returns:
        Benchmark results dictionary.
    """
    print("Benchmarking context loading agent...")

    # Convert all data to JSON (simulates what goes into system prompt)
    context_json = json.dumps(data, indent=2)

    # Measure size
    context_size_chars = len(context_json)
    context_size_tokens = count_tokens(context_json)

    # Count entities
    num_users = len(data["users"])
    num_products = len(data["products"])
    num_categories = len(data["categories"])
    num_orders = len(data["orders"])
    num_reviews = len(data["reviews"])

    results = {
        "approach": "context_loading",
        "context_size_chars": context_size_chars,
        "context_size_tokens": context_size_tokens,
        "entities_loaded": {
            "users": num_users,
            "products": num_products,
            "categories": num_categories,
            "orders": num_orders,
            "reviews": num_reviews,
            "total": num_users + num_products + num_categories + num_orders + num_reviews,
        },
        "tool_calls": 0,
        "queries_to_db": 5,  # One query per entity type
    }

    print(f"  Context size: {context_size_chars:,} chars, {context_size_tokens:,} tokens")
    print(f"  Total entities loaded: {results['entities_loaded']['total']}")

    return results


def benchmark_tool_calling(data: dict, limit: int = 10) -> dict:
    """Benchmark tool calling approach (on-demand data fetching).

    Args:
        data: Mock database data.
        limit: Number of entities to fetch per tool call.

    Returns:
        Benchmark results dictionary.
    """
    print("\nBenchmarking tool calling agent...")

    tool_calls = []
    total_tokens = 0
    total_chars = 0

    # Simulate common query patterns - fetch first 10 of each type

    # 1. List users
    users_subset = data["users"][:limit]
    users_json = json.dumps(users_subset)
    users_tokens = count_tokens(users_json)
    tool_calls.append({"tool": "list_users", "chars": len(users_json), "tokens": users_tokens})
    total_chars += len(users_json)
    total_tokens += users_tokens

    # 2. List products
    products_subset = data["products"][:limit]
    products_json = json.dumps(products_subset)
    products_tokens = count_tokens(products_json)
    tool_calls.append(
        {"tool": "list_products", "chars": len(products_json), "tokens": products_tokens}
    )
    total_chars += len(products_json)
    total_tokens += products_tokens

    # 3. List categories
    categories_subset = data["categories"][:limit]
    categories_json = json.dumps(categories_subset)
    categories_tokens = count_tokens(categories_json)
    tool_calls.append(
        {"tool": "list_categories", "chars": len(categories_json), "tokens": categories_tokens}
    )
    total_chars += len(categories_json)
    total_tokens += categories_tokens

    # 4. List orders
    orders_subset = data["orders"][:limit]
    orders_json = json.dumps(orders_subset)
    orders_tokens = count_tokens(orders_json)
    tool_calls.append({"tool": "list_orders", "chars": len(orders_json), "tokens": orders_tokens})
    total_chars += len(orders_json)
    total_tokens += orders_tokens

    # 5. List reviews
    reviews_subset = data["reviews"][:limit]
    reviews_json = json.dumps(reviews_subset)
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
            "users": len(users_subset),
            "products": len(products_subset),
            "categories": len(categories_subset),
            "orders": len(orders_subset),
            "reviews": len(reviews_subset),
            "total": len(users_subset)
            + len(products_subset)
            + len(categories_subset)
            + len(orders_subset)
            + len(reviews_subset),
        },
    }

    print(f"  Total data retrieved: {total_chars:,} chars, {total_tokens:,} tokens")
    print(f"  Tool calls made: {len(tool_calls)}")
    print(f"  Total entities loaded: {results['entities_loaded']['total']}")

    return results


def generate_visualizations(context_results: dict, tools_results: dict, output_dir: Path):
    """Generate matplotlib visualizations comparing both approaches.

    Args:
        context_results: Results from context loading agent.
        tools_results: Results from tool calling agent.
        output_dir: Directory to save visualizations.
    """
    print("\nGenerating visualizations...")

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Context Loading vs Tool Calling: Performance Comparison",
        fontsize=16,
        fontweight="bold",
    )

    # 1. Token Usage Comparison
    ax1 = axes[0, 0]
    approaches = ["Context\nLoading", "Tool\nCalling"]
    tokens = [context_results["context_size_tokens"], tools_results["context_size_tokens"]]
    colors = ["#3498db", "#e74c3c"]
    bars1 = ax1.bar(approaches, tokens, color=colors, alpha=0.7, edgecolor="black")
    ax1.set_ylabel("Tokens", fontsize=12)
    ax1.set_title("Token Usage", fontsize=13, fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)

    # Add value labels on bars
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

    # 2. Entities Loaded Comparison
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

    # 3. Entity Breakdown (grouped bar chart)
    ax3 = axes[1, 0]
    entity_types = ["users", "products", "categories", "orders", "reviews"]
    context_counts = [context_results["entities_loaded"][e] for e in entity_types]
    tools_counts = [tools_results["entities_loaded"][e] for e in entity_types]

    x = range(len(entity_types))
    width = 0.35
    bars3a = ax3.bar(
        [i - width / 2 for i in x],
        context_counts,
        width,
        label="Context Loading",
        color=colors[0],
        alpha=0.7,
        edgecolor="black",
    )
    bars3b = ax3.bar(
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

    # 4. Database Queries & Tool Calls
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

    # Add value labels
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

    # Save visualization
    viz_path = output_dir / "agent_comparison.png"
    plt.savefig(viz_path, dpi=300, bbox_inches="tight")
    print(f"  Saved visualization: {viz_path}")

    plt.close()


def main():
    """Main benchmarking function."""
    print("=" * 60)
    print("Agent Performance Benchmark")
    print("=" * 60)

    # Create output directory
    output_dir = Path("benchmarks/results")
    output_dir.mkdir(exist_ok=True, parents=True)

    # Create mock data
    print("\nCreating mock data...")
    data = create_mock_data(num_entities_per_type=100)
    print(f"Created {sum(len(v) for v in data.values())} total entities")

    # Benchmark context loading agent
    context_results = benchmark_context_loading(data)

    # Benchmark tools agent
    tools_results = benchmark_tool_calling(data, limit=10)

    # Create comparison summary
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

    # Save results to JSON
    results_path = output_dir / "benchmark_results.json"
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
    main()
