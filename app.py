import streamlit as st
from services.auth_service import AuthService
from services.challenge_service import ChallengeService
from services.db_service import DbService
from services.tutor_service import TutorService
from helpers.utils import reset_challenge
import time

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

    profiles_response = db_service.get_all_profiles()
    if not profiles_response:
        st.error("🚨 Nie udało się pobrać profili. Sprawdź połączenie z internetem.")
        st.stop()
    profiles = profiles_response.data
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
                result_profile = db_service.create_profile(nick, level)
                if result_profile:
                    st.success("Profil został dodany.")
                    st.rerun()
                else:
                    st.error("Nie udało się dodać profilu.")
    st.stop()
st.title("🧮 Generator Zadań")

# --- Sidebar ---
with st.sidebar:
    st.header(f"👤 {st.session_state['current_profile']['nickname']}")
    st.metric("XP", st.session_state["current_profile"]["total_xp"])
    level = st.session_state["current_profile"]["total_xp"] // 100
    progress = st.session_state["current_profile"]["total_xp"] % 100
    st.metric("Poziom", level)
    st.progress(progress / 100)
    st.caption(f"Poziom: {level} • {progress}/100 XP do następnego poziomu")
    with st.expander("❓ Jak używać?"):
        st.markdown("""
    **Krok 1:** Wybierz kategorię (Algebra, Geometria, Arytmetyka)
    
    **Krok 2:** Kliknij "Generuj Zadanie"
    
    **Krok 3:** Wpisz odpowiedź i kliknij "Sprawdź"
    
    **Krok 4:** Jeśli poprawnie → "Następne zadanie" ➡️
    
    💬 **Potrzebujesz pomocy?** Zapytaj Wirtualnego Nauczyciela poniżej!
    """)

    if st.button("Wyloguj / Zmień profil"):
        del st.session_state["current_profile"]
        st.rerun()

# --- Challenge Generator ---
st.divider()
st.header("🎯 Tryb Treningowy")

# Category Selector
category = st.selectbox("Wybierz kategorię:", ["Algebra", "Geometria", "Arytmetyka"])

# Generate Button
if st.button("Generuj Zadanie"):
    with st.status("🎲 Tworzę zadanie...", expanded=True) as status:
        st.write("🔍 Analizuję poprzednie zadania...")
        time.sleep(1)
        st.write("🧠 Dopasowuję poziom...")
        time.sleep(1)
        st.write("✨ Generuję zadanie...")

        try:
            challenge = challenge_service.generate_challenge(
                st.session_state["current_profile"]["id"], category
            )
            if challenge:
                st.session_state["current_challenge"] = challenge
                # Clear previous result if any
                if "submission_result" in st.session_state:
                    del st.session_state["submission_result"]
                status.update(label="✅ Gotowe!", state="complete")
            else:
                st.error("🔄 Generator się przeciążył. Spróbuj za chwilę!")
                status.update(label="❌ Błąd", state="error")
        except Exception as e:
            st.error(f"🔄 Generator się przeciążył. Spróbuj za chwilę!")
            status.update(label="❌ Błąd", state="error")

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
            profile_response = db_service.get_profile_by_id(
                st.session_state["current_profile"]["id"]
            )
            if profile_response and profile_response.data:
                st.session_state["current_profile"] = profile_response.data[0]
            st.rerun()
else:
    st.info("👆 Wybierz kategorię i kliknij 'Generuj Zadanie'")
# Display Result
if "submission_result" in st.session_state:
    result = st.session_state["submission_result"]
    if result["is_correct"]:
        st.success(f"{result['feedback']} (+{result['xp_earned']} XP)")
        st.balloons()
        if st.button("Następne zadanie", type="primary"):
            reset_challenge()
            st.rerun()
    else:
        st.error(f"{result['feedback']}")


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

                if "current_challenge" in st.session_state:
                    challenge_text = st.session_state["current_challenge"][
                        "problem_text"
                    ]
                else:
                    challenge_text = None

                chat_session = tutor_service.get_chat_session(
                    st.session_state.messages[:-1], challenge_context=challenge_text
                )
                response = tutor_service.send_message(chat_session, prompt)

                st.markdown(response.text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response.text}
                )
            except Exception as e:
                st.error(f"Błąd: {e}")
