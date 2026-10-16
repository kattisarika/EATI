
import re
from datetime import date

import psycopg
import streamlit as st
from geopy.geocoders import Nominatim
from streamlit_geolocation import streamlit_geolocation


# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Job Profile | EATI",
    page_icon="👤",
    layout="wide",
)


# ============================================
# GOOGLE AUTHENTICATION
# ============================================

if not st.user.get("is_logged_in", False):
    st.warning("Please log in to access your Job Profile.")
    st.page_link("app.py", label="Go to Login", icon="🔐")
    st.stop()


# ============================================
# DATABASE CONNECTION
# ============================================

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
            "Your Google account is not registered. "
            "Please return to the dashboard and log in again."
        )

    return result[0]


# ============================================
# RETRIEVE EXISTING JOB PROFILE
# ============================================

def get_job_profile(user_id):

    sql = """
        SELECT
            looking_for_job,
            full_name,
            date_of_birth,
            phone_number,
            skills,
            location,
            state,
            willing_to_relocate,
            relocation_other,
            desired_role,
            certifications,
            linkedin_profile,
            visa_status,
            visa_status_other
        FROM public.job_profiles
        WHERE user_id = %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
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
        "state",
        "willing_to_relocate",
        "relocation_other",
        "desired_role",
        "certifications",
        "linkedin_profile",
        "visa_status",
        "visa_status_other",
    ]

    return dict(zip(fields, result))


# ============================================
# SAVE JOB PROFILE TO SUPABASE
# ============================================

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
            state,
            willing_to_relocate,
            relocation_other,
            desired_role,
            certifications,
            linkedin_profile,
            visa_status,
            visa_status_other
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        ON CONFLICT (user_id)
        DO UPDATE SET
            looking_for_job = EXCLUDED.looking_for_job,
            full_name = EXCLUDED.full_name,
            date_of_birth = EXCLUDED.date_of_birth,
            phone_number = EXCLUDED.phone_number,
            skills = EXCLUDED.skills,
            location = EXCLUDED.location,
            state = EXCLUDED.state,
            willing_to_relocate = EXCLUDED.willing_to_relocate,
            relocation_other = EXCLUDED.relocation_other,
            desired_role = EXCLUDED.desired_role,
            certifications = EXCLUDED.certifications,
            linkedin_profile = EXCLUDED.linkedin_profile,
            visa_status = EXCLUDED.visa_status,
            visa_status_other = EXCLUDED.visa_status_other,
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
        profile["state"],
        profile["willing_to_relocate"],
        profile["relocation_other"],
        profile["desired_role"],
        profile["certifications"],
        profile["linkedin_profile"],
        profile["visa_status"],
        profile["visa_status_other"],
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, values)


# ============================================
# DETECT CITY AND STATE
# ============================================

def detect_city_state(latitude, longitude):

    geolocator = Nominatim(user_agent="eati_job_profile")

    result = geolocator.reverse(
        (latitude, longitude),
        language="en",
        timeout=10,
    )

    if not result:
        return None, None

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

    return city, state


# ============================================
# LOAD USER AND EXISTING PROFILE
# ============================================

st.title("👤 Job Profile")

st.write(
    "Complete your profile to help us understand "
    "your job preferences."
)

try:
    user_id = get_app_user_id()
    existing = get_job_profile(user_id)

except Exception as e:
    st.error("Unable to load your Job Profile.")
    st.exception(e)
    st.stop()


# ============================================
# INITIALIZE SESSION STATE
# ============================================

if st.session_state.get("job_profile_user_id") != str(user_id):

    st.session_state["job_profile_user_id"] = str(user_id)

    st.session_state["job_looking"] = (
        "Yes"
        if not existing or existing["looking_for_job"]
        else "No"
    )

    saved_relocation = (
        existing.get("willing_to_relocate")
        if existing
        else None
    )

    st.session_state["job_relocate"] = (
        saved_relocation
        if saved_relocation in ("Yes", "No", "Other")
        else "No"
    )

    st.session_state["job_relocation_other"] = (
        existing.get("relocation_other") or ""
        if existing
        else ""
    )

    st.session_state["job_city"] = (
        existing.get("location") or ""
        if existing
        else ""
    )

    st.session_state["job_state"] = (
        existing.get("state") or ""
        if existing
        else ""
    )

    saved_visa = (
        existing.get("visa_status")
        if existing
        else None
    )

    visa_options = [
        "H1",
        "H4 EAD",
        "OPT",
        "US Citizen",
        "L1",
        "Other",
    ]

    st.session_state["job_visa_status"] = (
        saved_visa
        if saved_visa in visa_options
        else None
    )

    st.session_state["job_visa_other"] = (
        existing.get("visa_status_other") or ""
        if existing
        else ""
    )


# ============================================
# ARE YOU LOOKING FOR A JOB?
# ============================================

looking_for_job = st.radio(
    "Are you looking for a job?",
    ["Yes", "No"],
    horizontal=True,
    key="job_looking",
)


# ============================================
# JOB SEEKER FORM
# ============================================

if looking_for_job == "Yes":

    st.divider()

    # ----------------------------------------
    # LOCATION DETECTION
    # ----------------------------------------

    st.subheader("📍 Location")

    st.caption(
        "Allow location access to detect your city "
        "and state automatically, or enter them manually."
    )

    location_data = streamlit_geolocation()

    if (
        location_data
        and location_data.get("latitude") is not None
        and location_data.get("longitude") is not None
    ):
        try:
            city_detected, state_detected = detect_city_state(
                location_data["latitude"],
                location_data["longitude"],
            )

            detected_location = (
                city_detected,
                state_detected,
            )

            if city_detected and state_detected:

                if (
                    st.session_state.get("last_detected_location")
                    != detected_location
                ):
                    st.session_state["job_city"] = city_detected
                    st.session_state["job_state"] = state_detected

                    st.session_state["last_detected_location"] = (
                        detected_location
                    )

                st.success(
                    f"Detected location: "
                    f"{city_detected}, {state_detected}"
                )

        except Exception:
            st.warning(
                "Unable to detect location. "
                "Please enter your city and state manually."
            )

    # ----------------------------------------
    # RELOCATION PREFERENCE
    # ----------------------------------------

    st.subheader("Relocation Preference")

    relocate = st.radio(
        "Are you willing to relocate?",
        ["Yes", "No", "Other"],
        horizontal=True,
        key="job_relocate",
    )

    relocation_other = None

    if relocate == "Other":

        relocation_other = st.text_area(
            "Please specify your relocation preference",
            placeholder=(
                "Example: Only within Texas, "
                "remote preferred, or relocation "
                "with assistance."
            ),
            key="job_relocation_other",
        )

    # ----------------------------------------
    # VISA STATUS
    # ----------------------------------------

    st.subheader("Work Authorization")

    visa_options = [
        "H1",
        "H4 EAD",
        "OPT",
        "US Citizen",
        "L1",
        "Other",
    ]

    saved_visa = st.session_state.get("job_visa_status")

    visa_status = st.selectbox(
        "Visa Status",
        visa_options,
        index=(
            visa_options.index(saved_visa)
            if saved_visa in visa_options
            else None
        ),
        placeholder="Select your visa status",
        key="job_visa_status",
    )

    visa_status_other = None

    if visa_status == "Other":

        visa_status_other = st.text_input(
            "Please specify your visa status",
            placeholder="Enter your visa status",
            key="job_visa_other",
        )

    st.divider()

    # ----------------------------------------
    # MAIN JOB PROFILE FORM
    # ----------------------------------------

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

        # ------------------------------------
        # CITY AND STATE
        # ------------------------------------

        city_col, state_col = st.columns(2)

        with city_col:

            city = st.text_input(
                "City",
                key="job_city",
                placeholder="Dallas",
            )

        with state_col:

            state = st.text_input(
                "State",
                key="job_state",
                placeholder="Texas",
            )

        # ------------------------------------
        # PROFESSIONAL INFORMATION
        # ------------------------------------

        st.subheader("Professional Information")

        skills = st.text_area(
            "Skills",
            value=(
                existing.get("skills") or ""
                if existing
                else ""
            ),
            placeholder=(
                "Python, SQL, Selenium, "
                "Business Analysis"
            ),
        )

        role = st.text_input(
            "Role",
            value=(
                existing.get("desired_role") or ""
                if existing
                else ""
            ),
            placeholder=(
                "QA Engineer, Business Analyst, "
                "Product Owner"
            ),
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
            placeholder=(
                "https://www.linkedin.com/in/your-profile"
            ),
            help="Optional LinkedIn profile URL.",
        )

        submitted = st.form_submit_button(
            "Submit",
            type="primary",
            use_container_width=True,
        )

    # ----------------------------------------
    # VALIDATE AND SAVE FORM
    # ----------------------------------------

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

        phone_digits = re.sub(r"\D", "", phone_number)

        valid_phone = (
            not phone_number
            or 10 <= len(phone_digits) <= 15
        )

        if not name.strip():
            st.error("Please enter your name.")

        elif not role.strip():
            st.error("Please enter your desired role.")

        elif not city.strip():
            st.error("Please enter your city.")

        elif not state.strip():
            st.error("Please enter your state.")

        elif not valid_phone:
            st.error("Please enter a valid phone number.")

        elif not valid_linkedin:
            st.error("Please enter a valid LinkedIn URL.")

        elif (
            relocate == "Other"
            and not (
                relocation_other
                and relocation_other.strip()
            )
        ):
            st.error(
                "Please specify your relocation preference."
            )

        elif not visa_status:
            st.error("Please select your visa status.")

        elif (
            visa_status == "Other"
            and not (
                visa_status_other
                and visa_status_other.strip()
            )
        ):
            st.error("Please specify your visa status.")

        else:

            profile = {
                "looking_for_job": True,
                "full_name": name.strip(),
                "date_of_birth": dob,
                "phone_number": phone_number or None,
                "skills": skills.strip(),
                "location": city.strip(),
                "state": state.strip(),
                "willing_to_relocate": relocate,
                "relocation_other": (
                    relocation_other.strip()
                    if relocate == "Other"
                    else None
                ),
                "desired_role": role.strip(),
                "certifications": certifications.strip(),
                "linkedin_profile": (
                    linkedin_profile or None
                ),
                "visa_status": visa_status,
                "visa_status_other": (
                    visa_status_other.strip()
                    if visa_status == "Other"
                    else None
                ),
            }

            try:
                save_job_profile(user_id, profile)

                st.success(
                    "Your Job Profile has been "
                    "saved successfully!"
                )

            except Exception as e:
                st.error(
                    "Unable to save your Job Profile."
                )
                st.exception(e)


# ============================================
# NOT LOOKING FOR A JOB
# ============================================

else:

    st.info(
        "You have selected No. "
        "Click Submit to save your response."
    )

    if st.button("Submit", type="primary"):

        profile = {
            "looking_for_job": False,
            "full_name": None,
            "date_of_birth": None,
            "phone_number": None,
            "skills": None,
            "location": None,
            "state": None,
            "willing_to_relocate": None,
            "relocation_other": None,
            "desired_role": None,
            "certifications": None,
            "linkedin_profile": None,
            "visa_status": None,
            "visa_status_other": None,
        }

        try:
            save_job_profile(user_id, profile)

            st.success(
                "Your response has been "
                "saved successfully!"
            )

        except Exception as e:
            st.error(
                "Unable to save your response."
            )
            st.exception(e)

