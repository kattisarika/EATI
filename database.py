
import streamlit as st
import pandas as pd
import psycopg

@st.cache_data(ttl=300)
def get_workforce_events():
    db_url = st.secrets["connections"]["postgres"]["url"]

    query = """
        SELECT
            id,
            company_name,
            industry,
            publication_month,
            news_category::text AS news_category,
            headline,
            publication_date,
            announcement_date,
            news_source,
            source_type,
            article_url,
            state_or_region,
            jobs_affected_count,
            jobs_affected_text,
            employment_status,
            factual_summary,
            created_at
        FROM public.workforce_events
        ORDER BY publication_date DESC NULLS LAST,
                 created_at DESC
        LIMIT 5000
    """

    with psycopg.connect(db_url, connect_timeout=10) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [col.name for col in cur.description]
            rows = cur.fetchall()

    return pd.DataFrame(rows, columns=columns)

