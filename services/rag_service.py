from google import genai
from google.genai import types
from services.db_service import DbService


class RagService:
    """Service for finding relevant curriculum topics using Google Gemini embeddings (New SDK)."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = "text-embedding-004"
        self.db_service = DbService()

    def find_relevant_topic(self, query: str, grade_range: str = None) -> dict | None:
        """Generate embedding and match curriculum topic."""

        try:
            print(f"\n🔍 RAG Query: '{query}' | Grade: {grade_range}")

            # Generate embedding
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=query,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
            )

            embedding_vector = response.embeddings[0].values

            # DEBUG: Show first 5 embedding values
            print(f"🔢 Embedding (first 5): {embedding_vector[:5]}")

            # Semantic search - TEMPORARILY WITHOUT GRADE FILTER for testing
            db_results = self.db_service.match_curriculum_topics(
                query_embedding=embedding_vector,
                match_count=3,
                filter_grade_range=None,  # DISABLED temporarily - test bez filtra
            )

            # DEBUG: Show top 3
            if db_results:
                print(f"📊 Top 3 matches:")
                for i, result in enumerate(db_results[:3], 1):
                    similarity = result.get("similarity", 0)
                    print(
                        f"  {i}. {result.get('topic_name')} | Similarity: {similarity:.2%}"
                    )
            else:
                print("❌ No matches found!")

            return db_results[0] if db_results else None

        except Exception as e:
            import traceback

            print(f"❌ Błąd RAG: {e}")
            traceback.print_exc()
            return None

    def get_topic_by_id(self, topic_id: int) -> dict | None:
        return self.db_service.get_curriculum_topic_by_id(topic_id)
