
import streamlit as st
import psycopg
from admin_auth import require_admin

# -----------------------------------------
# Administrator authorization
# -----------------------------------------
admin_email = require_admin()

st.title("📝 EATI Vendor Job Form")
st.caption(f"Administrator: {admin_email}")

st.write(
    "Paste the complete vendor job posting below. "
    "The original text will be saved without AI processing."
)

# -----------------------------------------
# Vendor Job Form
# -----------------------------------------
with st.form("vendor_job_form", clear_on_submit=True):

    job_posting = st.text_area(
        "Vendor Job Posting *",
        height=350,
        placeholder=(
            "Title: Forward Deployment Engineer\n"
            "Location: Atlanta, GA Hybrid\n"
            "Contract\n"
            "12+ Years of experience\n\n"
            "Paste the full job description here..."
        )
    )

    status = st.radio(
        "Posting Status",
        options=["draft", "published"],
        format_func=lambda value: value.capitalize(),
        horizontal=True,
        index=1
    )

    submitted = st.form_submit_button(
        "Save Job Posting",
        type="primary",
        use_container_width=True
    )

# -----------------------------------------
# Save to Supabase
# -----------------------------------------
if submitted:

    if not job_posting.strip():
        st.error("Please enter a job posting.")
        st.stop()

    try:
        db_url = st.secrets["connections"]["postgres"]["url"]

        with psycopg.connect(
            db_url,
            connect_timeout=10
        ) as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO public.vendor_jobs (
                        job_posting,
                        status,
                        created_by_email,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        NOW(),
                        NOW()
                    )
                    RETURNING id
                    """,
                    (
                        job_posting,
                        status,
                        admin_email
                    )
                )

                job_id = cur.fetchone()[0]

        st.success(
            f"Job posting saved successfully! "
            f"Status: {status.capitalize()}"
        )

        st.caption(f"Job ID: {job_id}")

    except Exception as e:
        st.error("Unable to save the job posting.")
        st.exception(e)

# -----------------------------------------
# Navigation
# -----------------------------------------
st.divider()

if st.button("⬅ Back to Admin Dashboard"):
    st.switch_page("v3/admin/dashboard.py")

