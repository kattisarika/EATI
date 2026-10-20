
"""EATI - Economic Activity Tracker & Information."""

import base64
from html import escape
from pathlib import Path
from datetime import datetime, timedelta, timezone

import psycopg
import streamlit as st
from psycopg.rows import dict_row

from idle_timeout import install_idle_timeout


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="EATI | Economic Activity Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

install_idle_timeout()

is_logged_in = st.user.is_logged_in

LOGO_PATH = Path(__file__).parent / "assets" / "eati_logo.png"


# =====================================================
# FULL-WIDTH PAGE STYLING
# =====================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --eati-navy: #16375B;
    --eati-blue: #1765A5;
    --eati-sky: #E8F1F9;
    --eati-accent: #0FA47A;
    --eati-ink: #2C3E50;
    --eati-muted: #6B7C93;
    --eati-line: #E1E7EF;
    --eati-shadow: 0 1px 2px rgba(22, 55, 91, .06),
                   0 8px 24px rgba(22, 55, 91, .06);
}

/* Keep the header, but make it invisible chrome. It is the parent of the
   "expand sidebar" button — hiding it outright makes the sidebar (and the
   Logout button inside it) permanently unreachable.
   It is a fixed, full-width bar, so it must not intercept clicks: without
   pointer-events:none it covers the top-right Login button. */
header[data-testid="stHeader"],
header[data-testid="stHeader"] [data-testid="stToolbar"] {
    background: transparent !important;
    box-shadow: none !important;
    pointer-events: none !important;
}

/* Hide the toolbar's own actions (menu, status, deploy) individually
   rather than hiding the whole toolbar. */
[data-testid="stToolbarActions"],
[data-testid="stStatusWidget"],
[data-testid="stMainMenu"],
[data-testid="stMainMenuButton"],
#MainMenu {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

footer {
    display: none !important;
}

/* Sidebar toggle: visible, on-brand, and the only clickable thing left
   in the header (its parent is pointer-events:none). */
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] {
    display: inline-flex !important;
    visibility: visible !important;
    pointer-events: auto !important;
}

[data-testid="stExpandSidebarButton"] button,
[data-testid="stExpandSidebarButton"] span,
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"] span {
    color: var(--eati-navy) !important;
}

/* Full-width layout */
.block-container {
    max-width: 100% !important;
    padding-left: 3% !important;
    padding-right: 3% !important;
    padding-top: 1.25rem !important;
    padding-bottom: 2rem !important;
}

/* Background */
.stApp {
    background:
        radial-gradient(1100px 520px at 88% -8%,
                        rgba(23, 101, 165, .10), transparent 60%),
        radial-gradient(900px 480px at -5% 0%,
                        rgba(15, 164, 122, .08), transparent 55%),
        #FBFCFE;
}

/* Typography */
html, body, .stApp,
[class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont,
                 'Segoe UI', sans-serif;
}

h1, h2, h3 {
    color: var(--eati-navy);
    letter-spacing: -0.02em;
}

p, li, span {
    color: var(--eati-ink);
}

/* Buttons */
div.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    letter-spacing: .01em;
    min-height: 46px;
    transition: transform .15s ease, box-shadow .15s ease,
                background-color .15s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,
                                var(--eati-blue) 0%,
                                var(--eati-navy) 100%);
    border: none;
    color: #FFFFFF;
    box-shadow: 0 6px 18px rgba(23, 101, 165, .28);
}

div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 10px 24px rgba(23, 101, 165, .36);
}

/* Google login buttons: white with a blue border, not a filled fill.
   Scoped by widget key so other primary buttons (Submit, Save) stay filled. */
.st-key-top_google_login div.stButton > button,
.st-key-bottom_google_login div.stButton > button {
    background: #FFFFFF !important;
    border: 2px solid var(--eati-blue) !important;
    color: var(--eati-blue) !important;
    box-shadow: none !important;
    width: 100% !important;
    cursor: pointer;
    pointer-events: auto !important;
    z-index: 2;
}

.st-key-top_google_login div.stButton > button:hover,
.st-key-bottom_google_login div.stButton > button:hover {
    background: var(--eati-sky) !important;
    border-color: var(--eati-navy) !important;
    color: var(--eati-navy) !important;
    box-shadow: 0 6px 16px rgba(23, 101, 165, .18) !important;
}

/* The label is inside the button; let clicks fall through to the button
   itself so the whole surface is active, not just around the icon. */
.st-key-top_google_login div.stButton > button p,
.st-key-bottom_google_login div.stButton > button p {
    color: inherit !important;
    font-weight: 600;
    width: 100%;
    pointer-events: none;
}

/* Job expanders */
div[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border: 1px solid var(--eati-line);
    border-radius: 12px;
    box-shadow: var(--eati-shadow);
}

/* Spacing */
div[data-testid="stVerticalBlock"] {
    gap: 0.8rem;
}

hr {
    border-color: var(--eati-line) !important;
}

/* ---------- Landing page components ---------- */

.eati-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: .35rem 0 1rem 0;
}

.eati-brand {
    display: flex;
    align-items: center;
    gap: .8rem;
}

.eati-brand img {
    height: 46px;
    width: auto;
}

.eati-brand-text .name {
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--eati-navy);
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.eati-brand-text .tag {
    font-size: .76rem;
    font-weight: 500;
    color: var(--eati-muted);
    letter-spacing: .04em;
    text-transform: uppercase;
}

.eati-hero {
    background: #FFFFFF;
    border: 2px solid var(--eati-blue);
    border-radius: 20px;
    padding: 3.2rem 3rem;
    color: var(--eati-ink);
    box-shadow: var(--eati-shadow);
    position: relative;
    overflow: hidden;
}

.eati-hero .eyebrow {
    display: inline-block;
    font-size: .74rem;
    font-weight: 600;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--eati-blue);
    background: var(--eati-sky);
    border: 1px solid #CFE2F2;
    padding: .32rem .8rem;
    border-radius: 999px;
    margin-bottom: 1.1rem;
}

.eati-hero h1 {
    color: var(--eati-navy);
    font-size: clamp(2rem, 4vw, 3.1rem);
    font-weight: 800;
    line-height: 1.12;
    margin: 0 0 1rem 0;
    letter-spacing: -0.03em;
    max-width: 18ch;
}

.eati-hero p {
    color: var(--eati-muted);
    font-size: 1.06rem;
    line-height: 1.65;
    max-width: 62ch;
    margin: 0;
}

.eati-pills {
    display: flex;
    flex-wrap: wrap;
    gap: .55rem;
    margin-top: 1.6rem;
    position: relative;
    z-index: 1;
}

.eati-pills span {
    font-size: .85rem;
    font-weight: 500;
    color: var(--eati-navy);
    background: #FFFFFF;
    border: 1px solid var(--eati-blue);
    border-radius: 999px;
    padding: .4rem .95rem;
}

.eati-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 1rem;
    margin: 1.6rem 0 .5rem 0;
}

.eati-card {
    background: #FFFFFF;
    border: 1px solid var(--eati-line);
    border-radius: 14px;
    padding: 1.3rem 1.4rem;
    box-shadow: var(--eati-shadow);
    transition: transform .18s ease, box-shadow .18s ease;
}

.eati-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 32px rgba(22, 55, 91, .12);
}

.eati-card .icon {
    font-size: 1.5rem;
    line-height: 1;
}

.eati-card h4 {
    margin: .7rem 0 .35rem 0;
    font-size: 1rem;
    font-weight: 700;
    color: var(--eati-navy);
}

.eati-card p {
    margin: 0;
    font-size: .88rem;
    line-height: 1.55;
    color: var(--eati-muted);
}

.eati-section-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
    margin: 2.2rem 0 .25rem 0;
}

.eati-section-head h2 {
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
}

.eati-section-head .sub {
    font-size: .88rem;
    color: var(--eati-muted);
}

.eati-job {
    display: flex;
    align-items: center;
    gap: 1.1rem;
    background: #FFFFFF;
    border: 1px solid var(--eati-line);
    border-left: 4px solid var(--eati-blue);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: .7rem;
    box-shadow: var(--eati-shadow);
    transition: transform .18s ease, box-shadow .18s ease,
                border-left-color .18s ease;
}

.eati-job:hover {
    transform: translateX(3px);
    border-left-color: var(--eati-accent);
    box-shadow: 0 12px 28px rgba(22, 55, 91, .12);
}

.eati-job .rank {
    flex: 0 0 auto;
    width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: var(--eati-sky);
    color: var(--eati-blue);
    font-weight: 700;
    font-size: .92rem;
}

.eati-job .body {
    flex: 1 1 auto;
    min-width: 0;
}

.eati-job .title {
    font-size: 1.02rem;
    font-weight: 600;
    color: var(--eati-navy);
    line-height: 1.4;
    margin-bottom: .3rem;
}

.eati-job .meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: .5rem;
    font-size: .8rem;
    color: var(--eati-muted);
}

.eati-badge {
    display: inline-block;
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .03em;
    padding: .2rem .6rem;
    border-radius: 999px;
    border: 1px solid transparent;
}

.eati-badge.type {
    background: var(--eati-sky);
    color: var(--eati-blue);
    border-color: #CFE2F2;
}

.eati-badge.new {
    background: #E6F7F1;
    color: #0B7E5E;
    border-color: #BFEADC;
}

.eati-footer {
    margin-top: 2.5rem;
    padding-top: 1.1rem;
    border-top: 1px solid var(--eati-line);
    text-align: center;
    font-size: .82rem;
    color: var(--eati-muted);
}

/* Mobile layout */
@media (max-width: 768px) {
    .block-container {
        padding-left: 4% !important;
        padding-right: 4% !important;
    }

    .eati-hero {
        padding: 2.1rem 1.5rem;
        border-radius: 16px;
    }

    .eati-job {
        align-items: flex-start;
    }

    .eati-section-head {
        flex-direction: column;
        gap: .2rem;
    }
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# DATABASE CONNECTION
# =====================================================

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


@st.cache_data
def get_logo_data_uri():
    """Return the logo as a data URI so it can be used inside HTML."""

    if not LOGO_PATH.exists():
        return None

    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode()

    return f"data:image/png;base64,{encoded}"


# =====================================================
# PUBLIC LANDING PAGE - BEFORE LOGIN
# =====================================================

if not is_logged_in:

    # -------------------------------------------------
    # TOP HEADER
    # -------------------------------------------------

    brand_col, login_col = st.columns(
        [7, 2],
        vertical_alignment="center"
    )

    with brand_col:

        logo_uri = get_logo_data_uri()

        logo_html = (
            f'<img src="{logo_uri}" alt="EATI logo">'
            if logo_uri
            else ""
        )

        st.markdown(
            f"""
            <div class="eati-brand">
                {logo_html}
                <div class="eati-brand-text">
                    <div class="name">EATI</div>
                    <div class="tag">
                        Economic Activity Tracker &amp; Information
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with login_col:

        if st.button(
            "🔐 Login with Google",
            type="primary",
            use_container_width=True,
            key="top_google_login"
        ):
            st.login("google")

    st.divider()

    # -------------------------------------------------
    # HERO SECTION
    # -------------------------------------------------

    st.markdown(
        """
        <div class="eati-hero">
            <span class="eyebrow">Workforce Intelligence</span>
            <h1>Discover Opportunities. Stay Ahead of Change.</h1>
            <p>
                Your destination for employment opportunities,
                workforce intelligence, and economic activity across
                the United States — the latest full-time and contract
                jobs, hiring trends, layoffs, job creation, and company
                expansions, all in one place.
            </p>
            <div class="eati-pills">
                <span>📈 Hiring Trends</span>
                <span>🏢 Company Expansions</span>
                <span>📉 Layoff Tracking</span>
                <span>💼 Live Job Board</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # FEATURE CARDS
    # -------------------------------------------------

    st.markdown(
        """
        <div class="eati-cards">
            <div class="eati-card">
                <div class="icon">💼</div>
                <h4>Curated Job Board</h4>
                <p>
                    Full-time and vendor contract roles,
                    published and refreshed continuously.
                </p>
            </div>
            <div class="eati-card">
                <div class="icon">📄</div>
                <h4>Job Profiles</h4>
                <p>
                    Build a profile once and match it against
                    every opportunity on the board.
                </p>
            </div>
            <div class="eati-card">
                <div class="icon">🎤</div>
                <h4>Mock Interviews</h4>
                <p>
                    Practice role-specific interviews and get
                    structured feedback before the real thing.
                </p>
            </div>
            <div class="eati-card">
                <div class="icon">📊</div>
                <h4>Economic Signals</h4>
                <p>
                    Track layoffs, job creation, and expansion
                    activity across the United States.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # LATEST JOBS
    # -------------------------------------------------

    st.markdown(
        """
        <div class="eati-section-head">
            <h2>🆕 Latest Job Opportunities</h2>
            <div class="sub">
                The five most recently published jobs on EATI
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    try:

        jobs = get_public_jobs()

        if not jobs:

            st.info(
                "No published jobs are available right now."
            )

        else:

            now = datetime.now(timezone.utc)

            for index, job in enumerate(jobs):

                posting = (
                    job["job_posting"]
                    or "Job details unavailable"
                )

                created_at = job["created_at"]

                is_new = (
                    created_at is not None
                    and created_at >= now - timedelta(days=7)
                )

                lines = [
                    line.strip()
                    for line in posting.splitlines()
                    if line.strip()
                ]

                job_title = (
                    lines[0][:120]
                    if lines
                    else "Job Opportunity"
                )

                job_type = job["job_type"]

                added_date = (
                    created_at.strftime("%B %d, %Y")
                    if created_at
                    else "Recently added"
                )

                new_badge = (
                    '<span class="eati-badge new">NEW</span>'
                    if is_new
                    else ""
                )

                st.markdown(
                    f"""
                    <div class="eati-job">
                        <div class="rank">{index + 1}</div>
                        <div class="body">
                            <div class="title">
                                {escape(job_title)}
                            </div>
                            <div class="meta">
                                <span class="eati-badge type">
                                    {escape(job_type)}
                                </span>
                                <span>
                                    Added {escape(added_date)}
                                </span>
                                {new_badge}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    except Exception:

        st.warning(
            "Job listings are temporarily unavailable."
        )

    # -------------------------------------------------
    # CLOSING CALL TO ACTION
    # -------------------------------------------------

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    cta_left, cta_mid, cta_right = st.columns([3, 2, 3])

    with cta_mid:

        if st.button(
            "🚀 Get Started — Login with Google",
            type="primary",
            use_container_width=True,
            key="bottom_google_login"
        ):
            st.login("google")


# =====================================================
# APPLICATION NAVIGATION
# =====================================================

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
        url_path="admin-full-time-roles"
    ),

    st.Page(
        "pages/5_Feedback.py",
        title="Feedback",
        icon="💬",
        url_path="Feedback"
    )

]


# =====================================================
# RUN NAVIGATION
# =====================================================

st.navigation(
    pages,
    position="hidden"
).run()


st.markdown(
    """
    <div class="eati-footer">
        © 2026 EATI | Economic Activity Tracker &amp; Information
    </div>
    """,
    unsafe_allow_html=True
)
