# src/config/settings.py

from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    # ── LLM Providers ──────────────────────────────
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # ── Slack ──────────────────────────────────────
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")

    # ── Models ─────────────────────────────────────
    MAIN_MODEL: str = os.getenv(
        "MAIN_MODEL", "llama-3.1-70b-versatile"
    )
    JUDGE_MODEL: str = os.getenv(
        "JUDGE_MODEL", "llama-3.1-8b-instant"
    )
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "all-MiniLM-L6-v2"
    )

    # ── FAISS ──────────────────────────────────────
    EMBEDDING_DIM: int = int(
        os.getenv("EMBEDDING_DIM", "384")
    )
    MAX_CHILD_RESULTS: int = int(
        os.getenv("MAX_CHILD_RESULTS", "5")
    )
    MAX_PARENT_RESULTS: int = int(
        os.getenv("MAX_PARENT_RESULTS", "2")
    )
    MAX_RETRIEVAL_DISTANCE: float = float(
        os.getenv("MAX_RETRIEVAL_DISTANCE", "1.0")
    )
    # ── Paths ──────────────────────────────────────
    BASE_DIR: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    INDEX_DIR: str = os.path.join(BASE_DIR, "indexes")
    DB_PATH: str = os.path.join(BASE_DIR, "triage.db")

    # ── Cost (USD per million tokens) ──────────────
    GROQ_INPUT_COST: float = float(
        os.getenv("GROQ_INPUT_COST", "0.59")
    )
    GROQ_OUTPUT_COST: float = float(
        os.getenv("GROQ_OUTPUT_COST", "0.79")
    )

    # ── SLA (hours) ────────────────────────────────
    SLA_MATRIX: dict = {
        "Platinum": {
            "first_reply": float(
                os.getenv("PLATINUM_FIRST_REPLY", "1")
            ),
            "resolution": float(
                os.getenv("PLATINUM_RESOLUTION", "4")
            )
            
        },
        "Diamond": {
            "first_reply": float(
                os.getenv("DIAMOND_FIRST_REPLY", "4")
            ),
            "resolution": float(
                os.getenv("DIAMOND_RESOLUTION", "24")
            )
            
        },
        "Gold": {
            "first_reply": float(
                os.getenv("GOLD_FIRST_REPLY", "8")
            ),
            "resolution": float(
                os.getenv("GOLD_RESOLUTION", "48")
            )
           
        }
    }

    # ── HITL Trigger Conditions ────────────────────
    HITL_CATEGORIES: list = ["cancellation_risk"]
    HITL_PRIORITIES: list = ["critical"]
    HITL_FAITH_THRESHOLD: float = 0.70

    # ── Eval Thresholds ────────────────────────────
    EVAL_THRESHOLDS: dict = {
        "faithfulness": 0.85,
        "answer_relevance": 0.80,
        "context_precision": 0.75,
        "context_recall": 0.75
    }

settings = Settings()