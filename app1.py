
"""EATI navigation entrypoint. Keep this file as Streamlit Cloud main file."""

import streamlit as st
import psycopg

from pathlib import Path
from datetime import datetime, timedelta, timezone
from psycopg.rows import dict_row

from idle_timeout import install_idle_timeout


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Economic Activity Tracker",
    page_icon="📊",
    layout="wide"
)

install_idle_timeout()


# --------------------------------------------------
# EATI LOGO
# --------------------------------------------------

logo_path = Path(__file__).parent / "assets" / "eati_logo.png"

if logo_path.exists():
    st.image(str(logo_path), width=350)
else:
    st.warning("EATI logo image not found.")


# --------------------------------------------------
# WELCOME MESSAGE
# --------------------------------------------------

st.markdown("""
### Welcome to EATI — Your Gateway to Employment Opportunities and Workforce Insights!

Stay informed with the latest news on hiring trends, layoffs, job creation, and company
expansions across the United States.

Browse full-time and contract job opportunities, create your professional profile,
and explore career development resources to support your job search.

EATI brings together workforce news, employment opportunities, and career tools
in one convenient platform to help you make informed decisions and take the
next step in your career.
""")

st.divider()


# --------------------------------------------------
# PUBLIC JOB LISTINGS
# --------------------------------------------------

@st.cache_data(ttl=300)
def get_public_jobs():

    db_url = st.secrets["connections"]["postgres"]["url"]

    query = """
        SELECT
            id,
            job_posting,
            created_at,
            'Full-Time' AS job_type
        FROM public.full_time_jobs
        WHERE status = 'published'

        UNION ALL

        SELECT
            id,
            job_posting,
            created_at,
            'Vendor / Contract' AS job_type
        FROM public.vendor_jobs
        WHERE status = 'published'

        ORDER BY created_at DESC NULLS LAST
        LIMIT 5
    """

    with psycopg.connect(
        db_url,
        connect_timeout=10,
        row_factory=dict_row
    ) as conn:

        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


st.subheader("🆕 Latest Jobs Added")

st.caption(
    "Discover the latest full-time and contract job opportunities on EATI."
)

try:

    jobs = get_public_jobs()

    if not jobs:

        st.info("No published jobs available right now.")

    else:

        now = datetime.now(timezone.utc)

        for job in jobs:

            created_at = job["created_at"]

            is_new = (
                created_at is not None
                and created_at >= now - timedelta(days=7)
            )

            posting = job["job_posting"] or "Job details unavailable"

            # First nonempty line is used as a preview
            lines = [
                line.strip()
                for line in posting.splitlines()
                if line.strip()
            ]

            preview = lines[0][:100] if lines else "Job Opportunity"

            with st.container(border=True):

                col1, col2 = st.columns([5, 1])

                with col1:
                    st.markdown(
                        f"**{job['job_type']} Opportunity**"
                    )

                with col2:
                    if is_new:
                        st.success("🆕 NEW")

                st.markdown(f"**{preview}**")

                if created_at:
                    st.caption(
                        "Added to EATI: "
                        + created_at.strftime("%B %d, %Y")
                    )

                with st.expander("View Job Details"):
                    st.text(posting)


except Exception:

    st.warning(
        "Job listings are temporarily unavailable."
    )


st.divider()


# --------------------------------------------------
# APPLICATION NAVIGATION
# --------------------------------------------------

# Admin access is enforced inside admin pages.
# st.navigation supports single-segment URL paths.

pages = [

    st.Page(
        "home.py",
        title="EATI Dashboard",
        icon="📊",
        default=True,
        url_path=""
    ),

    st.Page(
        "pages/1_Job_Profile.py",
        title="Job Profile",
        icon="📄"
    ),

    st.Page(
        "pages/2_Mock_Interviews.py",
        title="Mock Interviews",
        icon="🎤"
    ),

    st.Page(
        "pages/3_Jobs_By_Vendors.py",
        title="Jobs By Vendors",
        icon="💼"
    ),

    st.Page(
        "pages/4_Full_Time_Jobs.py",
        title="Full Time Jobs",
        icon="🏢"
    ),

    st.Page(
        "v3/admin/dashboard.py",
        title="Admin Dashboard",
        icon="🛡️",
        url_path="v3-admin"
    ),

    st.Page(
        "v3/admin/vendorjob.py",
        title="Vendor Job Form",
        icon="📝",
        url_path="v3-admin-vendorjob"
    ),

    st.Page(
        "v3/admin/fulltimejob.py",
        title="Admin - Full-Time Roles",
        url_path="admin-full-time-roles",
        default=False
    ),

    st.Page(
        "pages/5_Feedback.py",
        title="Feedback",
        icon="💬",
        url_path="Feedback"
    )

]


# --------------------------------------------------
# RUN NAVIGATION
# --------------------------------------------------

st.navigation(
    pages,
    position="hidden"
).run()

