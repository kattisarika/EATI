import math
import streamlit as st
import psycopg
from psycopg.rows import dict_row

# Navigation
home_col, dashboard_col = st.columns(2)

with home_col:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("home.py")

st.divider()

st.title("💼 Jobs By Vendors")
st.write("Browse the latest vendor job postings.")
# -----------------------------------------
# Pagination configuration
# -----------------------------------------
PAGE_SIZE = 5

# -----------------------------------------
# Load published jobs from Supabase
# -----------------------------------------
@st.cache_data(ttl=60)
def load_vendor_jobs(search_text, page, page_size):

    db_url = st.secrets["connections"]["postgres"]["url"]

    offset = (page - 1) * page_size

    with psycopg.connect(
        db_url,
        connect_timeout=10
    ) as conn:

        with conn.cursor(row_factory=dict_row) as cur:

            # Search all published job postings
            where_clause = """
                WHERE LOWER(status) = 'published'
            """

            params = []

            if search_text:
                where_clause += """
                    AND job_posting ILIKE %s
                """
                params.append(f"%{search_text}%")

            # Count matching jobs
            cur.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM public.vendor_jobs
                {where_clause}
                """,
                params
            )

            total_jobs = cur.fetchone()["total"]

            # Fetch only the requested page
            cur.execute(
                f"""
                SELECT
                    id,
                    job_posting,
                    created_at
                FROM public.vendor_jobs
                {where_clause}
                ORDER BY created_at DESC, id DESC
                LIMIT %s OFFSET %s
                """,
                params + [page_size, offset]
            )

            jobs = cur.fetchall()

    return jobs, total_jobs


# -----------------------------------------
# Search
# -----------------------------------------
search = st.text_input(
    "Search Jobs",
    placeholder="Search by title, skills, location, vendor...",
    key="vendor_search"
)

# Reset pagination when search changes
if "vendor_previous_search" not in st.session_state:
    st.session_state.vendor_previous_search = search

if search != st.session_state.vendor_previous_search:
    st.session_state.vendor_page = 1
    st.session_state.vendor_previous_search = search

if "vendor_page" not in st.session_state:
    st.session_state.vendor_page = 1


# -----------------------------------------
# Load total count and current page
# -----------------------------------------
try:
    jobs, total_jobs = load_vendor_jobs(
        search,
        st.session_state.vendor_page,
        PAGE_SIZE
    )

except Exception as e:
    st.error("Unable to load vendor jobs.")
    st.exception(e)
    st.stop()


total_pages = max(
    1,
    math.ceil(total_jobs / PAGE_SIZE)
)

# Handle page numbers that are no longer valid
if st.session_state.vendor_page > total_pages:
    st.session_state.vendor_page = total_pages

    jobs, total_jobs = load_vendor_jobs(
        search,
        st.session_state.vendor_page,
        PAGE_SIZE
    )


# -----------------------------------------
# Display results
# -----------------------------------------
if total_jobs == 0:
    st.info("No matching published jobs found.")

else:
    start_record = (
        (st.session_state.vendor_page - 1)
        * PAGE_SIZE + 1
    )

    end_record = min(
        st.session_state.vendor_page * PAGE_SIZE,
        total_jobs
    )

    st.caption(
        f"Showing {start_record}–{end_record} "
        f"of {total_jobs} jobs"
    )

    for job in jobs:

        with st.container(border=True):

            if job["created_at"]:
                st.caption(
                    "Added: "
                    + job["created_at"].strftime(
                        "%B %d, %Y"
                    )
                )

            # Display original posting with line breaks
            st.text(job["job_posting"] or "")


# -----------------------------------------
# Pagination controls
# -----------------------------------------
if total_pages > 1:

    st.divider()

    previous_col, page_col, next_col = st.columns(
        [1, 2, 1]
    )

    with previous_col:
        if st.button(
            "⬅ Previous",
            disabled=st.session_state.vendor_page == 1,
            use_container_width=True
        ):
            st.session_state.vendor_page -= 1
            st.rerun()

    with page_col:
        selected_page = st.selectbox(
            "Page",
            options=list(range(1, total_pages + 1)),
            index=st.session_state.vendor_page - 1,
            format_func=lambda p: (
                f"Page {p} of {total_pages}"
            ),
            key="vendor_page_selector"
        )

        if selected_page != st.session_state.vendor_page:
            st.session_state.vendor_page = selected_page
            st.rerun()

    with next_col:
        if st.button(
            "Next ➡",
            disabled=(
                st.session_state.vendor_page == total_pages
            ),
            use_container_width=True
        ):
            st.session_state.vendor_page += 1
            st.rerun()

