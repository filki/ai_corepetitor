"""
Simple Grader Service for MVP
Validates user answers with basic fuzzy matching
"""

class GraderService:
    """Service for grading mathematical answers"""
    
    XP_CORRECT = 10
    XP_INCORRECT = 0
    
    @staticmethod
    def normalize_answer(answer: str) -> str:
        """
        Normalize an answer for comparison.
        - Convert to lowercase
        - Remove whitespace
        - Replace Polish decimal comma with period
        """
        if not answer:
            return ""
        
        normalized = answer.lower().strip()
        # Remove all whitespace
        normalized = normalized.replace(" ", "")
        # Replace Polish decimal notation (comma) with period
        normalized = normalized.replace(',', '.')
        
        return normalized
    
    @staticmethod
    def answers_match(correct: str, user_answer: str) -> bool:
        """
        Check if two answers match with basic normalization.
        """
        correct_norm = GraderService.normalize_answer(correct)
        user_norm = GraderService.normalize_answer(user_answer)
        
        # Direct string match after normalization
        if correct_norm == user_norm:
            return True
        
        # Try numeric comparison for floats
        try:
            correct_num = float(correct_norm)
            user_num = float(user_norm)
            # Use small epsilon for floating point comparison
            return abs(correct_num - user_num) < 1e-9
        except (ValueError, TypeError):
            pass
        
        return False
    
    @staticmethod
    def grade_answer(correct: str, user_answer: str) -> tuple[bool, str, int]:
        """
        Grade a user's answer.
        
        Args:
            correct: The correct answer
            user_answer: The user's submitted answer
        
        Returns:
            Tuple of (is_correct: bool, feedback: str, xp_earned: int)
        """
        if not user_answer or not user_answer.strip():
            return (False, "Musisz wpisać odpowiedź! 🤔", GraderService.XP_INCORRECT)
        
        is_correct = GraderService.answers_match(correct, user_answer)
        
        if is_correct:
            feedback = "🎉 Brawo! Świetna robota! +10 XP"
            xp = GraderService.XP_CORRECT
        else:
            feedback = f"Nie tym razem... Poprawna odpowiedź to: {correct}. Spróbuj następnego! 💪"
            xp = GraderService.XP_INCORRECT
        
        return (is_correct, feedback, xp)
