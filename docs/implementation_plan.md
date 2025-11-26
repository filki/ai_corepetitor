# Training Grounds & Bug Fixes Implementation Plan

Brief overview: Fix critical bugs in existing code and implement the Training Grounds feature - a simplified profile-based challenge system for a single family (max 5 members). This includes Supabase integration, challenge generation, grading system, and UI updates.

## User Review Required

> [!IMPORTANT]
> **Supabase Configuration**: You need to provide Supabase credentials in Streamlit secrets:
> - `SUPABASE_URL` - Your Supabase project URL
> - `SUPABASE_KEY` - Your Supabase anon/public key
>
> These should be added to `.streamlit/secrets.toml` (local) or Streamlit Cloud secrets (production).

> [!WARNING]
> **Breaking Change**: The app will now require profiles to be selected before interacting with challenges. The chat-based tutor will remain accessible, but challenge features require profile selection.

## Proposed Changes

### Core Services

#### [MODIFY] [db_service.py](file:///c:/Users/ruder/Desktop/ai_corepetiror/services/db_service.py)

**Critical Bug Fix**: Missing import for Supabase client

- Add import: `from supabase import create_client, Client`
- Fix `create_client()` call to accept URL and key from Streamlit secrets
- Fix `add_xp()` method logic - currently has incorrect parameter usage

**Changes**:
- Import Supabase properly
- Initialize client with credentials from `st.secrets`
- Correct the XP addition logic to fetch current XP, add to it, and update

---

#### [NEW] [challenge_service.py](file:///c:/Users/ruder/Desktop/ai_corepetiror/services/challenge_service.py)

Service for generating and managing math challenges using Gemini AI.

**Methods**:
- `generate_problem(category: str, level: str)` - Uses Gemini to create math problems tailored to education level
- `save_challenge(problem_dict: dict)` - Saves generated challenge to Supabase
- `get_history(profile_id: str, limit: int)` - Retrieves submission history for a profile

**Design**: Single-agent approach using structured output from Gemini to ensure consistent problem format (problem_text, correct_answer, hints).

---

#### [NEW] [grader_service.py](file:///c:/Users/ruder/Desktop/ai_corepetiror/services/grader_service.py)

Service for grading user answers with fuzzy matching.

**Methods**:
- `grade_answer(correct: str, user_answer: str)` - Returns `(is_correct: bool, feedback: str, xp_earned: int)`
- Implements fuzzy matching for fractions (e.g., `0.5` == `1/2`)
- Normalizes whitespace, case, and common mathematical notations

**XP Calculation**:
- Correct answer: 10 XP
- Incorrect answer: 0 XP

---

### User Interface

#### [MODIFY] [app.py](file:///c:/Users/ruder/Desktop/ai_corepetiror/app.py)

Add profile selection and challenge generation UI while maintaining existing chat functionality.

**Sidebar Additions**:
- Profile selector dropdown (loads from Supabase)
- "Dodaj nowy profil" button
- Display current profile's XP

**New Page Section** (below chat):
- Category dropdown for challenge types (Algebra, Geometry, Arithmetics)
- "Generuj Zadanie" button
- Challenge display area
- Answer input and submit button
- Recent history table (last 5 submissions)

**Session State**:
- Add `current_profile` to track selected profile
- Add `current_challenge` for active challenge
- Keep existing `messages` for chat

---

## Verification Plan

### Automated Tests

Currently, there are no existing test files in the project. We will create manual test scripts to verify core functionality:

**Test 1: Database Connection**
```python
# test_db_connection.py
# Run: python -m streamlit run test_db_connection.py
import streamlit as st
from services.db_service import DbService

db = DbService()
profiles = db.get_all_profiles()
st.write(f"✅ Connected! Found {len(profiles.data)} profiles")
```

**Command**: `streamlit run test_db_connection.py` (after creating the file)

**Test 2: Challenge Generation**
```python
# test_challenge_gen.py
# Run: python test_challenge_gen.py
from services.challenge_service import ChallengeService
import os

api_key = os.getenv("GOOGLE_API_KEY")  # Set this in environment
service = ChallengeService(api_key)
problem = service.generate_problem("algebra", "podstawowka_4_8")
print(f"✅ Generated: {problem['problem_text']}")
assert problem['correct_answer'] is not None
```

**Command**: `python test_challenge_gen.py` (requires `GOOGLE_API_KEY` env var)

**Test 3: Grader Fuzzy Matching**
```python
# test_grader.py
# Run: python test_grader.py
from services.grader_service import GraderService

grader = GraderService()
test_cases = [
    ("4", "4", True),
    ("0.5", "1/2", True),
    ("10", "eleven", False),
    ("2.5", "2,5", True),  # Handle Polish decimal notation
    ("PI", "pi", True),
]

for correct, user, expected in test_cases:
    is_correct, _, _ = grader.grade_answer(correct, user)
    assert is_correct == expected, f"Failed: {correct} vs {user}"
print("✅ All 5 test cases passed!")
```

**Command**: `python test_grader.py`

### Manual Verification

> [!NOTE]
> **User action required**: After implementation, please test the following flow:

1. **Database Setup** (5 minutes)
   - Open your Supabase project dashboard
   - Go to SQL Editor
   - Copy contents of `docs/supabase_schema.sql`
   - Execute the SQL
   - Verify in Table Editor: `profiles`, `challenges`, `submissions` tables exist
   - Confirm test data: 2 profiles (Ania, Bartek) and 1 challenge present

2. **App Configuration** (2 minutes)
   - Add Supabase credentials to `.streamlit/secrets.toml`:
     ```toml
     SUPABASE_URL = "https://your-project.supabase.co"
     SUPABASE_KEY = "your-anon-key"
     ```
   - Restart Streamlit app

3. **Profile Selection** (3 minutes)
   - Open app in browser
   - In sidebar, verify dropdown shows "Ania" and "Bartek"
   - Select "Ania" → should show XP: 0
   - Click "Dodaj nowy profil" → enter name "Test" + level → submit
   - Verify "Test" appears in dropdown

4. **Challenge Flow** (5 minutes)
   - Select profile "Ania"
   - Choose category "Algebra"
   - Click "Generuj Zadanie"
   - Wait ~10-20s for problem generation
   - Verify problem text displays
   - Enter correct answer → click Submit
   - Verify: ✅ icon, "Brawo!" message, XP +10 shown
   - Enter wrong answer on new challenge → verify ❌ icon, feedback shown

5. **History Display** (2 minutes)
   - After 3+ submissions, scroll to "Historia" section
   - Verify table shows recent 5 submissions with:
     - ✅/❌ icons
     - Problem text (truncated)
     - XP earned
     - Timestamp

**Expected Success**: All steps complete without errors, app remains responsive, profile XP increments correctly.

If any step fails, please share:
- Error messages from Streamlit terminal
- Browser console errors (F12)
- Screenshot of the issue
