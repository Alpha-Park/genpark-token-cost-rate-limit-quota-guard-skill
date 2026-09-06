"""
Demonstration of genpark-token-cost-rate-limit-quota-guard-skill
"""

from client import TokenCostQuotaGuardClient

def main():
    guard = TokenCostQuotaGuardClient()
    guard.set_tenant_budget("team_alpha", monthly_budget_usd=10.0)

    # Check rate limit before call
    rl = guard.check_rate_limit("team_alpha", max_rpm=10, max_tpm=5000)
    print("Rate limit check:", rl)

    # Record inference
    res = guard.record_usage(
        tenant_id="team_alpha",
        model="claude-3-5-sonnet",
        prompt_tokens=1500,
        completion_tokens=600
    )
    print("\n=== TOKEN USAGE & COST REPORT ===")
    print(f"Call Cost: ${res['call_cost_usd']}")
    print(f"Cumulative Spend: ${res['cumulative_spend_usd']} / ${res['budget_usd']}")
    print(f"Remaining Budget: ${res['budget_remaining_usd']}")
    print(f"Budget Exceeded: {res['budget_exceeded']}")

if __name__ == "__main__":
    main()
