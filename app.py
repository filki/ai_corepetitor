import streamlit as st
from photo_converter import process_image
from auth_service import AuthService
from tutor_service import TutorService
from helpers.utils import replace_images_in_text
    
# site configuration
st.set_page_config(page_title="Twój Prywatny Nauczyciel Matmy", page_icon="🧮")

# authentications
AuthService.require_auth(st.secrets["APP_PASSWORD"])

st.title("🧮 Twój Prywatny Nauczyciel Matmy")

# returns tutor service instance
@st.cache_resource
def get_tutor_service(api_key):
    return TutorService(api_key=api_key)

# Force cache reload if secret changes
tutor_service = get_tutor_service(st.secrets["GOOGLE_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("📸 Materiały")
    uploaded_file = st.file_uploader("Wgraj zdjęcie zadania", type=['png', 'jpg', 'jpeg'])
    
    current_image = None
    if uploaded_file:
        current_image = process_image(uploaded_file)
        st.image(current_image, caption="Podgląd", use_column_width=True)

    st.divider()
    debug_mode = st.checkbox("🐞 Tryb Developerski", key="debug_mode")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(replace_images_in_text(msg["content"]))

if prompt := st.chat_input("Z czym masz problem?"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:

            chat_session = tutor_service.get_chat_session(st.session_state.messages[:-1]) 
            
    
            message_parts = [prompt]
            if current_image:
                message_parts.append(current_image)
            response = tutor_service.send_message(chat_session, message_parts)
            
            # Streaming is disabled due to function calling support
            if response.text:
                full_response = response.text
                message_placeholder.markdown(replace_images_in_text(full_response))
            
            # Zapisz odpowiedź
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Wystąpił błąd: {e}")