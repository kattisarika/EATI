import streamlit as st

st.set_page_config(page_title="Job Profile | EATI", layout="wide")

if not st.user.get("is_logged_in", False):
    st.warning("Please sign in with Google from the EATI home page.")
    st.page_link("app.py", label="Go to login", icon="🏠")
    st.stop()

st.page_link("app.py", label="← Back to EATI Dashboard", icon="🏠")
st.title("Job Profile")
st.write("Build and manage your professional profile.")
st.info("This page is ready for its features to be added. No job listings or user data are populated yet.")
