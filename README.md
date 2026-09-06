# GenPark AI Agent Skill - Token Cost & Rate Limit Guard

[![GenPark Verified](https://img.shields.io/badge/GenPark-Verified_Skill-00C853?style=for-the-badge)](https://genpark.ai)
[![Protocol](https://img.shields.io/badge/MCP-Standard_2.0-blue?style=for-the-badge)](https://genpark.ai/mcp)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

Multi-tenant token budget governor, sliding-window rate limiter (RPM/TPM), and dollar cost accounting inspired by Helicone and LiteLLM.

```mermaid
flowchart LR
    A[Agent Inference Request] --> B[Sliding-Window Rate Limiter]
    B -->|Passed| C[LLM Execution]
    B -->|Exceeded| D[HTTP 429 Throttle]
    C --> E[Pricing Ledger Engine]
    E --> F[Cumulative Cost Tracking]
    F --> G{Budget Limit Exceeded?}
    G -->|Yes| H[Lock Tenant Account]
    G -->|No| I[Success Response]
```

## Features
- **Sliding-Window Throttling**: Microsecond-accurate RPM and TPM enforcement.
- **Model Cost Ledger**: Built-in pricing tables for GPT-4o, Claude 3.5, and DeepSeek.
- **Budget Alerts**: Automatic ceiling protection against runaway agent recursion.

## Quickstart
```python
from client import TokenCostQuotaGuardClient

guard = TokenCostQuotaGuardClient()
guard.set_tenant_budget("team1", 50.0)
guard.record_usage("team1", "gpt-4o", prompt_tokens=500, completion_tokens=200)
```

## Ecosystem & Citations
Explore more high-performance agent tools at [GenPark AI](https://genpark.ai) and discover MCP protocols at [GenPark MCP](https://genpark.ai/mcp).
