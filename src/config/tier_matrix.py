# src/config/tier_matrix.py

from src.config.settings import settings

# Add near the top of tier_matrix.py, after the imports

CATEGORY_ESCALATION_OVERRIDES = {
    "export_bug": "Engineering",
    "login_crash": "Engineering",
    "integration_failure": "Engineering",
    "billing_dispute": "Billing Team",
    "cancellation_risk": "Account Management",
    "feature_request": "Product Team",
}


def get_escalation_target(tier: str, category: str) -> str:
    """
    Determines WHO a ticket escalates to, combining the
    department that owns the PROBLEM TYPE (category) with
    the URGENCY WEIGHT given by customer tier.

    Engineering/billing/product issues route to the relevant
    department regardless of tier. Tier mainly affects WHICH
    LEVEL within that department gets pinged for the highest-
    value customers. Categories with no explicit mapping
    (e.g. an auto-resolvable category escalated due to low
    faithfulness) fall back to a generic Support Team queue.
    """
    base_department = CATEGORY_ESCALATION_OVERRIDES.get(category, "Support Team")

    if tier == "Platinum":
        tier_prefix = "Senior "
    elif tier == "Diamond":
        tier_prefix = "Priority "
    else:
        tier_prefix = ""

    return f"{tier_prefix}{base_department}"

def get_tier_config(tier: str) -> dict:
    tier = tier.strip().title()

    if tier not in settings.SLA_MATRIX:
        tier = "Gold"

    config = settings.SLA_MATRIX[tier]

    return {
        "tier": tier,
        "first_reply_hours": config["first_reply"],
        "resolution_hours": config["resolution"],
    }



def get_priority_override(tier: str, category: str) -> str | None:
    """
    Certain combinations always escalate to critical
    regardless of LLM classification.
    Deterministic — no LLM involved.
    """
    if category == "cancellation_risk":
        return "critical"

    if tier == "Platinum" and category == "billing_dispute":
        return "high"

    return None  # no override, keep LLM classification


def get_sla_hours(tier: str, priority: str) -> float:
    """
    Returns first reply SLA in hours.
    Critical tickets get half the normal SLA time.
    """
    config = settings.SLA_MATRIX.get(
        tier, settings.SLA_MATRIX["Gold"]
    )
    base_hours = config["first_reply"]

    if priority == "critical":
        return base_hours / 2

    return base_hours


def needs_hitl(category: str, priority: str, faithfulness: float) -> bool:
    """
    Deterministic HITL trigger check.
    Returns True if ANY trigger condition is met.
    """
    if category in settings.HITL_CATEGORIES:
        return True

    if priority in settings.HITL_PRIORITIES:
        return True

    if faithfulness < settings.HITL_FAITH_THRESHOLD:
        return True

    return False