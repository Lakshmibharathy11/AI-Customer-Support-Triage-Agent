import json

with open("eval_results/golden_run_results.json", encoding="utf-8") as f:
    results = json.load(f)

target_ids = ["GOLD-001", "GOLD-003", "GOLD-004", "GOLD-007", "GOLD-028"]

for r in results:
    if r["ticket_id"] in target_ids:
        print(f"--- {r['ticket_id']} ---")
        print("Expected outcome:", r.get("expected_outcome"), "| Actual:", r.get("actual_outcome"))
        print("Expected category:", r.get("expected_category"), "| Actual:", r.get("actual_category"))
        print("Faithfulness:", r.get("faithfulness_score"))
        print("Answer:", r.get("answer")[:150])
        print()