
import streamlit as st
import pandas as pd
import plotly.express as px

from database import get_workforce_events
from user_database import save_google_user
from admin_auth import is_admin


def logout():
    """Clear per-login session state, then end the Google session."""

    for key in (
        "google_user_saved",
        "app_user_id",
        "admin_landing_checked",
        "idle_timer_session_id",
    ):
        st.session_state.pop(key, None)

    # st.logout() clears st.user immediately and only *enqueues* a redirect:
    # it does not halt the script. Without st.stop(), the rest of this page
    # keeps rendering against an empty st.user and crashes on st.user.name.
    st.logout()
    st.stop()


# -----------------------------------
# Google Authentication
# -----------------------------------

if not st.user.get("is_logged_in", False):

    st.title("📊 Economic Activity Tracker")

    st.write(
        "Track employment announcements, hiring, "
        "layoffs and workforce developments."
    )

    if st.button("Login with Google", type="primary"):
        st.login("google")

    st.stop()

# Save the authenticated Google user once per Streamlit session.
if not st.session_state.get("google_user_saved", False):
    try:
        user_id = save_google_user(st.user)
        st.session_state["google_user_saved"] = True
        st.session_state["app_user_id"] = str(user_id)
    except Exception as e:
        st.error("Unable to save Google login information.")
        st.exception(e)
        st.stop()

# Google OAuth returns to the app entrypoint, not the page that initiated login.
# On the first authenticated home visit, send an authorized administrator to
# the Admin Dashboard. The flag prevents a redirect loop when returning Home.
if not st.session_state.get("admin_landing_checked", False):
    st.session_state["admin_landing_checked"] = True
    try:
        if is_admin(str(st.user.get("email") or "")):
            st.switch_page("v3/admin/dashboard.py")
    except Exception:
        # Do not block the regular EATI dashboard if admin lookup is unavailable.
        # The admin pages independently enforce authorization.
        pass

# Account bar: the sidebar starts collapsed, so Logout also lives in the
# main body where it is always reachable.
account_col, logout_col = st.columns([8, 2], vertical_alignment="center")

with account_col:
    st.markdown(f"**Welcome, {st.user.get('name') or 'there'}**")

with logout_col:
    if st.button(
        "🚪 Logout",
        key="home_logout_main",
        use_container_width=True,
    ):
        logout()

st.divider()

# Top navigation: each link opens a separate Streamlit page.
st.markdown("### Career Tools")
nav_cols = st.columns(5)
nav_items = [
    ("Job Profile", "pages/1_Job_Profile.py"),
    ("Mock Interviews", "pages/2_Mock_Interviews.py"),
    ("Jobs By Vendors", "pages/3_Jobs_By_Vendors.py"),
    ("Full Time Jobs", "pages/4_Full_Time_Jobs.py"),
    ("Feedback Form", "pages/5_Feedback.py"),
]
for column, (label, destination) in zip(nav_cols, nav_items):
    with column:
        st.page_link(destination, label=label, icon="📄")
st.divider()

# -----------------------------------
# Sidebar
# -----------------------------------
with st.sidebar:
    st.title("EATI")
    st.write(f"Welcome, {st.user.get('name') or 'there'}")

    if st.button("🚪 Logout", key="home_logout_sidebar", use_container_width=True):
        logout()

    st.divider()

    page = st.radio(
        "Navigation",
        ["Dashboard", "Workforce News"]
    )

    if st.button("Refresh Data"):
        get_workforce_events.clear()
        st.rerun()

# -----------------------------------
# Load data from Supabase
# -----------------------------------
try:
    df = get_workforce_events()
except Exception as e:
    st.error("Unable to load workforce data from Supabase.")
    st.exception(e)
    st.stop()

if df.empty:
    st.warning("No records found in workforce_events.")
    st.stop()

# -----------------------------------
# Prepare data
# -----------------------------------
df["publication_date"] = pd.to_datetime(
    df["publication_date"], errors="coerce"
)

df["jobs_affected_count"] = pd.to_numeric(
    df["jobs_affected_count"], errors="coerce"
)

# -----------------------------------
# Filters
# -----------------------------------
st.title("📊 Economic Activity Tracker")

col1, col2, col3 = st.columns(3)

with col1:
    categories = sorted(
        df["news_category"].dropna().unique().tolist()
    )
    selected_category = st.selectbox(
        "News Category", ["All"] + categories
    )

with col2:
    states = sorted(
        df["state_or_region"].dropna().unique().tolist()
    )
    selected_state = st.selectbox(
        "State / Region", ["All"] + states
    )

with col3:
    industries = sorted(
        df["industry"].dropna().unique().tolist()
    )
    selected_industry = st.selectbox(
        "Industry", ["All"] + industries
    )

# Publication date filters
st.markdown("**Publication Date**")
year_col, month_col = st.columns(2)

available_years = sorted(
    df["publication_date"].dropna().dt.year.astype(int).unique().tolist(),
    reverse=True,
)

with year_col:
    selected_year = st.selectbox("Year", ["All"] + available_years)

with month_col:
    month_options = ["All"] + [
        pd.Timestamp(year=2000, month=m, day=1).strftime("%B")
        for m in range(1, 13)
    ]
    selected_month = st.selectbox("Month", month_options)

filtered = df.copy()

if selected_year != "All":
    filtered = filtered[
        filtered["publication_date"].dt.year == selected_year
    ]

if selected_month != "All":
    month_number = month_options.index(selected_month)
    filtered = filtered[
        filtered["publication_date"].dt.month == month_number
    ]

if selected_category != "All":
    filtered = filtered[
        filtered["news_category"] == selected_category
    ]

if selected_state != "All":
    filtered = filtered[
        filtered["state_or_region"] == selected_state
    ]

if selected_industry != "All":
    filtered = filtered[
        filtered["industry"] == selected_industry
    ]

# -----------------------------------
# Dashboard
# -----------------------------------
if page == "Dashboard":

    st.subheader("Workforce Activity Overview")

    total_events = len(filtered)
    total_companies = filtered["company_name"].nunique()
    total_jobs = int(
        filtered["jobs_affected_count"].sum()
    )
    total_states = filtered["state_or_region"].nunique()

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("News Events", f"{total_events:,}")
    m2.metric("Companies", f"{total_companies:,}")
    m3.metric("Jobs Affected", f"{total_jobs:,}")
    m4.metric("States / Regions", f"{total_states:,}")

    st.caption(
        "Jobs Affected is the sum of reported counts "
        "across filtered records, not net job creation."
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("News by Category")

        category_counts = (
            filtered["news_category"]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )
        category_counts.columns = [
            "Category", "Events"
        ]

        fig = px.bar(
            category_counts,
            x="Category",
            y="Events",
            title="Workforce News Categories"
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("News by Company")

        company_counts = (
            filtered["company_name"]
            .fillna("Unknown")
            .value_counts()
            .head(10)
            .reset_index()
        )
        company_counts.columns = [
            "Company", "Events"
        ]

        fig = px.bar(
            company_counts,
            x="Company",
            y="Events",
            title="Top 10 Companies"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Monthly Workforce News Trend")

    monthly = filtered.dropna(
        subset=["publication_date"]
    ).copy()

    if not monthly.empty:
        monthly["Month"] = (
            monthly["publication_date"]
            .dt.to_period("M")
            .astype(str)
        )

        trend = (
            monthly.groupby("Month")
            .size()
            .reset_index(name="Events")
        )

        fig = px.line(
            trend,
            x="Month",
            y="Events",
            markers=True,
            title="Published Workforce Events by Month"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No publication dates available.")

# -----------------------------------
# Workforce News
# -----------------------------------
elif page == "Workforce News":

    st.subheader("Latest Workforce News")

    search = st.text_input(
        "Search by company or headline",
        placeholder="e.g. Microsoft, layoffs, hiring"
    )

    news = filtered.copy()

    if search:
        matches = (
            news["company_name"]
            .fillna("")
            .str.contains(search, case=False, regex=False)
            |
            news["headline"]
            .fillna("")
            .str.contains(search, case=False, regex=False)
        )
        news = news[matches]

    news = news.sort_values(
        "publication_date",
        ascending=False,
        na_position="last"
    )

    st.write(f"Showing {len(news)} records")

    for _, article in news.iterrows():

        with st.container(border=True):

            st.subheader(
                article["headline"]
                if pd.notna(article["headline"])
                else "Untitled News"
            )

            st.write(
                f"**Company:** {article['company_name']}"
            )

            st.write(
                f"**Industry:** {article['industry']}"
            )

            st.write(
                f"**Region:** {article['state_or_region']}"
            )

            st.write(
                f"**Employment Status:** "
                f"{article['employment_status']}"
            )

            if pd.notna(article["jobs_affected_count"]):
                st.write(
                    f"**Jobs Affected:** "
                    f"{int(article['jobs_affected_count']):,}"
                )
            elif pd.notna(article["jobs_affected_text"]):
                st.write(
                    f"**Jobs Affected:** "
                    f"{article['jobs_affected_text']}"
                )

            if pd.notna(article["factual_summary"]):
                st.write(article["factual_summary"])

            st.caption(
                f"Source: {article['news_source']} | "
                f"Published: {article['publication_date']}"
            )

            if pd.notna(article["article_url"]) \
                    and article["article_url"]:
                st.link_button(
                    "Read Original Article",
                    article["article_url"]
                )

