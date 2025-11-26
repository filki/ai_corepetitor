import streamlit as st
from services.auth_service import AuthService
from services.challenge_service import ChallengeService
from services.db_service import DbService
from services.tutor_service import TutorService

# Site configuration (MUSI być pierwsza linijka!)
st.set_page_config(page_title="Generator Zadań", page_icon="🧮")

# Authentication (zaraz po page_config!)
AuthService.require_auth(st.secrets["APP_PASSWORD"])


# Cached service instances
@st.cache_resource
def get_challenge_service(api_key):
    return ChallengeService(api_key)


@st.cache_resource
def get_db_service():
    return DbService()


@st.cache_resource
def get_tutor_service(api_key):
    return TutorService(api_key)


challenge_service = get_challenge_service(st.secrets["GOOGLE_API_KEY"])
db_service = get_db_service()
tutor_service = get_tutor_service(st.secrets["GOOGLE_API_KEY"])

if "current_profile" not in st.session_state:
    st.header("👤 Kto dzisiaj się uczy?")

    profiles = db_service.get_all_profiles().data
    cols = st.columns(len(profiles) + 1)

    for i, profile in enumerate(profiles):
        with cols[i]:
            st.subheader(profile["nickname"])
            st.metric("XP", profile["total_xp"])
            if st.button("Wybierz", key=f"select_{profile['id']}"):
                st.session_state["current_profile"] = profile
                st.rerun()

    with cols[-1]:
        st.subheader("➕ Nowy")
        with st.form("add_profile"):
            nick = st.text_input("Imię")
            level = st.selectbox("Poziom", ["podstawowka_1_3", "podstawowka_4_8"])
            if st.form_submit_button("Dodaj"):
                db_service.create_profile(nick, level)
                st.rerun()
    st.stop()
st.title("🧮 Generator Zadań")

# --- Sidebar ---
with st.sidebar:
    st.header(f"👤 {st.session_state['current_profile']['nickname']}")
    st.metric("XP", st.session_state["current_profile"]["total_xp"])
    if st.button("Wyloguj / Zmień profil"):
        del st.session_state["current_profile"]
        st.rerun()

# --- Chat Interface ---
st.subheader("💬 Wirtualny Nauczyciel")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("O co chcesz zapytać?"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Myślę..."):
            try:
                # Prepare history (excluding the last user message which we send now)
                chat_session = tutor_service.get_chat_session(
                    st.session_state.messages[:-1]
                )
                response = tutor_service.send_message(chat_session, prompt)

                st.markdown(response.text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response.text}
                )
            except Exception as e:
                st.error(f"Błąd: {e}")

# --- Challenge Generator ---
st.divider()
st.header("🎯 Tryb Treningowy")

# Category Selector
category = st.selectbox("Wybierz kategorię:", ["Algebra", "Geometria", "Arytmetyka"])

# Generate Button
if st.button("Generuj Zadanie"):
    with st.spinner("Generuję zadanie..."):
        try:
            challenge = challenge_service.generate_challenge(
                st.session_state["current_profile"]["id"], category
            )
            st.session_state["current_challenge"] = challenge
            # Clear previous result if any
            if "submission_result" in st.session_state:
                del st.session_state["submission_result"]
        except Exception as e:
            st.error(f"Błąd generowania: {e}")

# Display Challenge
if "current_challenge" in st.session_state:
    challenge = st.session_state["current_challenge"]

    st.info(f"📝 Zadanie: {challenge['problem_text']}")

    # Answer Input
    with st.form("answer_form"):
        user_answer = st.text_input("Twoja odpowiedź:")
        submitted = st.form_submit_button("Sprawdź")

        if submitted:
            result = challenge_service.submit_answer(
                challenge["id"], st.session_state["current_profile"]["id"], user_answer
            )
            st.session_state["submission_result"] = result

            # Refresh profile to update XP
            st.session_state["current_profile"] = db_service.get_profile_by_id(
                st.session_state["current_profile"]["id"]
            ).data[0]
            st.rerun()

# Display Result
if "submission_result" in st.session_state:
    result = st.session_state["submission_result"]
    if result["is_correct"]:
        st.success(f"{result['feedback']} (+{result['xp_earned']} XP)")
        st.balloons()
    else:
        st.error(f"{result['feedback']}")
