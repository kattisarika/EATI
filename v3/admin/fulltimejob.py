import streamlit as st
import psycopg
from admin_auth import require_admin

st.set_page_config(
    page_title="Admin - Full-Time Roles",
    layout="wide"
)

require_admin()

st.title("Admin - Full-Time Roles")
st.write("Paste the complete full-time job posting below.")

with st.form("full_time_job_form", clear_on_submit=True):

    job_posting = st.text_area(
        "Full-Time Job Posting",
        height=350,
        placeholder="Paste the entire job description here..."
    )

    status = st.selectbox(
        "Status",
        ["draft", "published"],
        index=1
    )

    submitted = st.form_submit_button(
        "Save Full-Time Role",
        type="primary"
    )

    if submitted:
        if not job_posting.strip():
            st.error("Please enter a job posting.")
        else:
            try:
                db_url = st.secrets["connections"]["postgres"]["url"]

                user = st.user
                email = user.get("email", "")

                with psycopg.connect(db_url) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO public.full_time_jobs (
                                job_posting,
                                status,
                                created_by_email
                            )
                            VALUES (%s, %s, %s)
                            """,
                            (
                                job_posting.strip(),
                                status,
                                email
                            )
                        )

                st.success("Full-time role saved successfully!")

            except Exception as e:
                st.error(f"Unable to save full-time role: {e}")
