-- ============================================
-- Digital Knowledge Twin Platform
-- PostgreSQL Database Schema
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  timezone VARCHAR(50) DEFAULT 'UTC',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_login_at TIMESTAMP,
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'churned')),
  subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'expert')),
  onboarding_completed BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- ============================================
-- USER PROFILES & PREFERENCES
-- ============================================

CREATE TABLE user_profiles (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  primary_domain VARCHAR(100),
  time_available_hours_per_week INTEGER,
  learning_style JSONB DEFAULT '{"video": 0.5, "reading": 0.5, "practice": 0.5}',
  budget_monthly_usd DECIMAL(10,2),
  preferred_language VARCHAR(10) DEFAULT 'en',
  location VARCHAR(100),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- GOALS
-- ============================================

CREATE TABLE goals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL CHECK (type IN ('role', 'skill', 'certification', 'project')),
  target TEXT NOT NULL,
  description TEXT,
  timeline_months INTEGER,
  target_date DATE,
  priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'achieved', 'abandoned')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  achieved_at TIMESTAMP
);

CREATE INDEX idx_goals_user_status ON goals(user_id, status);
CREATE INDEX idx_goals_created_at ON goals(created_at DESC);

-- ============================================
-- LEARNING PATHS
-- ============================================

CREATE TABLE learning_paths (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  estimated_hours INTEGER,
  estimated_weeks INTEGER,
  difficulty VARCHAR(20) CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
  status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'abandoned')),
  completion_percentage DECIMAL(5,2) DEFAULT 0.00 CHECK (completion_percentage BETWEEN 0 AND 100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_learning_paths_user_status ON learning_paths(user_id, status);
CREATE INDEX idx_learning_paths_goal ON learning_paths(goal_id);

-- ============================================
-- PATH STEPS
-- ============================================

CREATE TABLE path_steps (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  learning_path_id UUID NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
  sequence_number INTEGER NOT NULL,
  skill_id VARCHAR(100) NOT NULL, -- References Neo4j Skill node
  resource_ids JSONB NOT NULL DEFAULT '[]',
  estimated_hours INTEGER,
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'skipped')),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  UNIQUE(learning_path_id, sequence_number)
);

CREATE INDEX idx_path_steps_learning_path ON path_steps(learning_path_id, sequence_number);
CREATE INDEX idx_path_steps_status ON path_steps(status);

-- ============================================
-- SKILL PROGRESS
-- ============================================

CREATE TABLE skill_progress (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  skill_id VARCHAR(100) NOT NULL, -- References Neo4j Skill node
  proficiency_score DECIMAL(4,3) CHECK (proficiency_score BETWEEN 0 AND 1),
  proficiency_level VARCHAR(20) CHECK (proficiency_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
  confidence_score DECIMAL(4,3) CHECK (confidence_score BETWEEN 0 AND 1),
  last_practiced DATE,
  is_active BOOLEAN DEFAULT TRUE,
  evidence_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, skill_id)
);

CREATE INDEX idx_skill_progress_user ON skill_progress(user_id);
CREATE INDEX idx_skill_progress_skill ON skill_progress(skill_id);
CREATE INDEX idx_skill_progress_user_active ON skill_progress(user_id, is_active);
CREATE INDEX idx_skill_progress_updated_at ON skill_progress(updated_at DESC);

-- ============================================
-- LEARNING ACTIVITIES (Event Log)
-- ============================================

CREATE TABLE learning_activities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,
  resource_id UUID, -- References MongoDB resource
  learning_path_id UUID REFERENCES learning_paths(id) ON DELETE SET NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  session_id UUID,
  metadata JSONB DEFAULT '{}',
  time_spent_seconds INTEGER,
  device VARCHAR(20),
  location VARCHAR(100)
);

-- Partition by month for performance (example for future optimization)
CREATE INDEX idx_activities_user_timestamp ON learning_activities(user_id, timestamp DESC);
CREATE INDEX idx_activities_event_type ON learning_activities(event_type);
CREATE INDEX idx_activities_resource ON learning_activities(resource_id);
CREATE INDEX idx_activities_session ON learning_activities(session_id);

-- ============================================
-- ASSESSMENTS
-- ============================================

CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  skill_id VARCHAR(100) NOT NULL,
  title VARCHAR(255) NOT NULL,
  difficulty VARCHAR(20) CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
  question_count INTEGER,
  passing_score INTEGER CHECK (passing_score BETWEEN 0 AND 100),
  estimated_minutes INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessments_skill ON assessments(skill_id);

CREATE TABLE assessment_attempts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  assessment_id UUID NOT NULL REFERENCES assessments(id),
  score INTEGER CHECK (score BETWEEN 0 AND 100),
  passed BOOLEAN,
  time_spent_seconds INTEGER,
  answers JSONB,
  attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessment_attempts_user ON assessment_attempts(user_id, attempted_at DESC);
CREATE INDEX idx_assessment_attempts_assessment ON assessment_attempts(assessment_id);

-- ============================================
-- INTERVENTIONS
-- ============================================

CREATE TABLE interventions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  intervention_type VARCHAR(50) NOT NULL,
  risk_category VARCHAR(50),
  risk_score DECIMAL(4,3) CHECK (risk_score BETWEEN 0 AND 1),
  message_template VARCHAR(50),
  personalized_message TEXT,
  delivery_channel VARCHAR(20) CHECK (delivery_channel IN ('email', 'in_app', 'sms', 'push')),
  scheduled_for TIMESTAMP,
  sent_at TIMESTAMP,
  opened_at TIMESTAMP,
  clicked_at TIMESTAMP,
  action_taken VARCHAR(50),
  outcome VARCHAR(20) CHECK (outcome IN ('successful', 'failed', 'ignored')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interventions_user ON interventions(user_id, created_at DESC);
CREATE INDEX idx_interventions_outcome ON interventions(outcome);
CREATE INDEX idx_interventions_scheduled ON interventions(scheduled_for);

-- ============================================
-- NOTIFICATIONS
-- ============================================

CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL,
  title VARCHAR(255),
  message TEXT,
  action_url VARCHAR(500),
  priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high')),
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  read_at TIMESTAMP
);

CREATE INDEX idx_notifications_user_read ON notifications(user_id, read, created_at DESC);

-- ============================================
-- WEEKLY REPORTS
-- ============================================

CREATE TABLE weekly_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  week_start_date DATE NOT NULL,
  week_end_date DATE NOT NULL,
  hours_learned DECIMAL(6,2),
  resources_completed INTEGER,
  skills_improved JSONB DEFAULT '[]',
  path_completion_delta DECIMAL(5,2),
  streak_days INTEGER,
  achievements JSONB DEFAULT '[]',
  insights JSONB DEFAULT '[]',
  recommendations JSONB DEFAULT '[]',
  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  sent_at TIMESTAMP,
  UNIQUE(user_id, week_start_date)
);

CREATE INDEX idx_weekly_reports_user_date ON weekly_reports(user_id, week_start_date DESC);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_paths_updated_at BEFORE UPDATE ON learning_paths
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skill_progress_updated_at BEFORE UPDATE ON skill_progress
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
