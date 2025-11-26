import google.generativeai as genai
import streamlit as st
class TutorService:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.system_instruction = """
        Jesteś nauczycielem matematyki.
        1. Nie podawaj gotowych wyników.
        2. Naprowadzaj ucznia pytaniami metodą Sokratesową(ale nie zaznaczaj tego w odpowiedzi).
        3. Wzory pisz w LaTeX ($...$).
        4. Bądź cierpliwy i tłumaczący.
        5. W przypadku kiedy uczeń zacznie zmieniać temat, uprzejmie poinformuj go, że twoim zadaniem jest pomoc mu w nauce matematyki.
        """
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self.system_instruction
        )
    def get_chat_session(self, st_messages):
        """Przygotowuje historię w formacie Gemini i zwraca sesję czatu."""
        gemini_history = []
        for msg in st_messages:
            role = "user" if msg["role"] == "user" else "model"
            # Gemini oczekuje listy 'parts', nawet dla samego tekstu
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        return self.model.start_chat(history=gemini_history)