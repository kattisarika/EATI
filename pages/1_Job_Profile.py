
import re
from datetime import date

import psycopg
import streamlit as st
from geopy.geocoders import Nominatim
from streamlit_geolocation import streamlit_geolocation


# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Job Profile | EATI",
    page_icon="👤",
    layout="wide",
)


# -----------------------------------
# Google Authentication
# -----------------------------------
if not st.user.get("is_logged_in", False):
    st.warning("Please log in to access your Job Profile.")
    st.page_link("app.py", label="Go to Login", icon="🔐")
    st.stop()


# -----------------------------------
# Database Connection
# -----------------------------------
def get_connection():
    db_url = st.secrets["connections"]["postgres"]["url"]
    return psycopg.connect(db_url, connect_timeout=10)


def get_app_user_id():
    google_sub = st.user.get("sub")

    if not google_sub:
        raise ValueError("Google user ID is missing.")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id
                FROM public.app_users
                WHERE google_sub = %s
                """,
                (google_sub,),
            )
            result = cur.fetchone()

    if result is None:
        raise ValueError(
            "Your account was not found in app_users. "
            "Please return to the dashboard and log in again."
        )

    return result[0]


# -----------------------------------
# Retrieve Existing Profile
# -----------------------------------
def get_job_profile(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    looking_for_job,
                    full_name,
                    date_of_birth,
                    phone_number,
                    skills,
                    location,
                    willing_to_relocate,
                    relocation_other,
                    desired_role,
                    certifications,
                    linkedin_profile
                FROM public.job_profiles
                WHERE user_id = %s
                """,
                (user_id,),
            )

            result = cur.fetchone()

    if not result:
        return None

    fields = [
        "looking_for_job",
        "full_name",
        "date_of_birth",
        "phone_number",
        "skills",
        "location",
        "willing_to_relocate",
        "relocation_other",
        "desired_role",
        "certifications",
        "linkedin_profile",
    ]

    return dict(zip(fields, result))


# -----------------------------------
# Save Job Profile
# -----------------------------------
def save_job_profile(user_id, profile):

    sql = """
        INSERT INTO public.job_profiles (
            user_id,
            looking_for_job,
            full_name,
            date_of_birth,
            phone_number,
            skills,
            location,
            willing_to_relocate,
            relocation_other,
            desired_role,
            certifications,
            linkedin_profile
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (user_id)
        DO UPDATE SET
            looking_for_job = EXCLUDED.looking_for_job,
            full_name = EXCLUDED.full_name,
            date_of_birth = EXCLUDED.date_of_birth,
            phone_number = EXCLUDED.phone_number,
            skills = EXCLUDED.skills,
            location = EXCLUDED.location,
            willing_to_relocate = EXCLUDED.willing_to_relocate,
            relocation_other = EXCLUDED.relocation_other,
            desired_role = EXCLUDED.desired_role,
            certifications = EXCLUDED.certifications,
            linkedin_profile = EXCLUDED.linkedin_profile,
            updated_at = NOW()
    """

    values = (
        user_id,
        profile["looking_for_job"],
        profile["full_name"],
        profile["date_of_birth"],
        profile["phone_number"],
        profile["skills"],
        profile["location"],
        profile["willing_to_relocate"],
        profile["relocation_other"],
        profile["desired_role"],
        profile["certifications"],
        profile["linkedin_profile"],
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, values)


# -----------------------------------
# Location Detection
# -----------------------------------
def detect_city_state(latitude, longitude):
    geolocator = Nominatim(user_agent="eati_job_profile")

    result = geolocator.reverse(
        (latitude, longitude),
        language="en",
        timeout=10,
    )

    if not result:
        return None

    address = result.raw.get("address", {})

    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
        or ""
    )

    state = address.get("state", "")

    if not city or not state:
        return None

    return f"{city}, {state}"


# -----------------------------------
# Initialize User
# -----------------------------------
st.title("👤 Job Profile")
st.write("Complete your profile to help us understand your job preferences.")

try:
    user_id = get_app_user_id()
    existing = get_job_profile(user_id)

except Exception as e:
    st.error("Unable to load your Job Profile.")
    st.exception(e)
    st.stop()


# -----------------------------------
# Initialize Session State
# -----------------------------------
if "job_profile_user_id" not in st.session_state or (
    st.session_state["job_profile_user_id"] != str(user_id)
):
    st.session_state["job_profile_user_id"] = str(user_id)

    st.session_state["job_looking"] = (
        "Yes"
        if existing and existing["looking_for_job"]
        else "No"
        if existing
        else "Yes"
    )

    st.session_state["job_relocate"] = (
        existing.get("willing_to_relocate") or "No"
        if existing
        else "No"
    )

    st.session_state["job_location"] = (
        existing.get("location") or ""
        if existing
        else ""
    )

    st.session_state["job_relocation_other"] = (
        existing.get("relocation_other") or ""
        if existing
        else ""
    )


# -----------------------------------
# Looking for Job
# -----------------------------------
looking_for_job = st.radio(
    "Are you looking for a job?",
    ["Yes", "No"],
    horizontal=True,
    key="job_looking",
)


# -----------------------------------
# Form for Job Seekers
# -----------------------------------
if looking_for_job == "Yes":

    st.divider()

    # Location detection outside the form
    st.subheader("📍 Location")

    st.caption(
        "Use location detection or enter your city and state manually."
    )

    location_data = streamlit_geolocation()

    if (
        location_data
        and location_data.get("latitude") is not None
        and location_data.get("longitude") is not None
    ):
        try:
            detected = detect_city_state(
                location_data["latitude"],
                location_data["longitude"],
            )

            if detected:
                if st.session_state.get("last_detected_location") != detected:
                    st.session_state["job_location"] = detected
                    st.session_state["last_detected_location"] = detected

                st.success(f"Detected location: {detected}")

        except Exception:
            st.warning(
                "Unable to detect location. "
                "Please enter your city and state manually."
            )

    # Relocation outside the form for immediate UI updates
    st.subheader("Relocation Preference")

    relocate = st.radio(
        "Are you willing to relocate?",
        ["Yes", "No", "Other"],
        horizontal=True,
        key="job_relocate",
    )

    if relocate == "Other":
        relocation_other = st.text_area(
            "Please specify your relocation preference",
            placeholder=(
                "e.g. Only within Texas, remote preferred, "
                "or relocation with assistance"
            ),
            key="job_relocation_other",
        )
    else:
        relocation_other = None

    st.divider()

    # -----------------------------------
    # Job Profile Form
    # -----------------------------------
    with st.form("job_profile_form"):

        st.subheader("Personal Information")

        name = st.text_input(
            "Name",
            value=(
                existing.get("full_name")
                if existing and existing.get("full_name")
                else st.user.get("name") or ""
            ),
            placeholder="Enter your full name",
        )

        col1, col2 = st.columns(2)

        with col1:
            dob = st.date_input(
                "Date of Birth",
                value=(
                    existing.get("date_of_birth")
                    if existing
                    else None
                ),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
            )

        with col2:
            phone_number = st.text_input(
                "Phone Number",
                value=(
                    existing.get("phone_number") or ""
                    if existing
                    else ""
                ),
                placeholder="(123) 456-7890",
                max_chars=25,
            )

        location = st.text_input(
            "Location (City, State)",
            key="job_location",
            placeholder="Dallas, TX",
        )

        st.subheader("Professional Information")

        skills = st.text_area(
            "Skills",
            value=(
                existing.get("skills") or ""
                if existing
                else ""
            ),
            placeholder="Python, SQL, Selenium, Business Analysis",
        )

        role = st.text_input(
            "Role",
            value=(
                existing.get("desired_role") or ""
                if existing
                else ""
            ),
            placeholder="QA Engineer, Business Analyst, Product Owner",
        )

        certifications = st.text_area(
            "Certifications",
            value=(
                existing.get("certifications") or ""
                if existing
                else ""
            ),
            placeholder="CSPO, AWS, ISTQB",
        )

        linkedin_profile = st.text_input(
            "LinkedIn URL",
            value=(
                existing.get("linkedin_profile") or ""
                if existing
                else ""
            ),
            placeholder="https://www.linkedin.com/in/your-profile",
            help="Optional: Enter your LinkedIn profile URL.",
        )

        submitted = st.form_submit_button(
            "Submit",
            type="primary",
            use_container_width=True,
        )

    # -----------------------------------
    # Save Form Submission
    # -----------------------------------
    if submitted:

        linkedin_profile = linkedin_profile.strip()
        phone_number = phone_number.strip()

        valid_linkedin = (
            not linkedin_profile
            or re.fullmatch(
                r"https://(www\.)?linkedin\.com/in/"
                r"[A-Za-z0-9_%\-]+/?",
                linkedin_profile,
                re.IGNORECASE,
            )
        )

        valid_phone = (
            not phone_number
            or (
                len(re.sub(r"\D", "", phone_number)) >= 10
                and len(re.sub(r"\D", "", phone_number)) <= 15
            )
        )

        if not name.strip():
            st.error("Please enter your name.")

        elif not role.strip():
            st.error("Please enter your desired role.")

        elif not valid_phone:
            st.error("Please enter a valid phone number.")

        elif not valid_linkedin:
            st.error("Please enter a valid LinkedIn URL.")

        elif relocate == "Other" and not (
            relocation_other and relocation_other.strip()
        ):
            st.error("Please specify your relocation preference.")

        else:
            profile = {
                "looking_for_job": True,
                "full_name": name.strip(),
                "date_of_birth": dob,
                "phone_number": phone_number or None,
                "skills": skills.strip(),
                "location": location.strip(),
                "willing_to_relocate": relocate,
                "relocation_other": (
                    relocation_other.strip()
                    if relocate == "Other"
                    else None
                ),
                "desired_role": role.strip(),
                "certifications": certifications.strip(),
                "linkedin_profile": linkedin_profile or None,
            }

            try:
                save_job_profile(user_id, profile)
                st.success(
                    "Your Job Profile has been saved successfully!"
                )

            except Exception as e:
                st.error("Unable to save your Job Profile.")
                st.exception(e)


# -----------------------------------
# User Not Looking for a Job
# -----------------------------------
else:
    st.info("You have selected No.")

    if st.button("Submit", type="primary"):

        profile = {
            "looking_for_job": False,
            "full_name": None,
            "date_of_birth": None,
            "phone_number": None,
            "skills": None,
            "location": None,
            "willing_to_relocate": None,
            "relocation_other": None,
            "desired_role": None,
            "certifications": None,
            "linkedin_profile": None,
        }

        try:
            save_job_profile(user_id, profile)
            st.success("Your response has been saved successfully!")

        except Exception as e:
            st.error("Unable to save your response.")
            st.exception(e)

