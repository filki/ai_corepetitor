from google.genai import Client, types
from services.db_service import DbService
from services.rag_service import RagService
import json


class ContextAgent:
    def __init__(self, api_key: str):
        self.client = Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

        self.db_service = DbService()
        self.rag_service = RagService(api_key)

    def analyze_context(self, profile_id: int, category: str) -> dict:
        profile = self.db_service.get_profile_by_id(profile_id)
        submission = self.db_service.get_submissions(profile_id)

        profile_data = profile.data[0] if profile.data else {}
        submissions_data = submission.data if submission.data else []

        prompt = f"""
        Profil ucznia:
        - Nickname: {profile_data.get("nickname")}
        - Poziom: {profile_data.get("education_level")}
        - Total XP: {profile_data.get("total_xp", 0)}

        Historia ({len(submissions_data)} zadań rozwiązanych).

        Kategoria: {category}
        
        Przeanalizuj dane i zwróć kontekst w formacie JSON zgodnie z systemową instrukcją.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="""
Jesteś Analitykiem Danych Edukacyjnych. Twoim zadaniem jest przetworzenie surowych danych o historii ucznia na ustrukturyzowane wytyczne dla Agenta Generującego Zadania.

DANE WEJŚCIOWE:
Otrzymasz profil ucznia, jego XP oraz listę ostatnich prób (wraz z informacją, czy były udane).

TWOJE ZADANIE:
1. Przeanalizuj "win rate" (stosunek sukcesów do porażek) w ostatnich 5-10 zadaniach.
2. Określ, czy uczeń jest w fazie nauki (potrzebuje wsparcia) czy w fazie "flow" (potrzebuje wyzwania).
3. Zidentyfikuj, jakie typy zadań sprawiały problem (na podstawie treści nieudanych prób).

FORMAT ODPOWIEDZI (JSON):
Zwróć TYLKO obiekt JSON o następującej strukturze:

{
"_reasoning": "Krótka analiza trendu: np. Uczeń rozwiązał 3 ostatnie zadania bezbłędnie, czas podnieść poprzeczkę.",
"student_profile_summary": {
    "skill_level": "beginner" | "intermediate" | "advanced",
    "current_streak": "int (liczba sukcesów z rzędu)"
},
"generation_directives": {
    "difficulty": "easy" | "medium" | "hard",
    "topic_focus": "Na czym generator ma się skupić (np. ułamki dziesiętne)",
    "constraints": "Czego unikać (np. unikaj dużych liczb, unikaj dzielenia z resztą)",
    "narrative_style": "formalny" | "przygoda" | "sportowy" (dobierz pod profil)"
}
}

PAMIĘTAJ:
Twoim celem jest utrzymanie ucznia w strefie najbliższego rozwoju (Vygotsky Zone). Nie dawaj zadań zbyt łatwych (nuda) ani zbyt trudnych (frustracja).
""",
                    response_mime_type="application/json",  # ← KLUCZOWE!
                ),
            )

            context = json.loads(response.text)

            # Add curriculum topic using RAG
            if context:
                grade_range = self._get_grade_range(profile_data.get("education_level"))
                curriculum_topic = self.rag_service.find_relevant_topic(
                    query=category,  # Pure query bez szumu!
                    grade_range=grade_range,
                )
                context["curriculum_topic"] = curriculum_topic

            return context

        except Exception as e:
            print(f"Error in Context Agent: {e}")
            return None

    def _get_grade_range(self, education_level: str) -> str:
        """Konwertuje education_level na grade_range."""
        print(f"🎓 DEBUG education_level: '{education_level}'")

        if not education_level:
            return "IV-VI"  # Default fallback

        # Obsługa różnych formatów
        if any(
            x in str(education_level).lower() for x in ["1", "2", "3", "podstawówka"]
        ):
            return "IV-VI"  # Klasy 1-3 -> przypisz IV-VI (łatwiejsze)
        if any(c in str(education_level) for c in ["4", "5", "6"]):
            return "IV-VI"
        elif any(c in str(education_level) for c in ["7", "8"]):
            return "VII-VIII"

        return "IV-VI"  # Default fallback
