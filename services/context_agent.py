import google.generativeai as genai
from services.db_service import DbService
import json
class ContextAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction="""
            Jesteś pierwszymn agentem w szeregu orkiestracji. 
            Twoim zadaniem jest analiza profilu studenta i zwrócenie kontekstu do drugiego agenta.
            Drugi agent musi wygenerować na podstawie kontekstu zadanie dla studenta.
            Odpowiedź zwróc jako słownik, a konkretniej format JSON.

            Przykład odpowiedzi:
            {
                "age_range": "10-14 lat",
                "skill_level": "początkujący",
                "recommended_difficulty": "easy",
                "context_description": "Uczeń klasy 6, ma problemu z ułamkami."
            }
            """
        )
        self.db_service = DbService()
    
    def analyze_context(self,profile_id: int, category: str) -> dict:
       
        profile = self.db_service.get_profile_by_id(profile_id)
        submission = self.db_service.get_submissions(profile_id)
        profile_data = profile.data[0] if profile.data else {}
        submissions_data = submission.data if submission.data else []


        prompt = f"""
        Profil ucznia:
        - Nickname: {profile_data.get('nickname')}
        - Poziom: {profile_data.get('education_level')}
        - Total XP: {profile_data.get('total_xp', 0)}

        Historia ({len(submissions_data)} zadań rozwiązanych)

        Kategoria: {category}

        Zadanie: Przeanalizuj dane i zwróć kontekst w formacie JSON...
        """
        try:
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

    def _validate_context(self, context: dict) -> bool:
        required = ["age_range", "skill_level", "recommended_difficulty", "context_description"]
        return all(key in context for key in required)