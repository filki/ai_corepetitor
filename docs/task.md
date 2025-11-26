# AI Korepetitor - Implementation Tasks

## 🎯 Phase 1: Image Upload Feature (Partial)
- [x] Basic file uploader in UI
- [x] Photo converter implementation
- [x] Utils for image replacement
- [ ] Fix `photo_converter.py` issues (if any)
- [ ] Verify multimodal integration with Gemini

## 🏗️ Phase 2: Training Grounds - Simplified (Single Family)
**Context**: One family (max 5 profiles), no complex auth  
**Branch**: `feature/supabase` ✅

### Day 1: Database Setup ✅ COMPLETED!
- [x] 1.1 Create Tables in Supabase SQL Editor ✅
  - [x] Run SQL for `profiles` (no RLS)
  - [x] Run SQL for `challenges`
  - [x] Run SQL for `submissions`
  - [x] AC: Tables visible in Table Editor
- [x] 1.2 Seed Test Data ✅
  - [x] 2 test profiles exist (Ania, Bartek)
  - [x] Test challenge exists
  - [x] AC: Can query data via SQL Editor

### Day 2-3: Multi-Agent Services 🤖
- [x] 2.1 Fix `db_service.py` ✅ COMPLETED!
  - [x] All bugs fixed and working
- [x] 2.2 Agent A: Context Analyzer ✅ COMPLETED!
  - [x] Create `services/context_agent.py`
  - [x] `analyze_context(profile, category)` - returns rich context
  - [x] Load submission history for personalization
  - [x] Parse and build prompt from profile + submissions
  - [x] Parse JSON response from Gemini (handles markdown!)
  - [x] Error handling and validation
  - [x] AC: Returns structured context JSON
- [x] 2.3 Agent B: Problem Generator ✅ COMPLETED!
  - [x] Create `services/generator_service.py`
  - [x] `generate_problem(context, category)` - uses Agent A context
  - [x] Prompt engineering for age-appropriate problems
  - [x] AC: Generates problem in <20s with valid JSON
- [x] 2.4 Simple Grader ✅ COMPLETED! (MVP - bez AI)
  - [x] Create `services/grader_service.py`
  - [x] Basic fuzzy matching (lowercase, decimals, numeric)
  - [x] Friendly feedback in Polish
  - [x] XP calculation (10 for correct, 0 for wrong)
- [ ] 2.5 Agent D: Hint Assistant (SKIPPED FOR MVP) 🔜
  - [ ] Will be added after MVP
- [x] 2.6 Orchestrator: Challenge Service ✅ COMPLETED!
  - [x] Create `services/challenge_service.py`
  - [x] `generate_challenge()` - coordinates Agent A + B
  - [x] `submit_answer()` - coordinates Grader + DB
  - [x] Saves to Supabase (challenges, submissions)
  - [x] AC: Full flow works end-to-end

### Day 4-5: UI
- [ ] 3.1 Profile Selector
  - [ ] Sidebar: Dropdown "Kto dzisiaj?"
  - [ ] Load profiles from Supabase
  - [ ] Button: "Dodaj nowy profil"
  - [ ] Store selected profile in `st.session_state`
  - [ ] AC: Can switch between profiles
- [ ] 3.2 Challenge Generator
  - [ ] Category dropdown
  - [ ] "Generuj Zadanie" button
  - [ ] Display problem + answer input
  - [ ] Submit & grade
  - [ ] AC: Full flow works
- [ ] 3.3 Simple History
  - [ ] Show last 5 submissions
  - [ ] Display: ✅ or ❌, XP earned
  - [ ] AC: History updates after submission

### Day 6-7: Polish & Deploy
- [ ] 4.1 Error Handling
  - [ ] Supabase offline fallback
  - [ ] Gemini rate limit message
  - [ ] AC: No crashes
- [ ] 4.2 Deploy
  - [ ] Add secrets to Streamlit Cloud
  - [ ] Test live
  - [ ] AC: Works in production

## 🚫 NOT Included (Too Complex for 1 Family)
- ~~Authentication / login~~
- ~~Row Level Security~~
- ~~Leaderboards~~
- ~~Badges/achievements~~
- ~~Photo upload grading~~

## ✅ Success Criteria
5 family members can use app, generate & solve challenges
