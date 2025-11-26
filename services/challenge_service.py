from services.context_agent import ContextAgent
from services.generator_service import GeneratorService
from services.grader_service import GraderService
from services.db_service import DbService

class ChallengeService:
    def __init__(self, api_key):
        # Importuj ISTNIEJĄCYCH agentów
        self.context_agent = ContextAgent(api_key)
        self.generator = GeneratorService(api_key)
        self.grader = GraderService()
        self.db = DbService()
        
    def generate_challenge(self, profile_id, category):
        # 1. Agent A
        context = self.context_agent.analyze_context(profile_id, category)
        # 2. Agent B
        problem = self.generator.generate_challenge(context, category)
        # 3. Save to DB
        challenge_data = {
            "category": category,
            "difficulty": problem.get("difficulty"),
            "problem_text": problem.get("problem_text"),
            "correct_answer": problem.get("correct_answer"),
            "hints": problem.get("hints")
        }
        result = self.db.supabase.table("challenges").insert(challenge_data).execute()
        
        return result.data[0]
    def submit_answer(self, challenge_id, profile_id, user_answer):
      
        challenge_response = self.db.supabase.table("challenges").select("*").eq("id", challenge_id).execute()
        challenge = challenge_response.data[0]
        
 
        is_correct, feedback, xp = self.grader.grade_answer(
            challenge["correct_answer"], 
            user_answer
        )
        
       
        if is_correct:
            self.db.add_xp(profile_id, xp)
        
       
        submission_data = {
            "profile_id": profile_id,
            "challenge_id": challenge_id,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "feedback": feedback,
            "xp_earned": xp
        }
        self.db.supabase.table("submissions").insert(submission_data).execute()
        
        return {
            "is_correct": is_correct,
            "feedback": feedback,
            "xp_earned": xp
        }