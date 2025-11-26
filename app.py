import streamlit as st
import google.generativeai as genai
from photo_converter import process_image 
# 1. Konfiguracja Strony


st.set_page_config(page_title="Twój Korepetytor Matmy", page_icon="🧮")
st.title("🧮 Gemini Math Tutor")

# 2. BRAMKARZ (Logowanie)
if "authenticated" not in st.session_state:
    password = st.text_input("Podaj hasło dostępu:", type="password")
    if st.button("Zaloguj"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Nieprawidłowe hasło.")
    st.stop()

# --- Aplikacja właściwa ---

# 3. Konfiguracja Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Instrukcja systemowa (Gemini obsługuje to natywnie w konfiguracji modelu)
system_instruction = """
Jesteś nauczycielem matematyki.
1. Nie podawaj gotowych wyników.
2. Naprowadzaj ucznia pytaniami.
3. Wzory pisz w LaTeX ($...$).
4. Bądź cierpliwy i tłumaczący.
"""

# Wybór modelu - Flash jest szybki i oszczędny
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=system_instruction
)

# 4. Pamięć Konwersacji
# Streamlit trzyma historię do wyświetlania
if "messages" not in st.session_state:
    st.session_state.messages = []

# Gemini wymaga specyficznego formatu historii (history list for chat session)
# Przekształcamy format Streamlita na format Gemini
gemini_history = []
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "model"
    gemini_history.append({"role": role, "parts": [msg["content"]]})


# --- SIDEBAR: Obsługa Zdjęć ---
with st.sidebar:
    st.header("📸 Materiały")
    uploaded_file = st.file_uploader("Wgraj zdjęcie zadania", type=['png', 'jpg', 'jpeg'])
    
    current_image = None
    if uploaded_file:
        current_image = process_image(uploaded_file)
        st.image(current_image, caption="Podgląd", use_column_width=True)
# 5. Inicjalizacja czatu z historią
chat_session = model.start_chat(history=gemini_history)

# Wyświetlanie historii w UI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Obsługa wejścia
if prompt := st.chat_input("Z czym masz problem?"):
    # Dodajemy wiadomość użytkownika do historii UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # Generowanie odpowiedzi
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Przygotowanie treści wiadomości
            # Jeśli mamy zdjęcie, wysyłamy je razem z pytaniem
            message_parts = [prompt]
            if current_image:
                message_parts.append(current_image)
            
            # Streamowanie odpowiedzi z Gemini
            response = chat_session.send_message(message_parts, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Zapisz odpowiedź modelu do historii
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Wystąpił błąd API: {e}")