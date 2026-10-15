
import streamlit as st

# ----------------------------------------
# Page configuration
# ----------------------------------------
st.set_page_config(
    page_title="Economic Activity Tracker",
    page_icon="📊",
    layout="wide"
)

# ----------------------------------------
# Google Login
# ----------------------------------------
def login_page():
    st.title("📊 Economic Activity Tracker")
    st.subheader("Welcome to EATI")

    st.write(
        "Track employment, business, and economic "
        "activity across the United States."
    )

    st.divider()

    st.write("Please sign in to continue.")

    if st.button("🔐 Login with Google", type="primary"):
        st.login("google")


# ----------------------------------------
# Authentication check
# ----------------------------------------
if not st.user.is_logged_in:
    login_page()
    st.stop()


# ----------------------------------------
# Sidebar
# ----------------------------------------
with st.sidebar:
    st.title("📊 EATI")

    st.write(f"Welcome, {st.user.name}!")

    if st.user.get("email"):
        st.caption(st.user.email)

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Employment News",
            "Business News",
            "Economic News"
        ]
    )

    st.divider()

    if st.button("🚪 Logout"):
        st.logout()


# ----------------------------------------
# Dashboard
# ----------------------------------------
if page == "Dashboard":

    st.title("Economic Activity Tracker")

    st.write(
        "Monitor employment trends, business "
        "developments, and economic activity."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Employment Articles", 0)

    with col2:
        st.metric("Business Articles", 0)

    with col3:
        st.metric("Economic Articles", 0)

    st.divider()

    st.subheader("Latest Economic Activity")

    st.info(
        "News collection and AI analysis "
        "will be integrated here."
    )


# ----------------------------------------
# Employment News
# ----------------------------------------
elif page == "Employment News":

    st.title("💼 Employment News")

    category = st.selectbox(
        "Employment Category",
        [
            "All",
            "Government Jobs",
            "Private Sector Jobs",
            "Startup Jobs",
            "Layoffs",
            "Hiring Announcements"
        ]
    )

    st.write(f"Selected category: {category}")

    st.info("Employment news will appear here.")


# ----------------------------------------
# Business News
# ----------------------------------------
elif page == "Business News":

    st.title("🏢 Business News")

    category = st.selectbox(
        "Business Category",
        [
            "All",
            "New Businesses",
            "Business Expansion",
            "Investments",
            "Mergers and Acquisitions",
            "Business Closures"
        ]
    )

    st.write(f"Selected category: {category}")

    st.info("Business news will appear here.")


# ----------------------------------------
# Economic News
# ----------------------------------------
elif page == "Economic News":

    st.title("📈 Economic News")

    region = st.selectbox(
        "Select Region",
        [
            "United States",
            "Texas",
            "California",
            "New York",
            "Florida",
            "Other"
        ]
    )

    st.write(f"Selected region: {region}")

    st.info("Economic indicators and news will appear here.")

