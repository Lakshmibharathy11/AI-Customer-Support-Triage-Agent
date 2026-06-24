"""Generate the synthetic Stacklytics knowledge base.

Usage (from project root, venv active):
    python scripts/generate_kb.py

Idempotent: articles that already exist are skipped, so it's safe to re-run
after a rate-limit interruption.
"""

import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq  # noqa: E402

KB_ROOT = Path("data/raw/stacklytics_kb")
MODEL = "llama-3.3-70b-versatile"

# One canonical source of truth injected into every prompt so the 30
# articles never contradict each other. This consistency is what makes
# the KB usable as eval ground truth later.
FACTS = """
Stacklytics is a B2B product-analytics SaaS for engineering teams.
Customer tiers: Gold (entry tier, Net-15 payment terms, auto-charged,
1 seat included, 1M events/mo, standard support response in 8 hours);
Diamond (mid tier, Net-15 payment terms, invoiced, up to 10 seats,
10M events/mo, priority support response in 4 hours);
Platinum (top tier, Net-30 payment terms, invoiced, unlimited seats,
unlimited events, SSO/SAML included, dedicated CSM, support response
in 1 hour, escalations reviewed within 2 business hours).
Support hours: Monday-Friday, 9am-5pm Pacific Time.
API base URL: https://api.stacklytics.io/v2
SDKs available: JavaScript, Python, Go.
Common errors: 401 = invalid API key; 429 = rate limit exceeded
(error code RATE_LIMIT_EXCEEDED); SDK-1042 = event schema validation failure.
Billing: invoices issued on the 1st of each month. Disputes must be
submitted as a ticket tagged "billing-dispute" within 14 days of the
invoice date.
Refunds: 30-day money-back on annual plans; downgrades get prorated credits.
Status page: https://status.stacklytics.io
Uptime SLA: Platinum 99.95%, Diamond 99.9%, Gold 99.5%.
"""

# (slug, title, category, folder, needs_table)
ARTICLES = [
    # Technical -> integrations/
    ("fixing-401-invalid-api-key", "Fixing 401 invalid API key errors", "sdk_api_error", "integrations", False),
    ("handling-429-rate-limits", "Handling 429 rate limit errors", "sdk_api_error", "integrations", False),
    ("fixing-sdk-1042-schema-errors", "Fixing SDK-1042 schema validation errors", "sdk_api_error", "integrations", False),
    ("events-not-appearing", "Events not appearing in your dashboard", "data_sync_issue", "integrations", False),
    ("fixing-delayed-data-sync", "Fixing delayed data sync", "data_sync_issue", "integrations", False),
    ("duplicate-events-troubleshooting", "Troubleshooting duplicate events", "data_sync_issue", "integrations", False),
    ("installing-the-javascript-sdk", "Installing the JavaScript SDK", "configuration_help", "integrations", False),
    ("installing-the-python-sdk", "Installing the Python SDK", "configuration_help", "integrations", False),

    # Technical -> platform_ops/
    ("checking-platform-status", "Checking platform status", "outage_downtime", "platform_ops", False),
    ("what-to-do-during-an-outage", "What to do during an outage", "outage_downtime", "platform_ops", False),
    ("understanding-uptime-sla", "Understanding our uptime SLA", "outage_downtime", "platform_ops", True),
    ("how-to-file-a-bug-report", "How to file a bug report", "bug_report", "platform_ops", False),
    ("collecting-debug-logs", "Collecting debug logs", "bug_report", "platform_ops", False),
    ("known-issues-and-workarounds", "Known issues and workarounds", "bug_report", "platform_ops", False),
    ("quickstart-guide", "Quickstart guide", "how_to_onboarding", "platform_ops", False),

    # Billing -> billing/
    ("understanding-your-invoice", "Understanding your invoice", "invoice_payment", "billing", True),
    ("fixing-a-failed-payment", "Fixing a failed payment", "invoice_payment", "billing", False),
    ("updating-payment-method", "Updating your payment method", "invoice_payment", "billing", False),
    ("upgrading-or-downgrading", "Upgrading or downgrading your plan", "plan_change_refund", "billing", True),
    ("refund-policy", "Refund policy", "plan_change_refund", "billing", False),
    ("proration-and-credits", "Proration and credits explained", "plan_change_refund", "billing", False),
    ("enterprise-plan-overview", "Platinum plan overview", "upgrade_expansion", "billing", True),
    ("requesting-a-demo-or-quote", "Requesting a demo or quote", "upgrade_expansion", "billing", False),
    ("adding-seats-to-your-plan", "Adding seats to your plan", "upgrade_expansion", "billing", True),

    # General -> auth/
    ("resetting-your-password", "Resetting your password", "login_access", "auth", False),
    ("setting-up-sso-saml", "Setting up SSO / SAML (Platinum)", "login_access", "auth", False),
    ("managing-roles-and-permissions", "Managing team roles and permissions", "login_access", "auth", False),

    # General -> export/
    ("creating-your-first-dashboard", "Creating your first dashboard", "how_to_onboarding", "export", False),
    ("tracking-custom-events", "Tracking custom events", "how_to_onboarding", "export", False),
    ("configuring-event-batching", "Configuring event batching", "how_to_onboarding", "export", True),
]

PROMPT_TEMPLATE = """You are writing a help-center article for Stacklytics.

Canonical product facts (every detail you state MUST agree with these):
{facts}

Write a help article titled "{title}".
Audience: a customer searching the help center.
Length: 250-400 words.

STRUCTURE REQUIREMENTS (strict):
- Format: markdown body only (no top-level "# Title" line, that is added separately).
- Organize the content into 3 to 5 sections using "## " markdown headers.
- Each section should be 2-5 sentences of clear, concrete prose.
- Use specific details: exact error codes, URLs, prices, tier names
  (Gold, Diamond, Platinum), and policies from the facts above.
- Do not invent facts that conflict with the canonical list.
- Do not add a closing sign-off.
{table_instruction}
"""

TABLE_INSTRUCTION = """
- One of your sections MUST include a markdown table (using | pipes |)
  presenting structured information such as a comparison across tiers
  (Gold / Diamond / Platinum), a list of error codes, or pricing/limits.
  The table must contain real values from the canonical facts above.
"""


def build_frontmatter(slug: str, title: str, category: str, department: str) -> str:
    # Platinum-only content gets restricted visibility; everything else
    # is visible to all tiers. This becomes a metadata filter at retrieval time.
    if "platinum" in title.lower() or slug in ("setting-up-sso-saml", "enterprise-plan-overview"):
        tier_visibility = ["Platinum"]
    else:
        tier_visibility = ["Platinum", "Diamond", "Gold"]

    tier_list_str = "[" + ", ".join(f'"{t}"' for t in tier_visibility) + "]"

    return (
        "---\n"
        f'title: "{title}"\n'
        f"category: {category}\n"
        f"department: {department}\n"
        f"tier_visibility: {tier_list_str}\n"
        f"article_id: {slug}\n"
        'last_updated: "2026-05-12"\n'
        "---\n\n"
    )


def main() -> None:
    KB_ROOT.mkdir(parents=True, exist_ok=True)
    llm = ChatGroq(model=MODEL, temperature=0.4)

    generated, skipped = 0, 0
    for slug, title, category, folder, needs_table in ARTICLES:
        folder_path = KB_ROOT / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        path = folder_path / f"{slug}.md"

        if path.exists():
            skipped += 1
            continue

        table_instruction = TABLE_INSTRUCTION if needs_table else ""
        prompt = PROMPT_TEMPLATE.format(
            facts=FACTS, title=title, table_instruction=table_instruction
        )
        body = llm.invoke(prompt).content.strip()

        frontmatter = build_frontmatter(slug, title, category, folder)
        path.write_text(frontmatter + f"# {title}\n\n" + body + "\n", encoding="utf-8")

        generated += 1
        print(f"[{generated + skipped}/{len(ARTICLES)}] wrote {path}")
        time.sleep(2)  # stay friendly with the free-tier rate limit

    print(f"\nDone. Generated {generated}, skipped {skipped} existing.")


if __name__ == "__main__":
    main()