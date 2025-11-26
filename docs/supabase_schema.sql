-- ============================================
-- AI Corepetitor - Training Grounds Database
-- SIMPLIFIED for Single Family (no RLS)
-- ============================================

-- 1. PROFILES TABLE
-- Stores family member profiles (max ~5)
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nickname TEXT NOT NULL UNIQUE,
  education_level TEXT NOT NULL CHECK (
    education_level IN ('podstawowka_1_3', 'podstawowka_4_8', 'szkola_srednia', 'studia')
  ),
  total_xp INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX idx_profiles_nickname ON profiles(nickname);

-- 2. CHALLENGES TABLE
-- Stores generated math problems
CREATE TABLE IF NOT EXISTS challenges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category TEXT NOT NULL,
  difficulty TEXT CHECK (difficulty IN ('easy', 'medium', 'hard')),
  problem_text TEXT NOT NULL,
  correct_answer TEXT,
  hints JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index for filtering by category
CREATE INDEX idx_challenges_category ON challenges(category);

-- 3. SUBMISSIONS TABLE
-- Tracks who solved what and when
CREATE TABLE IF NOT EXISTS submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  challenge_id UUID REFERENCES challenges(id) ON DELETE CASCADE,
  user_answer TEXT,
  is_correct BOOLEAN,
  feedback TEXT,
  xp_earned INTEGER DEFAULT 0,
  submitted_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for history queries
CREATE INDEX idx_submissions_profile ON submissions(profile_id, submitted_at DESC);
CREATE INDEX idx_submissions_challenge ON submissions(challenge_id);

-- ============================================
-- TEST DATA (optional)
-- ============================================

-- Add sample profiles
INSERT INTO profiles (nickname, education_level) VALUES
  ('Ania', 'podstawowka_4_8'),
  ('Bartek', 'szkola_srednia')
ON CONFLICT (nickname) DO NOTHING;

-- Add sample challenge
INSERT INTO challenges (category, difficulty, problem_text, correct_answer) VALUES
  ('algebra', 'easy', 'Ile wynosi 2 + 2?', '4')
ON CONFLICT DO NOTHING;

-- ============================================
-- Verification Query
-- ============================================
-- Run this to confirm tables exist:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
