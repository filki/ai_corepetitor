from services.context_agent import ContextAgent
from services.generator_service import GeneratorService
from services.grader_service import GraderService
from services.db_service import DbService


class ChallengeService:
    def __init__(self, api_key):
        self.context_agent = ContextAgent(api_key)
        self.generator = GeneratorService(api_key)
        self.grader = GraderService(api_key)
        self.db = DbService()

    def generate_challenge(self, profile_id, category):
        context = self.context_agent.analyze_context(profile_id, category)
        if context is None:
            return None

        problem = self.generator.generate_challenge(context, category)
        if problem is None:
            return None

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
