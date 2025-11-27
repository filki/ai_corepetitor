"""RAG Service for curriculum topic matching using Google Gemini embeddings."""

import google.generativeai as genai
from services.db_service import DbService


class RagService:
    """Service for finding relevant curriculum topics using RAG.

    Uses Google Gemini text-embedding-004 to generate embeddings and
    performs semantic search over the curriculum database.
    """

    def __init__(self, api_key: str):
        """Initialize RAG service with Gemini API key.

        Args:
            api_key: Google API key for Gemini
        """
        genai.configure(api_key=api_key)
        self.model_name = "models/text-embedding-004"
        self.db_service = DbService()

    def find_relevant_topic(self, query: str, grade_range: str = None) -> dict | None:
        """Find most relevant curriculum topic for a query.

        Args:
            query: Search query (e.g., "dodawanie ułamków zwykłych")
            grade_range: Optional filter "IV-VI" or "VII-VIII"

        Returns:
            Dict with topic data and similarity score, or None if no match
        """
        # Generate embedding for query
        result = genai.embed_content(
            model=self.model_name,
            content=query,
            task_type="retrieval_query",  # For queries, not documents
        )
        embedding = result["embedding"]

        # Search in database
        db_results = self.db_service.match_curriculum_topics(
            query_embedding=embedding, match_count=1, filter_grade_range=grade_range
        )

        return db_results[0] if db_results else None

    def get_topic_by_id(self, topic_id: int) -> dict | None:
        """Get curriculum topic by ID.

        Args:
            topic_id: ID of the topic in curriculum_chunks table

        Returns:
            Dict with topic data or None if not found
        """
        return self.db_service.get_curriculum_topic_by_id(topic_id)
