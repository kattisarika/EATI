import streamlit as st
import psycopg

# Navigation
home_col, dashboard_col = st.columns(2)

with home_col:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("home.py")

st.divider()


st.title("Feedback")

st.write("We value your feedback! Please share your thoughts below.")

with st.form("feedback_form", clear_on_submit=True):

    feedback = st.text_area(
        "Feedback",
        placeholder="Enter your feedback here...",
        height=200
    )

    submitted = st.form_submit_button(
        "Submit",
        type="primary"
    )

    if submitted:
        if not feedback.strip():
            st.warning("Please enter your feedback before submitting.")
        else:
            try:
                db_url = st.secrets["connections"]["postgres"]["url"]

                with psycopg.connect(db_url) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO public.user_feedback (feedback)
                            VALUES (%s)
                            """,
                            (feedback.strip(),)
                        )

                st.success("Thank you! Your feedback has been submitted.")

            except Exception:
                st.error(
                    "Unable to submit feedback. Please try again later."
                )
