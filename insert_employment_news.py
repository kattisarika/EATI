#!/usr/bin/env python3
"""JMT employment news importer.

Usage:
    python3 insert_employment_news.py             # validate only
    python3 insert_employment_news.py --write     # insert new URLs into Supabase

Requires: pip install supabase python-dotenv
Input: jmt_articles.json in the same directory as this script.
Credentials: .env in the same directory, containing SUPABASE_URL and
SUPABASE_SERVICE_ROLE_KEY (a backend sb_secret_ or legacy service_role key).
"""

import argparse
import json
import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

CATEGORIES = {"Layoffs", "Hiring", "Job Creation", "Company Expansion"}
SOURCE_TYPES = {"News", "Startup News", "Government Announcement", "Company Press Release"}
STATE_NAMES = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming",
}
STATE_ABBREVIATIONS = dict(zip(
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split(),
    [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
        "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
        "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
        "Wisconsin", "Wyoming",
    ]
))

BASE_DIR = Path(__file__).resolve().parent


def required_text(record, field):
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value.strip()


def optional_text(record, field):
    value = record.get(field)
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string or null")
    return value.strip() or None


def parse_date(value, field, required=False):
    if value is None or value == "":
        if required:
            raise ValueError(f"{field} is required")
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid YYYY-MM-DD date") from exc


def normalize_state(value):
    # Missing state is allowed for nationwide announcements.
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValueError("state must be a state name, abbreviation, or null")
    cleaned = value.strip()
    if not cleaned:
        return None
    state = STATE_ABBREVIATIONS.get(cleaned.upper(), cleaned.title())
    if state not in STATE_NAMES:
        raise ValueError(f"unrecognized state: {value}")
    return state


def normalize_article(article, today):
    if not isinstance(article, dict):
        raise ValueError("article must be a JSON object")

    category = required_text(article, "category")
    if category not in CATEGORIES:
        raise ValueError(f"unknown category: {category}")

    source_type = required_text(article, "source_type")
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"unknown source_type: {source_type}")

    published = date.fromisoformat(parse_date(article.get("publication_date"), "publication_date", True))
    if not (today - timedelta(days=30) <= published <= today):
        raise ValueError("publication_date is outside the trailing 30 days")

    url = required_text(article, "source_url")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or any(c.isspace() for c in url):
        raise ValueError("source_url must be a plain HTTP(S) URL")

    jobs = article.get("jobs_affected")
    if jobs is not None and (type(jobs) is not int or jobs < 0):
        raise ValueError("jobs_affected must be a nonnegative integer or null")

    country = optional_text(article, "country") or "USA"
    if country.upper() not in ("USA", "US", "UNITED STATES", "UNITED STATES OF AMERICA"):
        raise ValueError("country must be USA")

    return {
        "company_name": required_text(article, "company_name"),
        "industry": optional_text(article, "industry"),
        "category": category,
        "headline": required_text(article, "headline"),
        "publication_date": published.isoformat(),
        "announcement_date": parse_date(article.get("announcement_date"), "announcement_date"),
        "source_name": optional_text(article, "source_name"),
        "source_type": source_type,
        "source_url": url,
        "country": "USA",
        "state": normalize_state(article.get("state")),
        "city": optional_text(article, "city"),
        "jobs_affected": jobs,
        "employment_status": optional_text(article, "employment_status"),
        "summary": optional_text(article, "summary"),
        "verification_status": "pending",
    }


def insert_into_supabase(articles):
    from dotenv import load_dotenv
    from supabase import create_client

    load_dotenv(BASE_DIR / ".env")
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env")
    if key.startswith("sb_publishable_"):
        raise RuntimeError("A publishable key cannot bypass RLS. Use a backend secret key in .env.")

    client = create_client(url, key)
    # ignore_duplicates=True uses ON CONFLICT DO NOTHING for source_url.
    # This preserves existing records and any previous verification decisions.
    response = (
        client.table("employment_news")
        .upsert(articles, on_conflict="source_url", ignore_duplicates=True)
        .execute()
    )
    return len(response.data or [])


def main():
    parser = argparse.ArgumentParser(description="Validate and import JMT employment news")
    parser.add_argument("--write", action="store_true", help="Insert valid articles into Supabase")
    parser.add_argument("--file", default=str(BASE_DIR / "jmt_articles.json"), help="Path to JMT JSON file")
    args = parser.parse_args()

    print("JMT Employment News Collector started...")
    try:
        with open(args.file, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict) or not isinstance(data.get("articles"), list):
            raise ValueError('JSON must be an object containing an "articles" array')

        articles = data["articles"]
        print(f"Articles found: {len(articles)}")
        today = datetime.now(ZoneInfo("America/Chicago")).date()
        valid = []
        seen_urls = set()
        for index, article in enumerate(articles, 1):
            try:
                normalized = normalize_article(article, today)
                if normalized["source_url"] in seen_urls:
                    print(f"Article {index} skipped: duplicate source_url in JSON")
                    continue
                seen_urls.add(normalized["source_url"])
                valid.append(normalized)
            except (ValueError, TypeError) as exc:
                print(f"Article {index} rejected: {exc}")

        print(f"Valid articles: {len(valid)}")
        if not args.write:
            print("Dry run completed. No data inserted into Supabase.")
            return 0
        if not valid:
            print("No valid articles to insert.")
            return 0

        inserted = insert_into_supabase(valid)
        print(f"Supabase write completed. New records returned: {inserted}")
        print("All newly inserted articles have verification_status='pending'.")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
