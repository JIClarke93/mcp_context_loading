"""
Simulation: Token vs Latency Trade-offs for MCP Context Loading Approaches

Compares three approaches across varying tool counts:
1. Full Context - All data pre-loaded into system prompt
2. Static Tools - All tool schemas loaded upfront
3. Dynamic Toolset - Lazy schema loading (Speakeasy approach)

Run: python -m be.chat_tools_speakeasy.simulation
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Callable


@dataclass
class ApproachConfig:
    """Configuration for simulating an approach."""
    name: str
    color: str
    linestyle: str
    marker: str
    # Functions that take num_tools and return tokens/latency
    token_fn: Callable[[np.ndarray], np.ndarray]
    latency_fn: Callable[[np.ndarray], np.ndarray]


# =============================================================================
# MODEL PARAMETERS (based on real-world measurements)
# =============================================================================

# Token parameters
BASE_SYSTEM_PROMPT_TOKENS = 500  # Base system prompt overhead
TOKENS_PER_TOOL_SCHEMA = 100    # Average tokens per tool definition
TOKENS_PER_ENTITY = 72          # Tokens per database entity (from our benchmarks)
ENTITIES_PER_TYPE = 100         # Entities loaded per type (users, products, etc.)
NUM_ENTITY_TYPES = 5            # Number of entity types

# Dynamic toolset parameters
DYNAMIC_META_TOOLS_TOKENS = 150  # search_tools + describe_tools + execute_tool
DYNAMIC_DISCOVERY_OVERHEAD = 75  # Tokens for discovery results per query
DYNAMIC_SCHEMAS_LOADED = 2.5     # Average number of schemas loaded per query

# Latency parameters (milliseconds)
LLM_BASE_LATENCY = 800          # Base LLM inference time
LLM_LATENCY_PER_1K_TOKENS = 50  # Additional latency per 1000 input tokens
TOOL_CALL_LATENCY = 200         # Round-trip time per tool call
DB_QUERY_LATENCY = 30           # Database query latency

# Dynamic approach makes 2-3x more calls
DYNAMIC_EXTRA_LLM_CALLS = 2     # Additional LLM inference rounds for discovery

# =============================================================================
# ACCURACY MODEL PARAMETERS
# =============================================================================
# Based on research: "Lost in the Middle" paper, Speakeasy benchmarks, etc.

# Full Context accuracy degradation factors
CONTEXT_SIZE_ACCURACY_THRESHOLD = 20000  # Tokens where "lost in middle" kicks in
CONTEXT_SIZE_ACCURACY_DECAY = 0.00002    # Accuracy loss per token above threshold
MAX_CONTEXT_ACCURACY_LOSS = 0.15         # Max 15% accuracy loss from context size

# Static Tools accuracy degradation factors
TOOL_COUNT_ACCURACY_THRESHOLD = 15       # Tools where selection confusion starts
TOOL_COUNT_ACCURACY_DECAY = 0.003        # Accuracy loss per tool above threshold
MAX_TOOL_ACCURACY_LOSS = 0.20            # Max 20% accuracy loss from tool overload

# Dynamic Toolset accuracy factors
DISCOVERY_FAILURE_BASE_RATE = 0.02       # 2% base rate of failing to find right tool
DISCOVERY_CYCLE_ERROR_RATE = 0.015       # 1.5% compounding error per extra cycle
DYNAMIC_CYCLES_MIN = 2                    # Best case: simple query
DYNAMIC_CYCLES_AVG = 3                    # Average case
DYNAMIC_CYCLES_MAX = 6                    # Worst case: complex multi-tool query

# Latency per additional cycle
LATENCY_PER_CYCLE = 600                   # ~600ms per discovery cycle (LLM + tool call)


# =============================================================================
# APPROACH MODELS
# =============================================================================

def full_context_tokens(num_tools: np.ndarray) -> np.ndarray:
    """Full context: tokens don't depend on tools, but on data size."""
    # All entities loaded into context
    entity_tokens = ENTITIES_PER_TYPE * NUM_ENTITY_TYPES * TOKENS_PER_ENTITY
    return np.full_like(num_tools, BASE_SYSTEM_PROMPT_TOKENS + entity_tokens, dtype=float)


def full_context_latency(num_tools: np.ndarray) -> np.ndarray:
    """Full context: single LLM call with large context."""
    tokens = full_context_tokens(num_tools)
    # Single LLM call, but with large context
    return LLM_BASE_LATENCY + (tokens / 1000) * LLM_LATENCY_PER_1K_TOKENS


def static_tools_tokens(num_tools: np.ndarray) -> np.ndarray:
    """Static tools: all tool schemas loaded upfront."""
    schema_tokens = num_tools * TOKENS_PER_TOOL_SCHEMA
    # Assume we fetch ~10 entities per type on average via tools
    data_tokens = 10 * NUM_ENTITY_TYPES * TOKENS_PER_ENTITY * 0.5  # Partial data
    return BASE_SYSTEM_PROMPT_TOKENS + schema_tokens + data_tokens


def static_tools_latency(num_tools: np.ndarray) -> np.ndarray:
    """Static tools: LLM call + tool calls."""
    tokens = static_tools_tokens(num_tools)
    llm_latency = LLM_BASE_LATENCY + (tokens / 1000) * LLM_LATENCY_PER_1K_TOKENS
    # Assume average 3 tool calls per query
    tool_latency = 3 * TOOL_CALL_LATENCY
    return llm_latency + tool_latency


def dynamic_toolset_tokens(num_tools: np.ndarray) -> np.ndarray:
    """Dynamic toolset: only meta-tools + schemas loaded on-demand."""
    # Only 3 meta-tools loaded, regardless of total tool count
    meta_tokens = DYNAMIC_META_TOOLS_TOKENS
    discovery_tokens = DYNAMIC_DISCOVERY_OVERHEAD
    # Only load schemas for tools actually used
    loaded_schema_tokens = DYNAMIC_SCHEMAS_LOADED * TOKENS_PER_TOOL_SCHEMA
    # Data fetched is similar to static
    data_tokens = 10 * NUM_ENTITY_TYPES * TOKENS_PER_ENTITY * 0.3
    return np.full_like(
        num_tools,
        BASE_SYSTEM_PROMPT_TOKENS + meta_tokens + discovery_tokens + loaded_schema_tokens + data_tokens,
        dtype=float
    )


def dynamic_toolset_latency(num_tools: np.ndarray) -> np.ndarray:
    """Dynamic toolset: more LLM calls but smaller context."""
    tokens = dynamic_toolset_tokens(num_tools)
    # Multiple LLM calls (discovery + description + execution)
    llm_latency = (1 + DYNAMIC_EXTRA_LLM_CALLS) * (
        LLM_BASE_LATENCY + (tokens / 1000) * LLM_LATENCY_PER_1K_TOKENS
    )
    # More tool calls: search + describe + execute
    tool_latency = 5 * TOOL_CALL_LATENCY
    return llm_latency + tool_latency


# =============================================================================
# ACCURACY MODELS
# =============================================================================

def full_context_accuracy(num_tools: np.ndarray) -> np.ndarray:
    """
    Full context accuracy: degrades due to "Lost in the Middle" phenomenon.

    When context is large, models struggle to retrieve information from the
    middle of the context window, leading to accuracy degradation.
    """
    tokens = full_context_tokens(num_tools)

    # Calculate accuracy loss from context size
    excess_tokens = np.maximum(0, tokens - CONTEXT_SIZE_ACCURACY_THRESHOLD)
    context_loss = np.minimum(
        excess_tokens * CONTEXT_SIZE_ACCURACY_DECAY,
        MAX_CONTEXT_ACCURACY_LOSS
    )

    # Additional loss from irrelevant data diluting signal
    # More data = more noise in the context
    data_noise_loss = 0.02  # 2% base loss from irrelevant data

    return 1.0 - context_loss - data_noise_loss


def static_tools_accuracy(num_tools: np.ndarray) -> np.ndarray:
    """
    Static tools accuracy: degrades when too many tools overwhelm the model.

    As tool count increases, the model has:
    1. More schemas to process (attention dilution)
    2. More similar tools to distinguish between (selection confusion)
    3. Higher chance of selecting wrong tool
    """
    # Calculate accuracy loss from tool overload
    excess_tools = np.maximum(0, num_tools - TOOL_COUNT_ACCURACY_THRESHOLD)
    tool_loss = np.minimum(
        excess_tools * TOOL_COUNT_ACCURACY_DECAY,
        MAX_TOOL_ACCURACY_LOSS
    )

    # Base success rate (tools are explicit, so fairly reliable)
    base_accuracy = 0.98

    return base_accuracy - tool_loss


def dynamic_toolset_accuracy(num_tools: np.ndarray, cycles: int = None) -> np.ndarray:
    """
    Dynamic toolset accuracy: affected by discovery failures and cycle errors.

    Each extra cycle has a chance of:
    1. Failing to discover the right tool
    2. Getting wrong schema
    3. Compounding errors across cycles

    Args:
        num_tools: Array of tool counts
        cycles: Number of discovery cycles (None = use average)
    """
    if cycles is None:
        cycles = DYNAMIC_CYCLES_AVG

    # Base discovery failure rate (finding wrong tool)
    discovery_loss = DISCOVERY_FAILURE_BASE_RATE

    # Compounding error per cycle: (1 - cycle_error)^cycles
    # This simulates error propagation across the discovery-describe-execute flow
    cycle_success = (1 - DISCOVERY_CYCLE_ERROR_RATE) ** cycles

    # Better tool selection when fewer tools (easier to find the right one)
    # But scales logarithmically - doubling tools doesn't double confusion
    tool_scaling = 1 - 0.01 * np.log10(np.maximum(num_tools, 1))

    # Speakeasy claims 100% success rate, but we model some realistic degradation
    base_accuracy = 0.97

    return base_accuracy * cycle_success * tool_scaling - discovery_loss


def dynamic_toolset_accuracy_range(num_tools: np.ndarray) -> tuple:
    """Return (min, avg, max) accuracy for dynamic toolset based on cycle count."""
    # More cycles = worse accuracy (compounding errors)
    best = dynamic_toolset_accuracy(num_tools, cycles=DYNAMIC_CYCLES_MIN)   # 2 cycles
    avg = dynamic_toolset_accuracy(num_tools, cycles=DYNAMIC_CYCLES_AVG)    # 3 cycles
    worst = dynamic_toolset_accuracy(num_tools, cycles=DYNAMIC_CYCLES_MAX)  # 6 cycles
    return best, avg, worst


def dynamic_toolset_latency(num_tools: np.ndarray, cycles: int = None) -> np.ndarray:
    """Dynamic toolset: latency varies by number of discovery cycles."""
    if cycles is None:
        cycles = DYNAMIC_CYCLES_AVG

    tokens = dynamic_toolset_tokens(num_tools)
    # Multiple LLM calls based on cycle count
    llm_latency = cycles * (
        LLM_BASE_LATENCY + (tokens / 1000) * LLM_LATENCY_PER_1K_TOKENS
    )
    # Tool calls scale with cycles: search + describe per cycle + execute
    tool_latency = (cycles + 1) * TOOL_CALL_LATENCY
    return llm_latency + tool_latency


def dynamic_toolset_latency_range(num_tools: np.ndarray) -> tuple:
    """Return (min, avg, max) latency for dynamic toolset based on cycle count."""
    best = dynamic_toolset_latency(num_tools, cycles=DYNAMIC_CYCLES_MIN)   # 2 cycles = fast
    avg = dynamic_toolset_latency(num_tools, cycles=DYNAMIC_CYCLES_AVG)    # 3 cycles
    worst = dynamic_toolset_latency(num_tools, cycles=DYNAMIC_CYCLES_MAX)  # 6 cycles = slow
    return best, avg, worst


# =============================================================================
# APPROACH CONFIGURATIONS
# =============================================================================

APPROACHES = [
    ApproachConfig(
        name="Full Context",
        color="#e74c3c",  # Red
        linestyle="-",
        marker="s",
        token_fn=full_context_tokens,
        latency_fn=full_context_latency,
    ),
    ApproachConfig(
        name="Static Tools",
        color="#3498db",  # Blue
        linestyle="-",
        marker="o",
        token_fn=static_tools_tokens,
        latency_fn=static_tools_latency,
    ),
    ApproachConfig(
        name="Dynamic Toolset",
        color="#2ecc71",  # Green
        linestyle="-",
        marker="^",
        token_fn=dynamic_toolset_tokens,
        latency_fn=dynamic_toolset_latency,
    ),
]


# =============================================================================
# SIMULATION AND PLOTTING
# =============================================================================

def run_simulation(
    tool_counts: np.ndarray = None,
    save_path: str = None,
    show_plot: bool = True,
) -> dict:
    """
    Run the simulation and generate plots.
    Shows spread for Dynamic Toolset based on cycle count (2-6 cycles).

    Args:
        tool_counts: Array of tool counts to simulate
        save_path: Path to save the figure (optional)
        show_plot: Whether to display the plot

    Returns:
        Dictionary with simulation results
    """
    if tool_counts is None:
        tool_counts = np.array([5, 10, 20, 30, 40, 50, 75, 100, 150, 200])

    # Calculate metrics for Full Context and Static Tools
    fc_tokens = full_context_tokens(tool_counts)
    fc_latency = full_context_latency(tool_counts)

    st_tokens = static_tools_tokens(tool_counts)
    st_latency = static_tools_latency(tool_counts)

    # Calculate Dynamic Toolset with spread
    dy_tokens = dynamic_toolset_tokens(tool_counts)
    dy_lat_best, dy_lat_avg, dy_lat_worst = dynamic_toolset_latency_range(tool_counts)

    # Create figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("MCP Context Loading: Token vs Latency Trade-offs\n(Dynamic Toolset shows 2-6 cycle spread)",
                 fontsize=14, fontweight='bold')

    # =================================
    # Plot 1: Tokens vs Latency (main plot)
    # =================================
    ax1 = axes[0]
    ax1.set_title("Tokens vs Latency by Tool Count")
    ax1.set_xlabel("Latency (ms)")
    ax1.set_ylabel("Tokens")

    # Full Context
    ax1.plot(fc_latency, fc_tokens, color='#e74c3c', linestyle='-', marker='s',
             markersize=8, linewidth=2, label='Full Context')

    # Static Tools
    ax1.plot(st_latency, st_tokens, color='#3498db', linestyle='-', marker='o',
             markersize=8, linewidth=2, label='Static Tools')

    # Dynamic Toolset - show spread
    ax1.fill_betweenx(dy_tokens, dy_lat_best, dy_lat_worst, color='green', alpha=0.2,
                      label='Dynamic (2-6 cycles)')
    ax1.plot(dy_lat_best, dy_tokens, color='lightgreen', linestyle='--', linewidth=1,
             marker='^', markersize=6, alpha=0.7, label='Dynamic (2 cycles)')
    ax1.plot(dy_lat_avg, dy_tokens, color='#2ecc71', linestyle='-', marker='^',
             markersize=8, linewidth=2, label='Dynamic (3 cycles avg)')
    ax1.plot(dy_lat_worst, dy_tokens, color='darkgreen', linestyle=':', linewidth=1,
             marker='^', markersize=6, alpha=0.7, label='Dynamic (6 cycles)')

    # Annotate tool counts
    for i, tc in enumerate(tool_counts):
        if tc in [10, 50, 100, 200]:
            ax1.annotate(f"{tc}", (fc_latency[i], fc_tokens[i]),
                        textcoords="offset points", xytext=(5, 5), fontsize=8, color='#e74c3c')
            ax1.annotate(f"{tc}", (st_latency[i], st_tokens[i]),
                        textcoords="offset points", xytext=(5, 5), fontsize=8, color='#3498db')
            ax1.annotate(f"{tc}", (dy_lat_avg[i], dy_tokens[i]),
                        textcoords="offset points", xytext=(5, 5), fontsize=8, color='#2ecc71')

    ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)

    # =================================
    # Plot 2: Latency by Tool Count (with Dynamic spread)
    # =================================
    ax2 = axes[1]
    ax2.set_title("Latency by Tool Count")
    ax2.set_xlabel("Number of Tools")
    ax2.set_ylabel("Latency (ms)")

    ax2.plot(tool_counts, fc_latency, color='#e74c3c', linestyle='-', marker='s',
             markersize=8, linewidth=2, label='Full Context')
    ax2.plot(tool_counts, st_latency, color='#3498db', linestyle='-', marker='o',
             markersize=8, linewidth=2, label='Static Tools')

    # Dynamic Toolset with spread
    ax2.fill_between(tool_counts, dy_lat_best, dy_lat_worst, color='green', alpha=0.2,
                     label='Dynamic (2-6 cycles)')
    ax2.plot(tool_counts, dy_lat_best, color='lightgreen', linestyle='--', linewidth=1,
             marker='^', markersize=6, alpha=0.7, label='Dynamic (2 cycles)')
    ax2.plot(tool_counts, dy_lat_avg, color='#2ecc71', linestyle='-', marker='^',
             markersize=8, linewidth=2, label='Dynamic (3 cycles avg)')
    ax2.plot(tool_counts, dy_lat_worst, color='darkgreen', linestyle=':', linewidth=1,
             marker='^', markersize=6, alpha=0.7, label='Dynamic (6 cycles)')

    ax2.legend(loc="upper left", fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(left=0)
    ax2.set_ylim(bottom=0)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved figure to: {save_path}")

    if show_plot:
        plt.show()

    return {
        "tool_counts": tool_counts,
        "full_context": {"tokens": fc_tokens, "latency": fc_latency},
        "static_tools": {"tokens": st_tokens, "latency": st_latency},
        "dynamic_toolset": {
            "tokens": dy_tokens,
            "latency_best": dy_lat_best,
            "latency_avg": dy_lat_avg,
            "latency_worst": dy_lat_worst,
        },
    }


def run_crossover_analysis(
    tool_counts: np.ndarray = None,
    save_path: str = None,
    show_plot: bool = True,
) -> dict:
    """
    Analyze crossover points where dynamic becomes favorable.
    """
    if tool_counts is None:
        tool_counts = np.arange(5, 205, 5)

    # Calculate metrics
    static_tokens = static_tools_tokens(tool_counts)
    dynamic_tokens = dynamic_toolset_tokens(tool_counts)
    static_latency = static_tools_latency(tool_counts)
    dynamic_latency = dynamic_toolset_latency(tool_counts)

    # Calculate savings
    token_savings_pct = (static_tokens - dynamic_tokens) / static_tokens * 100
    latency_overhead_pct = (dynamic_latency - static_latency) / static_latency * 100

    # Find crossover points
    # When is token savings > latency overhead?
    net_benefit = token_savings_pct - latency_overhead_pct

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Dynamic Toolset: When Does It Pay Off?", fontsize=14, fontweight='bold')

    # Plot 1: Savings vs Overhead
    ax1 = axes[0]
    ax1.set_title("Token Savings vs Latency Overhead")
    ax1.set_xlabel("Number of Tools")
    ax1.set_ylabel("Percentage (%)")

    ax1.plot(tool_counts, token_savings_pct, 'g-', linewidth=2, label="Token Savings %")
    ax1.plot(tool_counts, latency_overhead_pct, 'r-', linewidth=2, label="Latency Overhead %")
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)

    # Highlight crossover region
    crossover_idx = np.where(token_savings_pct > latency_overhead_pct)[0]
    if len(crossover_idx) > 0:
        crossover_start = tool_counts[crossover_idx[0]]
        ax1.axvline(x=crossover_start, color='purple', linestyle='--', alpha=0.5,
                   label=f"Crossover: {crossover_start} tools")
        ax1.fill_between(tool_counts, 0, 100,
                        where=token_savings_pct > latency_overhead_pct,
                        alpha=0.1, color='green', label="Dynamic Favorable Zone")

    ax1.legend(loc="right")
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(left=0, right=200)
    ax1.set_ylim(-50, 150)

    # Plot 2: Net Benefit
    ax2 = axes[1]
    ax2.set_title("Net Benefit of Dynamic Approach")
    ax2.set_xlabel("Number of Tools")
    ax2.set_ylabel("Net Benefit (Token Savings % - Latency Overhead %)")

    colors = ['green' if x > 0 else 'red' for x in net_benefit]
    ax2.bar(tool_counts, net_benefit, color=colors, alpha=0.7, width=4)
    ax2.axhline(y=0, color='k', linestyle='-', linewidth=1)

    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xlim(left=0, right=205)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved figure to: {save_path}")

    if show_plot:
        plt.show()

    # Find and report crossover
    results = {
        "tool_counts": tool_counts,
        "token_savings_pct": token_savings_pct,
        "latency_overhead_pct": latency_overhead_pct,
        "net_benefit": net_benefit,
    }

    return results


def run_cost_simulation(
    tool_counts: np.ndarray = None,
    queries_per_month: int = 1_000_000,
    cost_per_million_tokens: float = 3.0,  # Claude 3.5 Sonnet input
    save_path: str = None,
    show_plot: bool = True,
) -> dict:
    """
    Simulate monthly costs for each approach.
    """
    if tool_counts is None:
        tool_counts = np.array([10, 20, 30, 40, 50, 75, 100, 150, 200])

    # Calculate tokens per query for each approach
    full_context = full_context_tokens(tool_counts)
    static = static_tools_tokens(tool_counts)
    dynamic = dynamic_toolset_tokens(tool_counts)

    # Monthly costs
    cost_multiplier = queries_per_month * cost_per_million_tokens / 1_000_000

    full_context_cost = full_context * cost_multiplier
    static_cost = static * cost_multiplier
    dynamic_cost = dynamic * cost_multiplier

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f"Monthly API Cost by Approach\n({queries_per_month:,} queries/month @ ${cost_per_million_tokens}/1M tokens)")
    ax.set_xlabel("Number of Tools")
    ax.set_ylabel("Monthly Cost ($)")

    width = 0.25
    x = np.arange(len(tool_counts))

    ax.bar(x - width, full_context_cost, width, label="Full Context", color="#e74c3c", alpha=0.8)
    ax.bar(x, static_cost, width, label="Static Tools", color="#3498db", alpha=0.8)
    ax.bar(x + width, dynamic_cost, width, label="Dynamic Toolset", color="#2ecc71", alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(tool_counts)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved figure to: {save_path}")

    if show_plot:
        plt.show()

    return {
        "tool_counts": tool_counts,
        "full_context_cost": full_context_cost,
        "static_cost": static_cost,
        "dynamic_cost": dynamic_cost,
    }


def run_accuracy_simulation(
    tool_counts: np.ndarray = None,
    save_path: str = None,
    show_plot: bool = True,
) -> dict:
    """
    Simulate and plot accuracy across approaches with spread for dynamic toolset.
    """
    if tool_counts is None:
        tool_counts = np.arange(5, 205, 5)

    # Calculate accuracy for each approach
    fc_accuracy = full_context_accuracy(tool_counts) * 100
    st_accuracy = static_tools_accuracy(tool_counts) * 100

    # Get dynamic range (best/avg/worst based on cycle count)
    dy_best, dy_avg, dy_worst = dynamic_toolset_accuracy_range(tool_counts)
    dy_best *= 100
    dy_avg *= 100
    dy_worst *= 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Accuracy Analysis by Approach (Dynamic shows 2-6 cycle spread)", fontsize=14, fontweight='bold')

    # Plot 1: Accuracy by Tool Count with spread
    ax1 = axes[0]
    ax1.set_title("Accuracy vs Tool Count")
    ax1.set_xlabel("Number of Tools")
    ax1.set_ylabel("Accuracy (%)")

    ax1.plot(tool_counts, fc_accuracy, 'r-', linewidth=2, marker='s',
             markevery=5, markersize=6, label="Full Context")
    ax1.plot(tool_counts, st_accuracy, 'b-', linewidth=2, marker='o',
             markevery=5, markersize=6, label="Static Tools")

    # Dynamic toolset with spread (shaded region)
    ax1.fill_between(tool_counts, dy_worst, dy_best, color='green', alpha=0.2,
                     label="Dynamic (2-6 cycles)")
    ax1.plot(tool_counts, dy_avg, 'g-', linewidth=2, marker='^',
             markevery=5, markersize=6, label="Dynamic (avg 3 cycles)")
    ax1.plot(tool_counts, dy_best, 'g--', linewidth=1, alpha=0.7, label="Dynamic (best: 2 cycles)")
    ax1.plot(tool_counts, dy_worst, 'g:', linewidth=1, alpha=0.7, label="Dynamic (worst: 6 cycles)")

    ax1.axhline(y=95, color='gray', linestyle='--', alpha=0.5, label="95% threshold")
    ax1.legend(loc="lower left", fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 205)
    ax1.set_ylim(75, 100)

    # Add annotations
    ax1.annotate("Lost in Middle", xy=(120, fc_accuracy[0]), fontsize=8, color='red')
    ax1.annotate("Tool overload", xy=(100, 80), fontsize=8, color='blue')

    # Plot 2: Accuracy vs Latency with spread
    ax2 = axes[1]
    ax2.set_title("Accuracy vs Latency Trade-off")
    ax2.set_xlabel("Latency (ms)")
    ax2.set_ylabel("Accuracy (%)")

    # Get latency values
    fc_latency = full_context_latency(tool_counts)
    st_latency = static_tools_latency(tool_counts)

    # Dynamic latency also varies by cycles
    dy_lat_best, dy_lat_avg, dy_lat_worst = dynamic_toolset_latency_range(tool_counts)

    ax2.scatter(fc_latency, fc_accuracy, c='red', s=50, alpha=0.7, label="Full Context")
    ax2.scatter(st_latency, st_accuracy, c='blue', s=50, alpha=0.7, label="Static Tools")

    # Show dynamic spread as error bars (latency AND accuracy vary)
    ax2.scatter(dy_lat_avg, dy_avg, c='green', s=50, alpha=0.7, label="Dynamic (avg)")

    # Draw spread region for dynamic
    # Connect best case points
    ax2.plot(dy_lat_best, dy_best, 'g--', alpha=0.5, linewidth=1, label="Dynamic (2 cycles)")
    ax2.plot(dy_lat_worst, dy_worst, 'g:', alpha=0.5, linewidth=1, label="Dynamic (6 cycles)")

    # Connect lines showing tool count progression
    ax2.plot(fc_latency, fc_accuracy, 'r-', alpha=0.3)
    ax2.plot(st_latency, st_accuracy, 'b-', alpha=0.3)
    ax2.plot(dy_lat_avg, dy_avg, 'g-', alpha=0.3)

    # Annotate key tool counts
    for i, tc in enumerate([10, 50, 100, 200]):
        idx = np.where(tool_counts == tc)[0]
        if len(idx) > 0:
            idx = idx[0]
            ax2.annotate(f"{tc}", (st_latency[idx], st_accuracy[idx]),
                        textcoords="offset points", xytext=(5, 0), fontsize=7, color='blue')

    ax2.legend(loc="lower left", fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(75, 100)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved figure to: {save_path}")

    if show_plot:
        plt.show()

    return {
        "tool_counts": tool_counts,
        "full_context_accuracy": fc_accuracy,
        "static_tools_accuracy": st_accuracy,
        "dynamic_toolset_accuracy_best": dy_best,
        "dynamic_toolset_accuracy_avg": dy_avg,
        "dynamic_toolset_accuracy_worst": dy_worst,
    }


def run_cycle_impact_simulation(
    save_path: str = None,
    show_plot: bool = True,
) -> dict:
    """
    Detailed analysis of how cycle count affects dynamic toolset performance.
    Shows accuracy AND latency degradation as cycles increase.
    """
    cycles = np.arange(1, 10)
    tool_counts_example = np.array([50])  # Example with 50 tools

    # Calculate metrics for each cycle count
    accuracies = []
    latencies = []
    for c in cycles:
        acc = dynamic_toolset_accuracy(tool_counts_example, cycles=c)[0] * 100
        lat = dynamic_toolset_latency(tool_counts_example, cycles=c)[0]
        accuracies.append(acc)
        latencies.append(lat)

    accuracies = np.array(accuracies)
    latencies = np.array(latencies)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Impact of Discovery Cycles on Dynamic Toolset Performance", fontsize=14, fontweight='bold')

    # Plot 1: Accuracy by cycle count
    ax1 = axes[0]
    ax1.set_title("Accuracy Degradation per Cycle")
    ax1.set_xlabel("Number of Cycles")
    ax1.set_ylabel("Accuracy (%)")

    ax1.bar(cycles, accuracies, color='green', alpha=0.7, edgecolor='darkgreen')
    ax1.axhline(y=95, color='gray', linestyle='--', alpha=0.5, label="95% threshold")
    ax1.axhline(y=90, color='orange', linestyle='--', alpha=0.5, label="90% threshold")

    # Annotate each bar
    for i, (c, acc) in enumerate(zip(cycles, accuracies)):
        ax1.annotate(f"{acc:.1f}%", (c, acc + 0.5), ha='center', fontsize=8)

    ax1.set_ylim(75, 100)
    ax1.set_xticks(cycles)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: Latency by cycle count
    ax2 = axes[1]
    ax2.set_title("Latency Increase per Cycle")
    ax2.set_xlabel("Number of Cycles")
    ax2.set_ylabel("Latency (ms)")

    ax2.bar(cycles, latencies, color='orange', alpha=0.7, edgecolor='darkorange')

    # Annotate each bar
    for i, (c, lat) in enumerate(zip(cycles, latencies)):
        ax2.annotate(f"{lat:.0f}", (c, lat + 100), ha='center', fontsize=8)

    ax2.set_xticks(cycles)
    ax2.grid(True, alpha=0.3, axis='y')

    # Plot 3: Accuracy vs Latency trade-off
    ax3 = axes[2]
    ax3.set_title("Accuracy-Latency Trade-off by Cycles")
    ax3.set_xlabel("Latency (ms)")
    ax3.set_ylabel("Accuracy (%)")

    # Color code by cycle count
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(cycles)))
    scatter = ax3.scatter(latencies, accuracies, c=cycles, cmap='RdYlGn_r',
                          s=100, edgecolors='black', linewidths=1)

    # Label each point with cycle count
    for c, lat, acc in zip(cycles, latencies, accuracies):
        ax3.annotate(f"{c}", (lat, acc), textcoords="offset points",
                    xytext=(5, 5), fontsize=9, fontweight='bold')

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax3)
    cbar.set_label('Cycles')

    # Add reference lines for static tools at 50 tools
    st_acc = static_tools_accuracy(tool_counts_example)[0] * 100
    st_lat = static_tools_latency(tool_counts_example)[0]
    ax3.axhline(y=st_acc, color='blue', linestyle='--', alpha=0.5, label=f"Static (50 tools): {st_acc:.0f}%")
    ax3.axvline(x=st_lat, color='blue', linestyle=':', alpha=0.5)
    ax3.scatter([st_lat], [st_acc], c='blue', s=150, marker='s', label="Static Tools @ 50")

    ax3.legend(loc='lower left', fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(75, 100)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved figure to: {save_path}")

    if show_plot:
        plt.show()

    return {
        "cycles": cycles,
        "accuracies": accuracies,
        "latencies": latencies,
    }


def run_3d_tradeoff_simulation(
    tool_counts: np.ndarray = None,
    save_path: str = None,
    show_plot: bool = True,
) -> dict:
    """
    Create comprehensive 3D trade-off visualization:
    X = Latency, Y = Tokens, Color/Size = Accuracy, Lines = Tool counts
    Shows spread for Dynamic Toolset based on cycle count (2-6 cycles)
    """
    if tool_counts is None:
        tool_counts = np.array([10, 20, 30, 40, 50, 75, 100, 150, 200])

    # Calculate all metrics
    fc_tokens = full_context_tokens(tool_counts)
    fc_latency = full_context_latency(tool_counts)
    fc_accuracy = full_context_accuracy(tool_counts) * 100

    st_tokens = static_tools_tokens(tool_counts)
    st_latency = static_tools_latency(tool_counts)
    st_accuracy = static_tools_accuracy(tool_counts) * 100

    dy_tokens = dynamic_toolset_tokens(tool_counts)

    # Get dynamic ranges for different cycle counts
    dy_lat_best, dy_lat_avg, dy_lat_worst = dynamic_toolset_latency_range(tool_counts)
    dy_acc_best, dy_acc_avg, dy_acc_worst = dynamic_toolset_accuracy_range(tool_counts)
    dy_acc_best *= 100
    dy_acc_avg *= 100
    dy_acc_worst *= 100

    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_title("Complete Trade-off: Tokens vs Latency vs Accuracy\n(bubble size = accuracy, Dynamic shows 2-6 cycle spread)",
                 fontsize=12, fontweight='bold')
    ax.set_xlabel("Latency (ms)")
    ax.set_ylabel("Tokens")

    # Normalize accuracy for bubble sizing (scale to reasonable size)
    def acc_to_size(acc):
        return ((acc - 75) / 25) * 300 + 50  # Scale 75-100% to 50-350 pixel size

    # Plot Full Context and Static Tools
    scatter_fc = ax.scatter(fc_latency, fc_tokens, s=acc_to_size(fc_accuracy),
                            c='red', alpha=0.6, edgecolors='darkred', linewidths=1.5,
                            label='Full Context')
    scatter_st = ax.scatter(st_latency, st_tokens, s=acc_to_size(st_accuracy),
                            c='blue', alpha=0.6, edgecolors='darkblue', linewidths=1.5,
                            label='Static Tools')

    # Plot Dynamic Toolset with spread - show best, avg, and worst cases
    # Best case (2 cycles) - lighter green, larger bubbles (higher accuracy)
    scatter_dy_best = ax.scatter(dy_lat_best, dy_tokens, s=acc_to_size(dy_acc_best),
                                  c='lightgreen', alpha=0.5, edgecolors='green', linewidths=1,
                                  label='Dynamic (2 cycles)')

    # Average case (3 cycles) - medium green
    scatter_dy_avg = ax.scatter(dy_lat_avg, dy_tokens, s=acc_to_size(dy_acc_avg),
                                 c='green', alpha=0.6, edgecolors='darkgreen', linewidths=1.5,
                                 label='Dynamic (3 cycles)')

    # Worst case (6 cycles) - darker, smaller bubbles (lower accuracy)
    scatter_dy_worst = ax.scatter(dy_lat_worst, dy_tokens, s=acc_to_size(dy_acc_worst),
                                   c='darkgreen', alpha=0.4, edgecolors='black', linewidths=1,
                                   label='Dynamic (6 cycles)')

    # Connect points showing tool count progression
    ax.plot(fc_latency, fc_tokens, 'r--', alpha=0.3, linewidth=1)
    ax.plot(st_latency, st_tokens, 'b--', alpha=0.3, linewidth=1)

    # Connect dynamic spread with horizontal lines to show the range
    for i in range(len(tool_counts)):
        ax.plot([dy_lat_best[i], dy_lat_worst[i]], [dy_tokens[i], dy_tokens[i]],
                'g-', alpha=0.3, linewidth=2)

    # Label key tool counts
    for i, tc in enumerate(tool_counts):
        if tc in [10, 50, 100, 200]:
            ax.annotate(f"{tc}", (st_latency[i], st_tokens[i]),
                       textcoords="offset points", xytext=(8, 5), fontsize=8,
                       color='blue', fontweight='bold')
            # Label at the average dynamic position
            ax.annotate(f"{tc}", (dy_lat_avg[i], dy_tokens[i]),
                       textcoords="offset points", xytext=(0, 10), fontsize=8,
                       color='green', fontweight='bold')

    # Add legend for approaches
    legend1 = ax.legend(loc='upper right', title='Approach', fontsize=9)
    ax.add_artist(legend1)

    # Create manual legend for bubble sizes
    for acc in [80, 85, 90, 95]:
        ax.scatter([], [], s=acc_to_size(acc), c='gray', alpha=0.5,
                  label=f'{acc}%')
    ax.legend(loc='upper left', title='Accuracy', scatterpoints=1, fontsize=9)
    ax.add_artist(legend1)

    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, dy_lat_worst.max() * 1.1)
    ax.set_ylim(0, fc_tokens.max() * 1.1)

    # Add zone annotations
    ax.annotate("IDEAL ZONE\n(low tokens, low latency,\nhigh accuracy)",
               xy=(1800, 4000), fontsize=10, color='green',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

    ax.annotate("Dynamic spread:\n2 cycles (fast) → 6 cycles (slow)",
               xy=(4500, 1500), fontsize=9, color='darkgreen',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved figure to: {save_path}")

    if show_plot:
        plt.show()

    return {
        "tool_counts": tool_counts,
        "full_context": {"tokens": fc_tokens, "latency": fc_latency, "accuracy": fc_accuracy},
        "static_tools": {"tokens": st_tokens, "latency": st_latency, "accuracy": st_accuracy},
        "dynamic_toolset": {
            "tokens": dy_tokens,
            "latency_best": dy_lat_best, "latency_avg": dy_lat_avg, "latency_worst": dy_lat_worst,
            "accuracy_best": dy_acc_best, "accuracy_avg": dy_acc_avg, "accuracy_worst": dy_acc_worst,
        },
    }


def print_summary_table(tool_counts: np.ndarray = None):
    """Print a summary table of all metrics including accuracy with cycle spread."""
    if tool_counts is None:
        tool_counts = np.array([10, 20, 30, 50, 100, 200])

    print("\n" + "=" * 140)
    print("SIMULATION SUMMARY: TOKENS, LATENCY & ACCURACY BY APPROACH")
    print("Dynamic Toolset shows range based on cycle count (2-6 cycles)")
    print("=" * 140)

    print(f"\n{'Tools':>6} | {'Full Context':^26} | {'Static Tools':^26} | {'Dynamic Toolset (2-6 cycles)':^50}")
    print(f"{'':>6} | {'Tokens':>8} {'Latency':>8} {'Acc':>6} | {'Tokens':>8} {'Latency':>8} {'Acc':>6} | {'Tokens':>8} {'Lat(min)':>9} {'Lat(max)':>9} {'Acc(best)':>10} {'Acc(worst)':>11}")
    print("-" * 140)

    for tc in tool_counts:
        tc_arr = np.array([tc])
        fc_tok = full_context_tokens(tc_arr)[0]
        fc_lat = full_context_latency(tc_arr)[0]
        fc_acc = full_context_accuracy(tc_arr)[0] * 100
        st_tok = static_tools_tokens(tc_arr)[0]
        st_lat = static_tools_latency(tc_arr)[0]
        st_acc = static_tools_accuracy(tc_arr)[0] * 100
        dy_tok = dynamic_toolset_tokens(tc_arr)[0]

        # Get ranges for dynamic
        dy_lat_best, dy_lat_avg, dy_lat_worst = dynamic_toolset_latency_range(tc_arr)
        dy_acc_best, dy_acc_avg, dy_acc_worst = dynamic_toolset_accuracy_range(tc_arr)

        print(f"{tc:>6} | {fc_tok:>8,.0f} {fc_lat:>6,.0f}ms {fc_acc:>5.1f}% | "
              f"{st_tok:>8,.0f} {st_lat:>6,.0f}ms {st_acc:>5.1f}% | "
              f"{dy_tok:>8,.0f} {dy_lat_best[0]:>7,.0f}ms {dy_lat_worst[0]:>7,.0f}ms "
              f"{dy_acc_best[0]*100:>8.1f}% {dy_acc_worst[0]*100:>9.1f}%")

    print("-" * 140)

    # Cycle impact summary
    print("\nCYCLE IMPACT (at 50 tools):")
    print("-" * 60)
    for c in [2, 3, 4, 5, 6]:
        tc_arr = np.array([50])
        acc = dynamic_toolset_accuracy(tc_arr, cycles=c)[0] * 100
        lat = dynamic_toolset_latency(tc_arr, cycles=c)[0]
        print(f"  {c} cycles: {lat:,.0f}ms latency, {acc:.1f}% accuracy")
    print("-" * 60)

    # Find crossover point
    test_range = np.arange(5, 300, 1)
    static_tokens = static_tools_tokens(test_range)
    dynamic_tokens = dynamic_toolset_tokens(test_range)
    static_latency = static_tools_latency(test_range)
    dynamic_latency = dynamic_toolset_latency(test_range)

    token_savings = (static_tokens - dynamic_tokens) / static_tokens * 100
    latency_overhead = (dynamic_latency - static_latency) / static_latency * 100

    # Find where token savings exceeds latency overhead
    favorable_idx = np.where(token_savings > latency_overhead)[0]
    if len(favorable_idx) > 0:
        crossover = test_range[favorable_idx[0]]
        print(f"\n>> CROSSOVER POINT: Dynamic becomes net favorable at {crossover} tools")

    # Find where latencies are within 10%
    latency_close_idx = np.where(latency_overhead < 10)[0]
    if len(latency_close_idx) > 0:
        latency_match = test_range[latency_close_idx[0]]
        print(f">> LATENCY PARITY: Dynamic latency within 10% of static at {latency_match} tools")

    print("=" * 90 + "\n")


def main():
    """Run all simulations."""
    import os

    # Use non-interactive backend for saving plots
    import matplotlib
    matplotlib.use('Agg')

    # Create output directory
    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("Running MCP Context Loading Simulations...")
    print("-" * 50)

    # Print summary table
    print_summary_table()

    # Run main simulation
    print("\n1. Running Token vs Latency simulation...")
    run_simulation(
        save_path=os.path.join(output_dir, "plot_tokens_vs_latency.png"),
        show_plot=False,
    )

    # Run crossover analysis
    print("\n2. Running crossover analysis...")
    run_crossover_analysis(
        save_path=os.path.join(output_dir, "plot_crossover_analysis.png"),
        show_plot=False,
    )

    # Run cost simulation
    print("\n3. Running cost simulation...")
    run_cost_simulation(
        save_path=os.path.join(output_dir, "plot_monthly_cost.png"),
        show_plot=False,
    )

    # Run accuracy simulation
    print("\n4. Running accuracy simulation (with cycle spread)...")
    run_accuracy_simulation(
        save_path=os.path.join(output_dir, "plot_accuracy_analysis.png"),
        show_plot=False,
    )

    # Run cycle impact simulation
    print("\n5. Running cycle impact analysis...")
    run_cycle_impact_simulation(
        save_path=os.path.join(output_dir, "plot_cycle_impact.png"),
        show_plot=False,
    )

    # Run 3D trade-off simulation
    print("\n6. Running complete trade-off visualization...")
    run_3d_tradeoff_simulation(
        save_path=os.path.join(output_dir, "plot_complete_tradeoff.png"),
        show_plot=False,
    )

    print("\nSimulations complete! Check the generated plots:")
    print(f"  - {output_dir}/plot_tokens_vs_latency.png")
    print(f"  - {output_dir}/plot_crossover_analysis.png")
    print(f"  - {output_dir}/plot_monthly_cost.png")
    print(f"  - {output_dir}/plot_accuracy_analysis.png")
    print(f"  - {output_dir}/plot_cycle_impact.png")
    print(f"  - {output_dir}/plot_complete_tradeoff.png")


if __name__ == "__main__":
    main()
