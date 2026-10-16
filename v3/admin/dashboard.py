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

    if st.button("Open Vendor Job Form", type="primary"):
        st.switch_page("v3/admin/vendorjob.py")

with st.sidebar:
    if st.button("Logout", key="admin_logout"):
        st.logout()
