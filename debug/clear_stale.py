from src.observability.logger import get_connection

with get_connection() as conn:
    conn.execute("DELETE FROM hitl_queue WHERE ticket_id = 'TKT-CANCEL-001'")

print("Cleared stale row")