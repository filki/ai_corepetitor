import google.generativeai as genai
import json
from tools.calculator import calculate


class GeneratorService:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction="""
            Jesteś drugim agentem w szeregu orkiestracji. 
            Twoim zadaniem jest wygenerowanie zadania na podstawie kontekstu.

            Kontekst zawiera informacje o profilu ucznia, historii rozwiązania zadań i kategorii.
            Przykład kontekstu:
            {
                "age_range": "10-14 lat",
                "skill_level": "początkujący",
                "recommended_difficulty": "easy",
                "context_description": "Uczeń klasy 6, ma problemu z ułamkami."
            }
            Kontekst jest podawany w formacie JSON.
            Odpowiedź zwróc jako JSON.
            Przykład odpowiedzi:
            {
                "problem_text": "?",
                "correct_answer": "?", 
                "hints": ["?"],
                "difficulty": "?"
            }
            NARZĘDZIA:
            Masz dostęp do kalkulatora (calculate).
            MUSISZ go użyć do obliczenia poprawnej odpowiedzi!

            Przykład:
            - Generujesz zadanie: "Ile to 17 × 23?"
            - Wywołaj: calculate("17 * 23") → dostaniesz "391"
            - Zapisz w "correct_answer": "391"

            Zawsze używaj kalkulatora do weryfikacji obliczeń matematycznych!
            """,
            tools=[calculate],
        )

    def generate_challenge(self, context: dict, category: str) -> dict:
        try:
            prompt = f"""
            Wygeneruj zadanie matematyczne.
            
            Kontekst ucznia:
            {json.dumps(context, indent=2)}
            
            Kategoria: {category}
            
            Uwzględnij poziom ucznia i wygeneruj odpowiednie zadanie.
            Zwróć odpowiedź w formacie JSON zgodnie z przykładem w instrukcji.
            """

            response = self.model.generate_content(prompt)
            if response.text.startswith("```json"):
                return self._handle_markdown(response.text)
            else:
                return json.loads(response.text.strip())
        except Exception as e:
            print(f"Error handling JSON response: {e}")
            return None

    def _handle_markdown(self, response: str) -> dict:
        response = response.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None
