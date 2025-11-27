"""Challenge service module for orchestrating challenge generation and grading.

This module coordinates between the context agent, generator, grader, and database
to provide a complete challenge lifecycle from generation to submission.
"""

from services.context_agent import ContextAgent
from services.generator_service import GeneratorService
from services.grader_service import GraderService
from services.db_service import DbService


class ChallengeService:
    """Service that orchestrates the complete challenge workflow.

    Coordinates between multiple services to generate contextually appropriate
    challenges and process user submissions.

    Attributes:
        context_agent: Agent for analyzing user context and history.
        generator: Service for generating new challenges.
        grader: Service for grading user answers.
        db: Database service for persistence.
    """

    def __init__(self, api_key):
        """Initializes the challenge service with API credentials.

        Args:
            api_key (str): Google Generative AI API key.
        """
        # Importuj ISTNIEJĄCYCH agentów
        self.context_agent = ContextAgent(api_key)
        self.generator = GeneratorService(api_key)
        self.grader = GraderService(api_key)
        self.db = DbService()

    def generate_challenge(self, profile_id, category):
        """Generates a new challenge tailored to the user's profile and category.

        Analyzes user context, generates an appropriate challenge, and saves it
        to the database. Returns None if any step fails.

        Args:
            profile_id (int): The ID of the user profile.
            category (str): The challenge category (e.g., 'Algebra', 'Geometry').

        Returns:
            dict: Challenge data with 'id', 'category', 'problem_text', etc., or None on failure.
        """
        # 1. Agent A
        context = self.context_agent.analyze_context(profile_id, category)
        if context is None:
            return None
        # 2. Agent B
        problem = self.generator.generate_challenge(context, category)
        if problem is None:
            return None
        # 3. Save to DB
        db_challenge = {
            "profile_id": profile_id,
            "problem_text": problem["problem_text"],
            "correct_answer": problem["correct_answer"],
            "category": category,
            "curriculum_topic_id": context.get("curriculum_topic", {}).get("id"),
        }
        result = self.db.supabase.table("challenges").insert(db_challenge).execute()

        return result.data[0]

    def submit_answer(self, challenge_id, profile_id, user_answer):
        """Processes a user's answer submission for a challenge.

        Retrieves the challenge, grades the answer, updates XP if correct,
        and records the submission in the database.

        Args:
            challenge_id (int): The ID of the challenge being answered.
            profile_id (int): The ID of the user submitting the answer.
            user_answer (str): The user's submitted answer.

        Returns:
            dict: Grading result with 'is_correct', 'feedback', and 'xp_earned'.
        """
        challenge_response = (
            self.db.supabase.table("challenges")
            .select("*")
            .eq("id", challenge_id)
            .execute()
        )
        challenge = challenge_response.data[0]

        is_correct, feedback, xp = self.grader.grade_answer(
            challenge["problem_text"],
            challenge["correct_answer"],
            user_answer,
        )

        if is_correct:
            self.db.add_xp(profile_id, xp)

        submission_data = {
            "profile_id": profile_id,
            "challenge_id": challenge_id,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "feedback": feedback,
            "xp_earned": xp,
        }
        self.db.supabase.table("submissions").insert(submission_data).execute()

        return {"is_correct": is_correct, "feedback": feedback, "xp_earned": xp}
