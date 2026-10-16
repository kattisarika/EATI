"""EATI navigation entrypoint. Keep this file as Streamlit Cloud main file."""
import streamlit as st

st.set_page_config(page_title="Economic Activity Tracker", page_icon="📊", layout="wide")
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
]

st.navigation(pages, position="hidden").run()
