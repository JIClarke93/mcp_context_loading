# RAG vs Function Calling for LLM Agents

**Source**: [GetStream Blog](https://getstream.io/blog/rag-function-calling/)

## Overview

This article distinguishes between Retrieval-Augmented Generation (RAG) and function calling patterns for LLM agents, clarifying when each approach is appropriate and how they complement each other.

## RAG: Retrieval-Augmented Generation

### Best For
Accessing large domain-specific datasets and real-time information that wasn't in the model's training data.

### Use Cases
- Medical studies, financial data, product catalogs
- Private knowledge bases and company documentation
- Research assistants needing current context

### Process Flow
Query embedding → Vector database search → Retrieved context → LLM response

### Characteristics
- Higher latency (retrieval step adds overhead)
- Flexible for varied queries
- Read-heavy database workloads

## Function Calling

### Best For
Executing predefined operations and structured actions with system integration.

### Use Cases
- Calculations (mortgages, financial transactions)
- Booking systems (flights, orders)
- Database writes and API calls

### Process Flow
Model determines function need → Execute function → Pass results to LLM

### Characteristics
- Lower latency (direct execution)
- Best for known operations
- Transactional database operations

## Comparison Matrix

| Aspect | RAG | Function Calling |
|--------|-----|------------------|
| **Latency** | Higher | Lower |
| **Flexibility** | Varied queries | Known operations |
| **Database Pattern** | Read-heavy | Transactional |
| **Context Source** | External datasets | Structured actions |

## Hybrid Approach

The recommended pattern combines both: use RAG to retrieve context (like real-time product availability) while function calling executes actions (like processing orders). This maximizes currency of information while enabling operational capability.

## Relevance to This Project

Our database access benchmark should measure both patterns independently and in combination. The distinction between read-heavy (RAG) and transactional (function calling) operations suggests we need different query types in our test suite.
