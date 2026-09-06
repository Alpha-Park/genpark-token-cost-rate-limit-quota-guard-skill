"""
Multi-tenant Token Cost, Budget Tracker and Sliding-Window Rate Limiter.
Zero external dependencies, standard library only.
"""

import time
from typing import Dict, List, Any, Optional

class TokenCostQuotaGuardClient:
    """
    Manages multi-tenant token consumption, rate limits (RPM, TPM),
    sliding-window throttles, and dollar-denominated model cost accounting.
    """

    MODEL_PRICING = {
        "gpt-4o": {"input_per_million": 2.50, "output_per_million": 10.00},
        "gpt-4o-mini": {"input_per_million": 0.15, "output_per_million": 0.60},
        "claude-3-5-sonnet": {"input_per_million": 3.00, "output_per_million": 15.00},
        "deepseek-v3": {"input_per_million": 0.14, "output_per_million": 0.28}
    }

    def __init__(self):
        # tenant_id -> list of (timestamp, tokens, cost)
        self.usage_history = {}
        # tenant_id -> budget in USD
        self.budgets = {}

    def set_tenant_budget(self, tenant_id: str, monthly_budget_usd: float):
        """Sets monthly dollar spending ceiling for a tenant."""
        self.budgets[tenant_id] = monthly_budget_usd

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates precise dollar cost of an inference call."""
        pricing = self.MODEL_PRICING.get(model, {"input_per_million": 1.0, "output_per_million": 2.0})
        in_cost = (prompt_tokens / 1_000_000.0) * pricing["input_per_million"]
        out_cost = (completion_tokens / 1_000_000.0) * pricing["output_per_million"]
        return round(in_cost + out_cost, 6)

    def check_rate_limit(self, tenant_id: str, max_rpm: int = 60, max_tpm: int = 100_000) -> Dict[str, Any]:
        """
        Evaluates sliding-window (last 60 seconds) request and token throughput.
        """
        now = time.time()
        window_start = now - 60.0

        history = self.usage_history.get(tenant_id, [])
        # Filter to active window
        active = [rec for rec in history if rec["timestamp"] >= window_start]
        self.usage_history[tenant_id] = active

        current_rpm = len(active)
        current_tpm = sum(rec["tokens"] for rec in active)

        rpm_exceeded = current_rpm >= max_rpm
        tpm_exceeded = current_tpm >= max_tpm

        allowed = not (rpm_exceeded or tpm_exceeded)
        return {
            "allowed": allowed,
            "tenant_id": tenant_id,
            "current_rpm": current_rpm,
            "max_rpm": max_rpm,
            "current_tpm": current_tpm,
            "max_tpm": max_tpm,
            "throttled_reason": "RPM_LIMIT" if rpm_exceeded else ("TPM_LIMIT" if tpm_exceeded else None)
        }

    def record_usage(self, tenant_id: str, model: str, prompt_tokens: int, completion_tokens: int) -> Dict[str, Any]:
        """
        Records completed call, updates balance, and checks budget overages.
        """
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        total_tokens = prompt_tokens + completion_tokens
        record = {
            "timestamp": time.time(),
            "model": model,
            "tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": cost
        }

        if tenant_id not in self.usage_history:
            self.usage_history[tenant_id] = []
        self.usage_history[tenant_id].append(record)

        # Calculate cumulative spend
        total_spend = sum(rec["cost_usd"] for rec in self.usage_history[tenant_id])
        budget = self.budgets.get(tenant_id, float("inf"))

        return {
            "tenant_id": tenant_id,
            "call_cost_usd": cost,
            "cumulative_spend_usd": round(total_spend, 4),
            "budget_usd": budget,
            "budget_remaining_usd": round(max(0.0, budget - total_spend), 4),
            "budget_exceeded": total_spend >= budget
        }
