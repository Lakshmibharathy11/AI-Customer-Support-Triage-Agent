# src/observability/logger.py

import sqlite3
from contextlib import contextmanager
from src.config.settings import settings


@contextmanager
def get_connection():
    """
    Context manager for SQLite connections.
    Ensures connections are always closed properly.
    """
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """
    Creates all tables if they don't exist.
    Safe to call on every app startup.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id           TEXT PRIMARY KEY,
                tier                TEXT NOT NULL,
                category            TEXT,
                priority            TEXT,
                ticket_text         TEXT NOT NULL,
                drafted_response    TEXT,
                outcome             TEXT,
                escalation_target   TEXT,
                auto_resolved       INTEGER DEFAULT 0,
                hitl_required       INTEGER DEFAULT 0,
                hitl_decision       TEXT,

                faithfulness_score  REAL,
                relevance_score     REAL,

                chunks_retrieved    INTEGER,
                parent_docs_used    INTEGER,

                input_tokens        INTEGER,
                output_tokens       INTEGER,
                judge_input_tokens  INTEGER,
                judge_output_tokens INTEGER,
                cost_usd            REAL,

                total_latency_ms    INTEGER,
                retrieval_latency_ms INTEGER,
                llm_latency_ms      INTEGER,

                created_at          TEXT NOT NULL,
                first_reply_sent_at TEXT,
                resolved_at         TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sla_log (
                ticket_id               TEXT PRIMARY KEY,
                tier                    TEXT NOT NULL,
                created_at              TEXT NOT NULL,
                first_reply_deadline    TEXT NOT NULL,
                resolution_deadline     TEXT NOT NULL,
                first_reply_sent_at     TEXT,
                resolved_at             TEXT,
                first_reply_breached    INTEGER DEFAULT 0,
                resolution_breached     INTEGER DEFAULT 0,
                FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hitl_queue (
                ticket_id        TEXT PRIMARY KEY,
                drafted_response TEXT NOT NULL,
                reason           TEXT NOT NULL,
                status           TEXT DEFAULT 'pending',
                decision_notes   TEXT,
                queued_at        TEXT NOT NULL,
                decided_at       TEXT,
                FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id)
            )
        """)

    print(f"✅ Database initialized at {settings.DB_PATH}")


def insert_ticket(ticket_data: dict):
    """
    Inserts a new ticket record.
    ticket_data keys must match the tickets table columns.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        columns = ", ".join(ticket_data.keys())
        placeholders = ", ".join(["?"] * len(ticket_data))
        values = list(ticket_data.values())

        cursor.execute(
            f"INSERT INTO tickets ({columns}) VALUES ({placeholders})",
            values
        )


def update_ticket(ticket_id: str, updates: dict):
    """
    Updates specific fields on an existing ticket.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [ticket_id]

        cursor.execute(
            f"UPDATE tickets SET {set_clause} WHERE ticket_id = ?",
            values
        )


def insert_sla_log(sla_data: dict):
   
    """
    Idempotent insert — safe to call multiple times for the same
    ticket_id (e.g. if a node re-runs after a graph interrupt).
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        columns = ", ".join(sla_data.keys())
        placeholders = ", ".join(["?"] * len(sla_data))
        values = list(sla_data.values())

        cursor.execute(
            f"INSERT OR REPLACE INTO sla_log ({columns}) VALUES ({placeholders})",
            values
        )
   
   
   
   

   
   
   
   

def insert_hitl_queue(hitl_data: dict):
    """
    Idempotent insert — safe to call multiple times for the same
    ticket_id. LangGraph re-executes node bodies on resume, so this
    function may legitimately be called more than once per ticket;
    only the first insert should take effect.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        columns = ", ".join(hitl_data.keys())
        placeholders = ", ".join(["?"] * len(hitl_data))
        values = list(hitl_data.values())

        cursor.execute(
            f"INSERT OR IGNORE INTO hitl_queue ({columns}) VALUES ({placeholders})",
            values
        )


def get_pending_hitl():
    """
    Returns all tickets currently waiting for human review.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM hitl_queue WHERE status = 'pending'"
        )
        return [dict(row) for row in cursor.fetchall()]


def get_all_tickets():
    """
    Returns all tickets — used by Streamlit dashboard.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]