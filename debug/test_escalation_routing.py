from src.config.tier_matrix import get_escalation_target

cases = [
    ("Platinum", "export_bug"),
    ("Platinum", "cancellation_risk"),
    ("Gold", "cancellation_risk"),
    ("Diamond", "billing_dispute"),
    ("Gold", "password_reset"),  # no override -> generic fallback
]

for tier, category in cases:
    target = get_escalation_target(tier, category)
    print(f"{tier:10} + {category:20} -> {target}")