/**
 * Core type definitions for the Digital Knowledge Twin Platform
 */

// ============================================
// User & Authentication
// ============================================

export interface User {
  id: string;
  email: string;
  name: string;
  timezone: string;
  created_at: Date;
  updated_at: Date;
  last_login_at?: Date;
  status: UserStatus;
  subscription_tier: SubscriptionTier;
  onboarding_completed: boolean;
}

export enum UserStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  CHURNED = 'churned',
}

export enum SubscriptionTier {
  FREE = 'free',
  PRO = 'pro',
  EXPERT = 'expert',
}

export interface UserProfile {
  user_id: string;
  primary_domain?: string;
  time_available_hours_per_week?: number;
  learning_style: LearningStyle;
  budget_monthly_usd?: number;
  preferred_language: string;
  location?: string;
  updated_at: Date;
}

export interface LearningStyle {
  video: number; // 0-1
  reading: number; // 0-1
  practice: number; // 0-1
}

// ============================================
// Skills & Knowledge
// ============================================

export interface Skill {
  id: string;
  name: string;
  canonical_name: string;
  category: string;
  domain: string;
  description?: string;
  popularity_score: number;
}

export interface UserSkill {
  user_id: string;
  skill_id: string;
  proficiency_score: number; // 0.0 - 1.0
  proficiency_level: ProficiencyLevel;
  confidence_score: number; // 0.0 - 1.0
  last_practiced?: Date;
  is_active: boolean;
  evidence_count: number;
  created_at: Date;
  updated_at: Date;
}

export enum ProficiencyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert',
}

export interface Domain {
  id: string;
  name: string;
  description?: string;
  parent_domain_id?: string;
  hierarchy_level: number;
}

// ============================================
// Goals & Learning Paths
// ============================================

export interface Goal {
  id: string;
  user_id: string;
  type: GoalType;
  target: string;
  description?: string;
  timeline_months?: number;
  target_date?: Date;
  priority: number; // 1-5
  status: GoalStatus;
  created_at: Date;
  achieved_at?: Date;
}

export enum GoalType {
  ROLE = 'role',
  SKILL = 'skill',
  CERTIFICATION = 'certification',
  PROJECT = 'project',
}

export enum GoalStatus {
  ACTIVE = 'active',
  ACHIEVED = 'achieved',
  ABANDONED = 'abandoned',
}

export interface LearningPath {
  id: string;
  user_id: string;
  goal_id?: string;
  name: string;
  description?: string;
  estimated_hours: number;
  estimated_weeks: number;
  difficulty: DifficultyLevel;
  status: PathStatus;
  completion_percentage: number;
  created_at: Date;
  started_at?: Date;
  completed_at?: Date;
  updated_at: Date;
}

export enum DifficultyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
}

export enum PathStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  ABANDONED = 'abandoned',
}

export interface PathStep {
  id: string;
  learning_path_id: string;
  sequence_number: number;
  skill_id: string;
  resource_ids: string[];
  estimated_hours: number;
  status: StepStatus;
  started_at?: Date;
  completed_at?: Date;
}

export enum StepStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  SKIPPED = 'skipped',
}

// ============================================
// Resources
// ============================================

export interface Resource {
  id: string;
  source: string;
  source_id: string;
  title: string;
  description: string;
  url: string;
  language: string;
  type: ResourceType;
  format: ResourceFormat;
  difficulty: DifficultyLevel;
  duration_hours: number;
  estimated_hours: number;
  price_usd: number;
  rating: number;
  review_count: number;
  quality_score: number;
  effectiveness_score: number;
  skills_taught: SkillTarget[];
  prerequisites: string[];
  scraped_at: Date;
  last_updated: Date;
  is_active: boolean;
}

export enum ResourceType {
  COURSE = 'course',
  BOOK = 'book',
  ARTICLE = 'article',
  VIDEO = 'video',
  TUTORIAL = 'tutorial',
  PRACTICE = 'practice',
}

export enum ResourceFormat {
  VIDEO = 'video',
  TEXT = 'text',
  INTERACTIVE = 'interactive',
  MIXED = 'mixed',
}

export interface SkillTarget {
  skill_id: string;
  proficiency_target: ProficiencyLevel;
  confidence: number;
}

// ============================================
// Learning Activities
// ============================================

export interface LearningActivity {
  id: string;
  user_id: string;
  event_type: ActivityEventType;
  resource_id?: string;
  learning_path_id?: string;
  timestamp: Date;
  session_id: string;
  metadata: Record<string, any>;
  time_spent_seconds?: number;
  device?: string;
  location?: string;
}

export enum ActivityEventType {
  RESOURCE_STARTED = 'resource_started',
  RESOURCE_IN_PROGRESS = 'resource_in_progress',
  RESOURCE_COMPLETED = 'resource_completed',
  RESOURCE_ABANDONED = 'resource_abandoned',
  ASSESSMENT_STARTED = 'assessment_started',
  ASSESSMENT_COMPLETED = 'assessment_completed',
  PATH_STARTED = 'path_started',
  PATH_STEP_COMPLETED = 'path_step_completed',
  MILESTONE_REACHED = 'milestone_reached',
}

// ============================================
// Assessments
// ============================================

export interface Assessment {
  id: string;
  skill_id: string;
  title: string;
  difficulty: DifficultyLevel;
  question_count: number;
  passing_score: number; // percentage
  estimated_minutes: number;
  created_at: Date;
}

export interface AssessmentAttempt {
  id: string;
  user_id: string;
  assessment_id: string;
  score: number; // percentage
  passed: boolean;
  time_spent_seconds: number;
  answers: Record<string, any>;
  attempted_at: Date;
}

// ============================================
// Interventions
// ============================================

export interface Intervention {
  id: string;
  user_id: string;
  intervention_type: InterventionType;
  risk_category: RiskCategory;
  risk_score: number;
  message_template: string;
  personalized_message: string;
  delivery_channel: DeliveryChannel;
  scheduled_for: Date;
  sent_at?: Date;
  opened_at?: Date;
  clicked_at?: Date;
  action_taken?: string;
  outcome?: InterventionOutcome;
  created_at: Date;
}

export enum InterventionType {
  DISENGAGEMENT = 'disengagement',
  STRUGGLE = 'struggle',
  PACING = 'pacing',
  MOTIVATION = 'motivation',
  PLATEAU = 'plateau',
  CELEBRATION = 'celebration',
}

export enum RiskCategory {
  DISENGAGEMENT_RISK = 'disengagement_risk',
  PERFORMANCE_RISK = 'performance_risk',
  PACING_RISK = 'pacing_risk',
  MOTIVATION_RISK = 'motivation_risk',
  PLATEAU_RISK = 'plateau_risk',
}

export enum DeliveryChannel {
  EMAIL = 'email',
  IN_APP = 'in_app',
  SMS = 'sms',
  PUSH = 'push',
}

export enum InterventionOutcome {
  SUCCESSFUL = 'successful',
  FAILED = 'failed',
  IGNORED = 'ignored',
}

// ============================================
// Notifications
// ============================================

export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  action_url?: string;
  priority: NotificationPriority;
  read: boolean;
  created_at: Date;
  read_at?: Date;
}

export enum NotificationType {
  MILESTONE = 'milestone',
  NEW_CONTENT = 'new_content',
  REMINDER = 'reminder',
  ACHIEVEMENT = 'achievement',
  INTERVENTION = 'intervention',
}

export enum NotificationPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
}

// ============================================
// API Request/Response Types
// ============================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  meta: {
    timestamp: string;
    version: string;
    request_id?: string;
  };
}

export interface PaginationParams {
  page: number;
  limit: number;
  sort?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

// ============================================
// Service Types
// ============================================

export interface ExtractionResult {
  skills: Array<{
    skill_id: string;
    name: string;
    proficiency_score: number;
    confidence: number;
    evidence: string[];
  }>;
  experiences: Array<{
    title: string;
    organization: string;
    start_date: Date;
    end_date?: Date;
    description: string;
    skills_used: string[];
  }>;
}

export interface LearningPathGenerationParams {
  user_id: string;
  goal_id: string;
  preferences?: {
    time_available_hours_per_week?: number;
    budget_constraint?: number;
    preferred_formats?: ResourceFormat[];
    pace?: 'slow' | 'moderate' | 'fast';
  };
}

export interface SkillGap {
  skill_id: string;
  skill_name: string;
  current_proficiency: number;
  target_proficiency: number;
  gap_score: number;
  priority: number;
}
