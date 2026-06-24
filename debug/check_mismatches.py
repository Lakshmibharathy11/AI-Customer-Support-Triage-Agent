import json

with open("eval_results/golden_run_results.json", encoding="utf-8") as f:
    results = json.load(f)

print("=== CATEGORY MISMATCHES ===")
for r in results:
    if r.get("actual_category") != r.get("expected_category"):
        print(f"{r['ticket_id']}: expected={r.get('expected_category')} actual={r.get('actual_category')}")
        print(f"  Question: {r['question'][:80]}")

print()
print("=== OUTCOME MISMATCHES ===")
for r in results:
    if r.get("actual_outcome") != r.get("expected_outcome"):
        print(f"{r['ticket_id']}: expected={r.get('expected_outcome')} actual={r.get('actual_outcome')}")
        print(f"  Question: {r['question'][:80]}")
        