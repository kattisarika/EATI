"""Read-only MCP server for JMT workforce_events in Supabase.

Run: python server.py
Transport: stdio (for local MCP clients).
"""
import os
from datetime import date
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from supabase import create_client

load_dotenv(override=True)

mcp = FastMCP("JMT Employment Intelligence")
TABLE = "workforce_events"
COLUMNS = (
    "id,company_name,industry,publication_month,news_category,headline,"
    "publication_date,announcement_date,news_source,source_type,article_url,"
    "state_or_region,jobs_affected_count,jobs_affected_text,employment_status,"
    "factual_summary,created_at,updated_at"
)


def db():
    url = os.getenv("SUPABASE_URL", "").strip()
    key = (os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    if not url or not key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SECRET_KEY in .env")
    if key.startswith("sb_publishable_"):
        raise RuntimeError("Use a backend secret key, not a publishable key, for this private MCP server")
    return create_client(url, key)


def bounded_limit(limit: int) -> int:
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    return limit


def fetch_rows(limit: int = 25, state: str | None = None, category: str | None = None,
               company: str | None = None, month: str | None = None) -> list[dict[str, Any]]:
    query = db().table(TABLE).select(COLUMNS)
    if state:
        query = query.ilike("state_or_region", f"%{state.strip()}%")
    if category:
        query = query.eq("news_category", category)
    if company:
        query = query.ilike("company_name", f"%{company.strip()}%")
    if month:
        query = query.eq("publication_month", month)
    result = query.order("publication_date", desc=True).limit(bounded_limit(limit)).execute()
    return result.data or []


@mcp.tool()
def get_employment_news(limit: int = 25, month: str | None = None) -> list[dict[str, Any]]:
    """Get the latest US workforce events, optionally filtered by month (e.g. October 2026)."""
    return fetch_rows(limit=limit, month=month)


@mcp.tool()
def get_news_by_state(state: str, limit: int = 25) -> list[dict[str, Any]]:
    """Find workforce events whose state_or_region contains the supplied state name."""
    return fetch_rows(limit=limit, state=state)


@mcp.tool()
def get_news_by_category(category: str, limit: int = 25) -> list[dict[str, Any]]:
    """Filter by Layoffs, Hiring, Job Creation, or Company Expansion."""
    allowed = {"Layoffs", "Hiring", "Job Creation", "Company Expansion"}
    if category not in allowed:
        raise ValueError(f"category must be one of: {', '.join(sorted(allowed))}")
    return fetch_rows(limit=limit, category=category)


@mcp.tool()
def get_company_news(company: str, limit: int = 25) -> list[dict[str, Any]]:
    """Find workforce announcements by partial company name."""
    if not company.strip():
        raise ValueError("company cannot be blank")
    return fetch_rows(limit=limit, company=company)


@mcp.tool()
def get_employment_summary(month: str | None = None) -> dict[str, Any]:
    """Summarize event counts and reported jobs by category for up to 10,000 rows.

    Job counts reflect announcements and must not be interpreted as net employment change.
    """
    client = db()
    totals: dict[str, dict[str, int]] = {}
    count = 0
    for start in range(0, 10000, 500):
        query = client.table(TABLE).select("news_category,jobs_affected_count")
        if month:
            query = query.eq("publication_month", month)
        rows = query.range(start, start + 499).execute().data or []
        for row in rows:
            cat = row.get("news_category") or "Unknown"
            bucket = totals.setdefault(cat, {"events": 0, "reported_jobs_affected": 0})
            bucket["events"] += 1
            bucket["reported_jobs_affected"] += int(row.get("jobs_affected_count") or 0)
            count += 1
        if len(rows) < 500:
            break
    return {"month": month or "All available", "events_counted": count,
            "by_category": totals,
            "note": "Counts are from stored records, not independently verified. Jobs affected are not net jobs gained/lost. Max 10,000 rows."}


if __name__ == "__main__":
    mcp.run(transport="stdio")
