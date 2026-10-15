
import os
import psycopg
import streamlit as st


def save_google_user(user):
    google_sub = user.get("sub")
    email = user.get("email")
    full_name = user.get("name")

    if not google_sub:
        raise ValueError("Google user ID is missing.")

    database_url = (
        st.secrets.get("DATABASE_URL")
        if "DATABASE_URL" in st.secrets
        else os.getenv("DATABASE_URL")
    )

    if not database_url:
        raise ValueError("DATABASE_URL is not configured.")

    sql = """
        INSERT INTO public.app_users (
            google_sub,
            email,
            full_name
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (google_sub)
        DO UPDATE SET
            email = EXCLUDED.email,
            full_name = EXCLUDED.full_name,
            last_login_at = NOW(),
            login_count = app_users.login_count + 1
        RETURNING id;
    """

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (google_sub, email, full_name))
            return cur.fetchone()[0]

