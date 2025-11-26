import google.generativeai as genai
import streamlit as st
from google.api_core.exceptions import GoogleAPICallError, ResourceExhausted
import time
from tools.calculator import calculate
MAX_RETRIES = 3
def retry_with_backoff(func):
    def wrapper(*args, **kwargs):
        attempt = 0
        while attempt < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except GoogleAPICallError as e:
                delay = 2 ** attempt
                print(f"Coś mi się pomieszało w obliczeniach. Spróbuję jeszcze raz za {delay} s...")
                time.sleep(delay)
                attempt += 1
            except ResourceExhausted as e:
                delay = 2 ** attempt
                print(f"Muszę chwilę odpocząć, bo aż mi się procesor zagrzał! 🌡️ Wracam za {delay} s...")
                time.sleep(delay)
                attempt += 1
            except Exception as e:
                print(f"Ups, mała awaria! Naprawiam i wracam za {delay} s...")
                time.sleep(delay)
                attempt += 1
        raise Exception("Uff, ale dużo liczenia! Muszę wziąć głęboki oddech. Spróbuj za moment ⏳")
    return wrapper



class TutorService:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.system_instruction = """
        Jesteś PASJONATEM matematyki i super-cierpliwym MENTOREM dla uczniów (wiek 8-14 lat).
        Twoim celem jest sprawienie, by matematyka była fajna i zrozumiala.

        ZASADY KOMUNIKACJI (Tone of Voice):
        1. Bądź energiczny, używaj emoji (🚀, 📐, 🧠), ale bez przesady.
        2. Tłumacz obrazowo. Używaj analogii do: pizzy, klocków LEGO, gier (Minecraft, Roblox) lub pieniędzy.
        3. Nigdy nie oceniaj negatywnie. Zamiast "Źle", napisz: "Blisko! Ale spójrz na to z innej strony...".

        ZASADY DYDAKTYCZNE (Core Logic):
        1. Metoda Sokratesowa: Nigdy nie podawaj wyniku. Zadawaj pytania pomocnicze, które naprowadzą ucznia.
        2. Pivotowanie Tematu: Jeśli uczeń zaczyna gadać o grach/filmach, NIE ODMAWIAJ sztywno. Nawiąż krótko do tematu i użyj go do stworzenia zadania matematycznego.
        - Przykład: "Clash Royale? Super gra! A gdybyś miał eliksir na poziomie 5 i zużył 3, to ile Ci zostanie? Wracamy do liczenia!"
        3. Formatowanie: Wzory i liczby pisz wyraźnie (możesz używać LaTeX $...$ dla czytelności, ale proste równania pisz normalnie).

        BEZPIECZEŃSTWO:
        Jeśli uczeń prosi o gotowca -> Odpowiedz: "Hej, nie mogę Ci zabrać satysfakcji z rozwiązania tego samemu! Spróbujmy pierwszy krok..."
        """
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self.system_instruction,
            tools=[calculate] 
        )
    def get_chat_session(self, st_messages):
        """Przygotowuje historię w formacie Gemini i zwraca sesję czatu."""
        gemini_history = []
        for msg in st_messages:
            role = "user" if msg["role"] == "user" else "model"
            # Gemini oczekuje listy 'parts', nawet dla samego tekstu
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        return self.model.start_chat(history=gemini_history, enable_automatic_function_calling=True)
    
    @retry_with_backoff
    def send_message(self, chat_session, parts):
        return chat_session.send_message(parts, stream = True)
