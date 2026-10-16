"""Google-authenticated, database-authorized EATI admin access."""
import streamlit as st
import psycopg


def is_admin(email: str) -> bool:
    """Check the active administrator allowlist in Supabase."""
    email = (email or "").strip().lower()
    if not email:
        return False
    db_url = st.secrets["connections"]["postgres"]["url"]
    with psycopg.connect(db_url, connect_timeout=10) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM public.admin_users "
                "WHERE lower(email) = %s AND is_active = true)",
                (email,),
            )
            return bool(cur.fetchone()[0])


def require_admin():
    if not st.user.get("is_logged_in", False):
        st.title("EATI Admin Login")
        st.write("Sign in with your authorized Google account.")
        if st.button("Login with Google", type="primary"):
            st.login("google")
        st.stop()

    email = str(st.user.get("email") or "").strip().lower()
    if not email:
        st.error("Google did not provide an email address.")
        st.stop()

    try:
        allowed = is_admin(email)
    except Exception:
        st.error("Could not verify administrator permissions. Check Supabase configuration.")
        st.stop()

    if not allowed:
        st.error("Access denied. This Google account is not an EATI administrator.")
        if st.button("Sign out"):
            st.logout()
        st.stop()
    return email
