from tests.golden_dataset import GOLDEN_TICKETS

print("Total tickets:", len(GOLDEN_TICKETS))

categories = {}
tiers = {}
outcomes = {}
for t in GOLDEN_TICKETS:
    categories[t["expected_category"]] = categories.get(t["expected_category"], 0) + 1
    tiers[t["tier"]] = tiers.get(t["tier"], 0) + 1
    outcomes[t["expected_outcome"]] = outcomes.get(t["expected_outcome"], 0) + 1

print("\nCategory distribution:")
for k, v in categories.items():
    print(f"  {k}: {v}")

print("\nTier distribution:")
for k, v in tiers.items():
    print(f"  {k}: {v}")

print("\nOutcome distribution:")
for k, v in outcomes.items():
    print(f"  {k}: {v}")
    