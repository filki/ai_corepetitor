from google import genai
from google.genai import types  # Ważne: tu siedzą konfiguracje
from services.db_service import DbService


class RagService:
    """Service for finding relevant curriculum topics using Google Gemini embeddings (New SDK)."""

    def __init__(self, api_key: str):
        # 1. Klient z nowego SDK
        self.client = genai.Client(api_key=api_key)
        self.model_name = "text-embedding-004"
        self.db_service = DbService()

    def find_relevant_topic(self, query: str, grade_range: str = None) -> dict | None:
        """Generate embedding and match curriculum topic."""

        try:
            # 2. Generowanie embeddingu w nowym SDK
            # Zauważ: 'config' pozwala określić typ zadania (ważne dla RAG!)
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=query,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY"  # Mówimy modelowi: "to jest zapytanie do wyszukiwania"
                ),
            )

            # 3. Wyciąganie danych (Tu się zmieniło najwięcej)
            # Odpowiedź to obiekt, nie słownik. Lista embeddingów jest w atrybucie .embeddings
            # Każdy element ma atrybut .values
            embedding_vector = response.embeddings[0].values

            # 4. Semantic search in database
            db_results = self.db_service.match_curriculum_topics(
                query_embedding=embedding_vector,
                match_count=1,
                filter_grade_range=grade_range,
            )

            return db_results[0] if db_results else None

        except Exception as e:
            import traceback

            print(f"❌ Błąd generowania embeddingu (New SDK): {e}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return None

    def get_topic_by_id(self, topic_id: int) -> dict | None:
        return self.db_service.get_curriculum_topic_by_id(topic_id)
