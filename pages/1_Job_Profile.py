
import re
import ssl
from datetime import date
from html import escape

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
# PAGE STYLING
# ============================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --eati-navy: #16375B;
    --eati-blue: #1765A5;
    --eati-sky: #E8F1F9;
    --eati-accent: #0FA47A;
    --eati-ink: #2C3E50;
    --eati-muted: #6B7C93;
    --eati-line: #E1E7EF;
    --eati-shadow: 0 1px 2px rgba(22, 55, 91, .06),
                   0 8px 24px rgba(22, 55, 91, .06);
}

html, body, .stApp, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont,
                 'Segoe UI', sans-serif;
}

.stApp {
    background:
        radial-gradient(1100px 520px at 88% -8%,
                        rgba(23, 101, 165, .09), transparent 60%),
        #FBFCFE;
}

h1, h2, h3 {
    color: var(--eati-navy);
    letter-spacing: -0.02em;
}

/* ---------- Profile header card ---------- */

.jp-header {
    display: flex;
    align-items: center;
    gap: 1.1rem;
    background: #FFFFFF;
    border: 2px solid var(--eati-blue);
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    box-shadow: var(--eati-shadow);
    margin-bottom: 1.2rem;
}

.jp-avatar {
    flex: 0 0 auto;
    width: 58px;
    height: 58px;
    border-radius: 50%;
    background: var(--eati-sky);
    border: 2px solid var(--eati-blue);
    color: var(--eati-blue);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: 700;
}

.jp-header .who {
    flex: 1 1 auto;
    min-width: 0;
}

.jp-header h1 {
    margin: 0 0 .2rem 0;
    font-size: 1.65rem;
    font-weight: 800;
    line-height: 1.2;
}

.jp-header .sub {
    font-size: .9rem;
    color: var(--eati-muted);
    line-height: 1.5;
}

/* ---------- Section headers ---------- */

.jp-section {
    display: flex;
    align-items: center;
    gap: .75rem;
    margin: 1.6rem 0 .2rem 0;
    padding-bottom: .7rem;
    border-bottom: 1px solid var(--eati-line);
}

.jp-section .chip {
    flex: 0 0 auto;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: var(--eati-sky);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.05rem;
}

.jp-section .text h3 {
    margin: 0;
    font-size: 1.08rem;
    font-weight: 700;
    color: var(--eati-navy);
}

.jp-section .text .hint {
    font-size: .82rem;
    color: var(--eati-muted);
    line-height: 1.4;
}

/* ---------- Status pill ---------- */

.jp-pill {
    display: inline-block;
    font-size: .74rem;
    font-weight: 600;
    letter-spacing: .03em;
    padding: .25rem .7rem;
    border-radius: 999px;
    border: 1px solid transparent;
}

.jp-pill.saved {
    background: #E6F7F1;
    color: #0B7E5E;
    border-color: #BFEADC;
}

.jp-pill.draft {
    background: #FFF4E5;
    color: #9A6400;
    border-color: #FFE0B2;
}

/* ---------- Form card ---------- */

[data-testid="stForm"] {
    background: #FFFFFF;
    border: 1px solid var(--eati-line);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    box-shadow: var(--eati-shadow);
}

/* ---------- Inputs ---------- */

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input {
    border-radius: 10px !important;
    border: 1px solid var(--eati-line) !important;
    background: #FFFFFF !important;
    color: var(--eati-ink) !important;
    transition: border-color .15s ease, box-shadow .15s ease;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stDateInput"] input:focus {
    border-color: var(--eati-blue) !important;
    box-shadow: 0 0 0 3px rgba(23, 101, 165, .14) !important;
}

[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stDateInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stRadio"] label {
    font-weight: 600 !important;
    color: var(--eati-navy) !important;
}

[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border-color: var(--eati-line) !important;
}

/* ---------- Radio as pill group ---------- */

[data-testid="stRadioGroup"] {
    gap: .5rem;
}

[data-testid="stRadioGroup"] > label {
    background: #FFFFFF;
    border: 1px solid var(--eati-line);
    border-radius: 999px;
    padding: .35rem .95rem .35rem .55rem;
    transition: border-color .15s ease, background .15s ease;
}

[data-testid="stRadioGroup"] > label:hover {
    border-color: var(--eati-blue);
    background: var(--eati-sky);
}

/* ---------- Buttons ---------- */

div.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    border-radius: 10px;
    font-weight: 600;
    min-height: 46px;
    transition: transform .15s ease, box-shadow .15s ease;
}

div.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-1px);
}

div.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background: linear-gradient(135deg,
                                var(--eati-blue) 0%,
                                var(--eati-navy) 100%);
    border: none;
    color: #FFFFFF;
    box-shadow: 0 6px 18px rgba(23, 101, 165, .28);
}

/* Back button: white with a blue outline. */
.st-key-jp_back_home div.stButton > button {
    background: #FFFFFF !important;
    border: 2px solid var(--eati-blue) !important;
    color: var(--eati-blue) !important;
    box-shadow: none !important;
}

.st-key-jp_back_home div.stButton > button:hover {
    background: var(--eati-sky) !important;
    border-color: var(--eati-navy) !important;
    color: var(--eati-navy) !important;
}

.st-key-jp_back_home div.stButton > button p {
    color: inherit !important;
    pointer-events: none;
}

/* ---------- Alerts ---------- */

[data-testid="stAlert"] {
    border-radius: 12px;
}

@media (max-width: 768px) {
    .jp-header {
        padding: 1.2rem 1.1rem;
        gap: .8rem;
    }
}

</style>
""", unsafe_allow_html=True)


def section(icon, title, hint=""):
    """Render a consistent section header."""

    hint_html = (
        f'<div class="hint">{escape(hint)}</div>'
        if hint
        else ""
    )

    st.markdown(
        f"""
        <div class="jp-section">
            <div class="chip">{icon}</div>
            <div class="text">
                <h3>{escape(title)}</h3>
                {hint_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================
# GOOGLE AUTHENTICATION
# ============================================

if not st.user.get("is_logged_in", False):
    st.warning("Please log in to access your Job Profile.")
    st.page_link("app.py", label="Go to Login", icon="🔐")
    st.stop()


# -----------------------------------------
# Navigation
# -----------------------------------------

home_col, _ = st.columns([2, 7])

with home_col:
    if st.button(
        "🏠 Back to Home",
        key="jp_back_home",
        use_container_width=True,
    ):
        st.switch_page("home.py")

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

def _geocoder():
    """Nominatim client with an explicit CA bundle.

    Some Python installs (notably the python.org macOS build before
    "Install Certificates.command" is run) ship no CA bundle, which makes
    every HTTPS verify fail. Pointing at certifi keeps reverse geocoding
    working regardless of the interpreter's default trust store.
    """

    try:
        import certifi

        context = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        context = None

    return Nominatim(
        user_agent="eati_job_profile",
        ssl_context=context,
    )


# Nominatim allows roughly one request per second, and Streamlit reruns the
# script on every interaction. Cache by rounded coordinates (~11 m) so a
# rerun does not re-query for a location we already resolved.
@st.cache_data(ttl=3600, show_spinner=False)
def detect_city_state(latitude, longitude):

    result = _geocoder().reverse(
        (round(latitude, 4), round(longitude, 4)),
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

user_name = st.user.get("name") or "there"
user_email = st.user.get("email") or ""
initial = user_name.strip()[:1].upper() or "?"

st.markdown(
    f"""
    <div class="jp-header">
        <div class="jp-avatar">{escape(initial)}</div>
        <div class="who">
            <h1>👤 Job Profile</h1>
            <div class="sub">
                Complete your profile to help us understand your job
                preferences.{
                    f" Signed in as {escape(user_email)}."
                    if user_email
                    else ""
                }
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    user_id = get_app_user_id()
    existing = get_job_profile(user_id)

except Exception as e:
    st.error("Unable to load your Job Profile.")
    st.exception(e)
    st.stop()

st.markdown(
    '<span class="jp-pill saved">✓ Saved profile found</span>'
    if existing
    else '<span class="jp-pill draft">◷ No profile saved yet</span>',
    unsafe_allow_html=True,
)


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

section(
    "🎯",
    "Job Search Status",
    "Tell us whether you are actively looking right now.",
)

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

    # ----------------------------------------
    # LOCATION DETECTION
    # ----------------------------------------

    section(
        "📍",
        "Location",
        "Allow location access to detect your city and state "
        "automatically, or enter them manually below.",
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

        except Exception as location_error:
            st.warning(
                "Unable to detect location automatically. "
                "Please enter your city and state manually below."
            )

            with st.expander("Why did location detection fail?"):
                st.caption(
                    f"{type(location_error).__name__}: {location_error}"
                )

                if "CERTIFICATE_VERIFY_FAILED" in str(location_error):
                    st.caption(
                        "This Python install has no CA certificate "
                        "bundle. Run the 'Install Certificates.command' "
                        "script bundled with Python, or `pip install "
                        "certifi`, then restart the app."
                    )

    # ----------------------------------------
    # RELOCATION PREFERENCE
    # ----------------------------------------

    section(
        "🧭",
        "Relocation Preference",
        "Let employers know how far you are willing to move.",
    )

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

    section(
        "🛂",
        "Work Authorization",
        "Your current visa or work authorization status.",
    )

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

    # ----------------------------------------
    # MAIN JOB PROFILE FORM
    # ----------------------------------------

    with st.form("job_profile_form"):

        section(
            "🪪",
            "Personal Information",
            "How we identify and contact you.",
        )

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

        section(
            "💼",
            "Professional Information",
            "Skills, target role, and credentials.",
        )

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

        st.markdown(
            "<div style='height:.6rem'></div>",
            unsafe_allow_html=True,
        )

        submitted = st.form_submit_button(
            "💾 Save My Job Profile",
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

    if st.button(
        "💾 Save My Response",
        type="primary",
        use_container_width=True,
    ):

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

