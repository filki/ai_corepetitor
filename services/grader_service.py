"""
Simple Grader Service for MVP
Validates user answers with basic fuzzy matching
"""

import google.generativeai as genai
import json
from tools.calculator import calculate


class GraderService:
    """Service for grading mathematical answers"""

    XP_CORRECT = 10
    XP_INCORRECT = 0

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction="""
            Jesteś wyrozumiałym mentorem matematycznym. Twoim zadaniem jest ocena odpowiedzi ucznia na podstawie kontekstu zadania, a nie tylko ścisłego dopasowania znaków.

            TWOJE CELE:
            1. Zidentyfikuj intencję ucznia i wyekstrahuj wynik z jego wypowiedzi.
            2. Zignoruj szum komunikacyjny (literówki, błędy ortograficzne, słowa poboczne).
            3. Oceń poprawność matematyczną wyekstrahowanego wyniku.
            4. Zwróć wynik w ściśle określonym formacie JSON.

            ALGORYTM OCENY (Thinking Process):
            Krok 1: Przeanalizuj "Poprawny wynik" (Ground Truth).
            Krok 2: Przeszukaj "Odpowiedź ucznia". Szukaj liczb lub wyrażeń matematycznych ukrytych w tekście (np. w "makja 9 batonikow" kluczowa jest liczba "9").
            Krok 3: Zastosuj "Fuzzy Matching" (Dopasowanie rozmyte):
            - Ignoruj literówki (np. "szesc" = 6, "cztery" = 4).
            - Ignoruj tekst otaczający (np. "wydaje mi sie ze 7" -> 7).
            - Akceptuj zamienne formaty (np. 0.5 = 1/2 = 50%).
            Krok 4: Porównaj wyekstrahowaną wartość z poprawnym wynikiem.

            ZASADY FEEDBACKU (w polu "feedback"):
            - Język: Polski.
            - Jeśli POPRAWNA: Bądź entuzjastyczny, użyj emoji (🎉, 🚀, ⭐). Pochwal myślenie.
            - Jeśli BŁĘDNA: Bądź wspierający. Nie podawaj od razu poprawnego wyniku. Daj delikatną wskazówkę, która naprowadzi ucznia na błąd (np. "Jesteś blisko, ale sprawdź jeszcze raz dodawanie").

            FORMAT ODPOWIEDZI:
            Musisz zwrócić TYLKO obiekt JSON. Nie dodawaj żadnego tekstu przed ani po JSONie.

            {
            "_thinking_process": "Opisz tutaj krótko swój tok rozumowania: co uczeń napisał, jaką liczbę wyciągnąłeś z tekstu i dlaczego pasuje/nie pasuje.",
            "is_correct": true,  // lub false
            "feedback": "Twoja wiadomość dla ucznia",
            "xp_earned": 10      // 10 za poprawną, 0 za błędną
            }
            """,
            tools=[
                {
                    "name": "calculator",
                    "description": "Oblicza matematyczne wyrażenia",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Wyrażenie matematyczne do obliczenia",
                            }
                        },
                        "required": ["expression"],
                    },
                }
            ],
        )

    def grade_answer(self, problem_text: str, correct_answer: str, user_answer: str):
        if not user_answer or not user_answer.strip():
            return (False, "Musisz wpisać odpowiedź! 🤔", self.XP_INCORRECT)

        prompt = f"""
        ZADANIE: {problem_text}
        POPRAWNA: {correct_answer}
        UCZEŃ: {user_answer}
        
        Oceń i zwróć JSON.
        """

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            return (result["is_correct"], result["feedback"], result["xp_earned"])
        except Exception as e:
            print(f"Grader error: {e}")
            return (False, "Ups, nie mogę ocenić. Spróbuj ponownie! ⏳", 0)

    def _parse_response(self, text: str):
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        result = json.loads(cleaned)

        if "is_correct" not in result:
            raise ValueError("Missing is_correct")

        return result
