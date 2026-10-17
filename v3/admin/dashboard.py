import streamlit as st
from admin_auth import require_admin

email = require_admin()

st.title("🛡️ EATI Admin Dashboard")
st.caption(f"Signed in as {email}")

st.subheader("Job Management")

with st.container(border=True):
    st.markdown("### 📝 Vendor Job Form")
    st.write(
        "Paste vendor job postings and prepare them "
        "for AI extraction and publishing."
    )

col1, col2 = st.columns(2)

with col1:
    if st.button("Vendor Jobs", use_container_width=True):
        st.switch_page("v3/admin/vendorjob.py")

with col2:
    if st.button("Full-Time Roles", use_container_width=True):
        st.switch_page("v3/admin/fulltimejob.py")

with st.sidebar:
    if st.button("Logout", key="admin_logout"):
        st.logout()
