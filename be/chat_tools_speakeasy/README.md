# Dynamic Toolset Evaluation: When Do We Need It?

## The Core Question

> **At what point does the number of tools make static toolsets impractical, requiring a switch to the Speakeasy dynamic toolset approach?**

This analysis evaluates trade-offs across **three dimensions**:
- **Tokens** (cost)
- **Latency** (speed)
- **Accuracy** (quality)

---

## Key Finding: Dynamic Toolset Has Variable Performance

The critical insight from our simulation is that **Dynamic Toolset performance varies based on query complexity** (number of discovery cycles):

| Cycles | Latency | Accuracy | When This Happens |
|--------|---------|----------|-------------------|
| 2 | 2,406ms | 91.2% | Simple query, tool found immediately |
| 3 | 3,508ms | 89.1% | Average case |
| 4 | 4,611ms | 87.8% | Needs refinement |
| 5 | 5,714ms | 86.4% | Complex multi-tool query |
| 6 | 6,816ms | 85.1% | Worst case: multiple retries |

This means Dynamic Toolset is **not a single point** but a **spread** depending on how many iterations the discovery process takes.

---

## Simulation Results

Run `python -m be.chat_tools_speakeasy.simulation` to generate plots.

### Summary Table (Dynamic shows 2-6 cycle range)

| Tools | Full Context | | | Static Tools | | | Dynamic Toolset (2-6 cycles) | | |
|-------|-------------|---------|-----|--------------|---------|-----|-----------------|-----------------|-----|
| | Tokens | Latency | Acc | Tokens | Latency | Acc | Tokens | Latency Range | Acc Range |
|-------|---------|---------|-----|----------|---------|-----|----------|-----------------|-----------|
| 10 | 36,500 | 2,625ms | 83% | 3,300 | 1,565ms | **98%** | 2,055 | 2,406-6,816ms | 85-91% |
| 30 | 36,500 | 2,625ms | 83% | 5,300 | 1,665ms | 94% | 2,055 | 2,406-6,816ms | 85-91% |
| 50 | 36,500 | 2,625ms | 83% | 7,300 | 1,765ms | 88% | 2,055 | 2,406-6,816ms | 85-91% |
| 100 | 36,500 | 2,625ms | 83% | 12,300 | 2,015ms | 78% | 2,055 | 2,406-6,816ms | **85-90%** |
| 200 | 36,500 | 2,625ms | 83% | 22,300 | 2,515ms | 78% | 2,055 | 2,406-6,816ms | **85-90%** |

### Key Observations

1. **Token Usage**: Dynamic wins massively (2,055 tokens vs 12,300-22,300 for Static at high tool counts)
2. **Latency**: Static wins at low tool counts, but Dynamic's best case (2 cycles) is competitive
3. **Accuracy**: Static wins below ~50 tools, Dynamic wins above due to tool overload degradation

---

## The Three Failure Modes

### Full Context: "Lost in the Middle" (83% accuracy)

```
Problem: Large context (36K tokens) causes retrieval failures
- Model struggles to find info buried in middle of context
- Irrelevant data dilutes the signal
- Fixed at 83% regardless of tool count
- Only viable for small datasets (<5K tokens)
```

### Static Tools: Tool Overload (98% → 78% accuracy)

```
Problem: Too many tool schemas overwhelm the model
- Degrades after 15 tools (0.3% per additional tool)
- Selection confusion: wrong tool chosen
- Attention dilution across schemas
- Bottoms out at 78% around 80+ tools
```

### Dynamic Toolset: Cycle Compounding (91% → 85% accuracy)

```
Problem: Each discovery cycle can introduce errors
- 2% base discovery failure rate
- 1.5% compounding error per cycle
- More cycles = more chances for mistakes
- But stays relatively stable (85-91%) regardless of tool count
```

---

## Generated Plots

### 1. `plot_tokens_vs_latency.png`
**Main trade-off visualization**
- Left: Tokens vs Latency scatter (Dynamic shows green shaded spread for 2-6 cycles)
- Right: Latency by Tool Count (Dynamic shows spread band)
- Tool count labels at 10, 50, 100, 200

### 2. `plot_accuracy_analysis.png`
**Accuracy with cycle spread**
- Left: Accuracy vs Tool Count
  - Static (blue): Degrades from 98% to 78%
  - Dynamic (green shaded): Band from best (2 cycles) to worst (6 cycles)
  - Full Context (red): Flat at 83%
- Right: Accuracy vs Latency trade-off

### 3. `plot_cycle_impact.png`
**Deep dive into cycle effects**
- Bar chart: Accuracy degradation per cycle (1-9 cycles)
- Bar chart: Latency increase per cycle
- Scatter: Accuracy vs Latency trade-off by cycle count

### 4. `plot_complete_tradeoff.png`
**3D bubble visualization**
- X: Latency, Y: Tokens, Bubble size: Accuracy
- Dynamic shows three bubble sets (2, 3, 6 cycles)
- Horizontal lines connect best→worst case for each tool count

### 5. `plot_crossover_analysis.png`
**Break-even analysis**
- Token savings % vs Latency overhead %
- Net benefit calculation
- Crossover point: ~85 tools

### 6. `plot_monthly_cost.png`
**Cost at scale** (1M queries/month @ $3/1M tokens)

---

## Decision Framework

### Crossover Point: ~85 Tools

At 85 tools, Dynamic Toolset becomes **net favorable** when weighing token savings against latency overhead.

### When to Use Each Approach

| Tool Count | Best Choice | Rationale |
|------------|-------------|-----------|
| **1-15** | Static Tools | 98% accuracy, fast, acceptable tokens |
| **16-40** | Static Tools | Still 90%+ accuracy, best latency |
| **41-70** | **Depends** | Static accuracy degrading, evaluate Dynamic |
| **71-100** | Dynamic Toolset | Static drops to 78%, Dynamic stable at 85-91% |
| **100+** | Dynamic Toolset | Static unusable, Dynamic is only option |

### The Deciding Factors

| Your Priority | Recommendation |
|---------------|----------------|
| **Maximize accuracy** | Static (<50 tools) or Dynamic (50+) |
| **Minimize tokens/cost** | Dynamic (always) |
| **Minimize latency** | Static (always) |
| **Simple queries** | Dynamic wins (2-cycle best case beats Static at high tool counts) |
| **Complex queries** | Static wins at low counts, Dynamic at high counts |

---

## Model Parameters

Adjustable in `simulation.py`:

```python
# Token parameters
TOKENS_PER_TOOL_SCHEMA = 100     # Average tokens per tool definition
ENTITIES_PER_TYPE = 100          # Database entities per type

# Latency parameters
LLM_BASE_LATENCY = 800           # Base inference time (ms)
TOOL_CALL_LATENCY = 200          # Per tool call overhead (ms)

# Accuracy parameters
CONTEXT_SIZE_ACCURACY_THRESHOLD = 20000  # "Lost in middle" threshold
TOOL_COUNT_ACCURACY_THRESHOLD = 15       # Tool overload starts
TOOL_COUNT_ACCURACY_DECAY = 0.003        # 0.3% loss per excess tool

# Dynamic cycle parameters
DYNAMIC_CYCLES_MIN = 2           # Best case cycles
DYNAMIC_CYCLES_AVG = 3           # Average cycles
DYNAMIC_CYCLES_MAX = 6           # Worst case cycles
DISCOVERY_CYCLE_ERROR_RATE = 0.015  # 1.5% error per cycle
```

---

## Files

```
chat_tools_speakeasy/
├── README.md                      # This document
├── simulation.py                  # NumPy/Matplotlib simulation (~1000 lines)
├── plot_tokens_vs_latency.png     # Main trade-off (2 panels)
├── plot_accuracy_analysis.png     # Accuracy with cycle spread
├── plot_cycle_impact.png          # Cycle-by-cycle breakdown
├── plot_complete_tradeoff.png     # 3D bubble chart
├── plot_crossover_analysis.png    # Break-even analysis
└── plot_monthly_cost.png          # Cost comparison
```

---

## Summary

**The Speakeasy Dynamic Toolset approach is valuable, but not universally better.**

| Dimension | Winner |
|-----------|--------|
| Tokens | Dynamic (always) |
| Latency | Static (always) |
| Accuracy (<50 tools) | Static |
| Accuracy (50+ tools) | Dynamic |
| Scalability | Dynamic |
| Predictability | Static (no cycle variance) |

**Bottom line**: Switch to Dynamic when tool count exceeds ~50-70, or when token costs become prohibitive. For small toolsets (<30), Static Tools remains optimal.

---

*Based on Speakeasy research: [How We Reduced Token Usage by 100x](https://www.speakeasy.com/blog/how-we-reduced-token-usage-by-100x-dynamic-toolsets-v2)*
