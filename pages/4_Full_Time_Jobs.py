
import streamlit as st

st.set_page_config(
    page_title="Full Time Jobs | EATI",
    layout="wide"
)

# Authentication
if not st.user.get("is_logged_in", False):
    st.warning(
        "Please sign in with Google from the EATI home page."
    )

    if st.button("🏠 Go to EATI Home"):
        st.switch_page("home.py")

    st.stop()

# Navigation
if st.button("🏠 Back to EATI Dashboard"):
    st.switch_page("home.py")

st.divider()

# Full Time Jobs
st.title("💼 Full Time Jobs")

st.write(
    "Explore full-time employment opportunities."
)

st.info(
    "This page is ready for full-time job listings "
    "to be added."
)

