# Effective Context Engineering for AI Agents

**Source**: [Anthropic Engineering Blog](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

## Overview

Anthropic's engineering team outlines best practices for managing agent context efficiently, contrasting ineffective "context stuffing" approaches with more sophisticated tool-based patterns.

## Context Stuffing vs Tool Calling

### Context Stuffing (Anti-pattern)
- Loads exhaustive information upfront
- Creates "context pollution" where models struggle to identify relevant details
- Wastes finite attention budget on irrelevant information
- Analogous to memorizing an entire encyclopedia

### Tool Calling (Recommended)
- Agents dynamically retrieve data at runtime
- Uses lightweight references (file paths, queries, links)
- Mirrors human cognition: external systems for on-demand retrieval
- Preserves context budget for reasoning

## Recommended Patterns

### 1. System Prompts at the Right Altitude
Avoid extremes:
- Too specific: brittle, hardcoded logic
- Too vague: insufficient guidance

Provide direction specific enough to guide behavior while remaining flexible for model heuristics.

### 2. Minimal Viable Tool Sets
Key principle: "If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."

### 3. Progressive Disclosure
Allow agents to explore incrementally, discovering context through interaction rather than receiving everything upfront.

### 4. Long-Horizon Task Management
- **Compaction**: Summarize and reset context windows
- **Structured note-taking**: Persist critical information externally
- **Sub-agent architectures**: Delegate focused tasks to specialists

## Guiding Principle

Find the smallest set of high-signal tokens that maximizes desired outcomes.

## Relevance to This Project

These patterns directly inform our implementation strategy. The contrast between context stuffing and tool calling forms the foundation of our comparative benchmarking approach.
