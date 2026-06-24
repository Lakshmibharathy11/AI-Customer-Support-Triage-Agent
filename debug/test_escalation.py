from src.agent.nodes.escalation_node import escalation_node

state = {
    "ticket_id": "TKT-ESC-TEST-001",
    "tier": "Platinum",
    "category": "export_bug",
    "priority": "critical",
    "escalation_target": "VP Engineering",
    "ticket_text": "PDF export broken before board meeting tomorrow.",
    "resolution_deadline": "2026-06-22T21:00:00",
}

# Need a ticket row to exist first, since update_ticket() targets
# an existing row by ticket_id
from src.observability.logger import insert_ticket
from datetime import datetime

try:
    insert_ticket({
        "ticket_id": "TKT-ESC-TEST-001",
        "tier": "Platinum",
        "category": "export_bug",
        "priority": "critical",
        "ticket_text": "PDF export broken before board meeting tomorrow.",
        "created_at": datetime.now().isoformat(),
    })
except Exception as e:
    print("Ticket may already exist, continuing:", e)

result = escalation_node(state)
print("Escalation node ran successfully")