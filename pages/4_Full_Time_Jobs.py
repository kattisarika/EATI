import streamlit as st
import psycopg
import math

# Navigation
home_col, dashboard_col = st.columns(2)

with home_col:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("home.py")

st.divider()

st.title("Full-Time Jobs")

PAGE_SIZE = 5

db_url = st.secrets["connections"]["postgres"]["url"]

if "fulltime_page" not in st.session_state:
    st.session_state.fulltime_page = 1

page = st.session_state.fulltime_page

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:

        cur.execute("""
            SELECT COUNT(*)
            FROM public.full_time_jobs
            WHERE status = 'published'
        """)

        total_jobs = cur.fetchone()[0]

        total_pages = max(
            1,
            (total_jobs + PAGE_SIZE - 1) // PAGE_SIZE
        )

        if page > total_pages:
            page = total_pages
            st.session_state.fulltime_page = page

        offset = (page - 1) * PAGE_SIZE

        cur.execute("""
            SELECT id, job_posting, created_at
            FROM public.full_time_jobs
            WHERE status = 'published'
            ORDER BY created_at DESC, id DESC
            LIMIT %s OFFSET %s
        """, (PAGE_SIZE, offset))

        jobs = cur.fetchall()

if not jobs:
    st.info("No full-time jobs are available right now.")

else:
    for job_id, job_posting, created_at in jobs:

        with st.container(border=True):
            st.markdown(job_posting)
            st.caption(
                f"Posted on {created_at.strftime('%B %d, %Y')}"
            )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button(
            "Previous",
            disabled=page <= 1,
            use_container_width=True
        ):
            st.session_state.fulltime_page -= 1
            st.rerun()

    with col2:
        st.markdown(
            f"<div style='text-align:center'>"
            f"Page {page} of {total_pages}"
            f"</div>",
            unsafe_allow_html=True
        )

    with col3:
        if st.button(
            "Next",
            disabled=page >= total_pages,
            use_container_width=True
        ):
            st.session_state.fulltime_page += 1
            st.rerun()
