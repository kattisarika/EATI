
import streamlit as st
import psycopg
from datetime import date

st.set_page_config(
    page_title="Mock Interviews | EATI",
    layout="wide"
)

# -----------------------------------------
# Authentication
# -----------------------------------------
if not st.user.get("is_logged_in", False):
    st.warning(
        "Please sign in with Google to request "
        "mock interview preparation."
    )

    if st.button("🏠 Go to EATI Home"):
        st.switch_page("home.py")

    st.stop()

# -----------------------------------------
# Navigation
# -----------------------------------------
if st.button("🏠 Back to EATI Dashboard"):
    st.switch_page("home.py")

st.divider()

# -----------------------------------------
# Page heading
# -----------------------------------------
st.title("🎤 Mock Interview Preparation")

st.write(
    "Preparing for an interview? Submit your details "
    "and a Subject Matter Expert (SME) will review "
    "your request and contact you."
)

# -----------------------------------------
# Request form
# -----------------------------------------
with st.form(
    "mock_interview_request",
    clear_on_submit=True
):

    full_name = st.text_input(
        "Full Name *",
        placeholder="Enter your full name"
    )

    email = st.text_input(
        "Email Address *",
        value=st.user.get("email", ""),
        placeholder="you@example.com"
    )

    job_role = st.text_input(
        "Role You Are Interviewing For *",
        placeholder=(
            "e.g., Business Analyst, QA Engineer, "
            "Product Owner"
        )
    )

    interview_date = st.date_input(
        "Interview Date (Optional)",
        value=None,
        min_value=date.today()
    )

    additional_information = st.text_area(
        "Additional Information",
        placeholder=(
            "Company name, interview round, "
            "topics you need help with..."
        ),
        height=120
    )

    submitted = st.form_submit_button(
        "Submit Interview Request",
        type="primary",
        use_container_width=True
    )

# -----------------------------------------
# Save request to Supabase
# -----------------------------------------
if submitted:

    if not full_name.strip():
        st.error("Please enter your full name.")
        st.stop()

    if not email.strip() or "@" not in email:
        st.error("Please enter a valid email address.")
        st.stop()

    if not job_role.strip():
        st.error(
            "Please enter the role you are interviewing for."
        )
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
                    INSERT INTO public.mock_interview_requests (
                        full_name,
                        email,
                        job_role,
                        interview_date,
                        additional_information,
                        status
                    )
                    VALUES (%s, %s, %s, %s, %s, 'pending')
                    RETURNING id
                    """,
                    (
                        full_name.strip(),
                        email.strip(),
                        job_role.strip(),
                        interview_date,
                        additional_information.strip()
                    )
                )

                request_id = cur.fetchone()[0]

        st.success(
            "Your mock interview request has been "
            "submitted successfully!"
        )

        st.info(
            "An SME will review your request "
            "and contact you using the email provided."
        )

        st.caption(f"Request ID: {request_id}")

    except Exception:
        st.error(
            "We couldn't save your request. "
            "Please try again later."
        )

