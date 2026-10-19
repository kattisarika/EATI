"""EATI navigation entrypoint. Keep this file as Streamlit Cloud main file."""
import streamlit as st
from pathlib import Path

from idle_timeout import install_idle_timeout

st.set_page_config(page_title="Economic Activity Tracker", page_icon="📊", layout="wide")
install_idle_timeout()
logo_path = Path(__file__).parent / "assets" / "eati_logo.png"

if logo_path.exists():
    st.image(str(logo_path), width=350)
else:
    st.warning("EATI logo image not found.")
# Welcome message shown above the selected page.
st.markdown("""
### Welcome to EATI — Your Gateway to Employment Opportunities and Workforce Insights!

Stay informed with the latest news on hiring trends, layoffs, job creation, and company
expansions across the United States. Browse full-time and contract job opportunities,
create your professional profile, and explore career development resources to support
your job search. EATI brings together workforce news, employment opportunities, and
career tools in one convenient platform to help you make informed decisions and take
the next step in your career.
""")
st.divider()

# st.navigation supports single-segment URL paths, not nested /v3/admin paths.
# Admin access is enforced inside the admin pages, NOT by hiding links.
pages = [
    st.Page("home.py", title="EATI Dashboard", icon="📊", default=True, url_path=""),
    st.Page("pages/1_Job_Profile.py", title="Job Profile", icon="📄"),
    st.Page("pages/2_Mock_Interviews.py", title="Mock Interviews", icon="🎤"),
    st.Page("pages/3_Jobs_By_Vendors.py", title="Jobs By Vendors", icon="💼"),
    st.Page("pages/4_Full_Time_Jobs.py", title="Full Time Jobs", icon="🏢"),
    st.Page("v3/admin/dashboard.py", title="Admin Dashboard", icon="🛡️", url_path="v3-admin"),
    st.Page("v3/admin/vendorjob.py", title="Vendor Job Form", icon="📝", url_path="v3-admin-vendorjob"),
    st.Page(
    "v3/admin/fulltimejob.py",
    title="Admin - Full-Time Roles",
    url_path="admin-full-time-roles",
    default=False
),
   st.Page("pages/5_Feedback.py", title="Feedback", icon="💬", url_path="Feedback"),
]

st.navigation(pages, position="hidden").run()
