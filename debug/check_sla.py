from src.observability.logger import get_connection

with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sla_log WHERE ticket_id = 'TKT-SLA-001'")
    row = cursor.fetchone()
    print(dict(row) if row else "No row found")