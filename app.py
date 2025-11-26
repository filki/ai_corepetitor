import streamlit as st
from services.auth_service import AuthService
from services.challenge_service import ChallengeService
from services.db_service import DbService

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

challenge_service = get_challenge_service(st.secrets["GOOGLE_API_KEY"])
db_service = get_db_service()

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
st.write(f"Witaj, {st.session_state['current_profile']['nickname']}!")

