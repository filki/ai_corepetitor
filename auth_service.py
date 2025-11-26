import streamlit as st
class AuthService:
    @staticmethod
    def authenticate(password: str, correct_password: str) -> bool:
        if password == correct_password:
            st.session_state.authenticated = True
            return True
        return False
    @staticmethod
    def is_authenticated() -> bool:
        return st.session_state.get("authenticated", False)
    @staticmethod
    def require_auth(secret_password: str):
        """Blokuje wykonanie reszty aplikacji jeśli użytkownik nie jest zalogowany."""
        if not AuthService.is_authenticated():
            st.title("🧮 Twój prywatny korepetytor matematyki!")
            password = st.text_input("Podaj hasło dostępu:", type="password")
            if st.button("Zaloguj się"):
                if AuthService.authenticate(password, secret_password):
                    st.rerun()
                else:
                    st.error("Nieprawidłowe hasło.")
            st.stop()