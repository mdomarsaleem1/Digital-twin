/**
 * Input validation schemas using Zod
 */

import { z } from 'zod';

// User schemas
export const CreateUserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  name: z.string().min(2).max(255),
  timezone: z.string().optional(),
});

export const UpdateUserProfileSchema = z.object({
  primary_domain: z.string().optional(),
  time_available_hours_per_week: z.number().int().min(1).max(168).optional(),
  learning_style: z
    .object({
      video: z.number().min(0).max(1),
      reading: z.number().min(0).max(1),
      practice: z.number().min(0).max(1),
    })
    .optional(),
  budget_monthly_usd: z.number().min(0).optional(),
  preferred_language: z.string().length(2).optional(),
  location: z.string().optional(),
});

// Goal schemas
export const CreateGoalSchema = z.object({
  type: z.enum(['role', 'skill', 'certification', 'project']),
  target: z.string().min(3).max(500),
  description: z.string().optional(),
  timeline_months: z.number().int().min(1).max(60).optional(),
  target_date: z.string().datetime().optional(),
  priority: z.number().int().min(1).max(5).optional(),
});

export const UpdateGoalSchema = CreateGoalSchema.partial();

// Learning path schemas
export const GeneratePathSchema = z.object({
  goal_id: z.string().uuid(),
  preferences: z
    .object({
      time_available_hours_per_week: z.number().int().min(1).max(168).optional(),
      budget_constraint: z.number().min(0).optional(),
      preferred_formats: z.array(z.enum(['video', 'text', 'interactive', 'mixed'])).optional(),
      pace: z.enum(['slow', 'moderate', 'fast']).optional(),
    })
    .optional(),
});

// Resource schemas
export const ResourceFilterSchema = z.object({
  skill_id: z.string().optional(),
  type: z.enum(['course', 'book', 'article', 'video', 'tutorial', 'practice']).optional(),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']).optional(),
  format: z.enum(['video', 'text', 'interactive', 'mixed']).optional(),
  max_price: z.number().min(0).optional(),
  min_rating: z.number().min(0).max(5).optional(),
  page: z.number().int().min(1).default(1),
  limit: z.number().int().min(1).max(100).default(20),
  sort: z.string().optional(),
});

// Activity schemas
export const RecordActivitySchema = z.object({
  event_type: z.string(),
  resource_id: z.string().uuid().optional(),
  learning_path_id: z.string().uuid().optional(),
  time_spent_seconds: z.number().int().min(0).optional(),
  metadata: z.record(z.any()).optional(),
});

// Assessment schemas
export const SubmitAssessmentSchema = z.object({
  assessment_id: z.string().uuid(),
  answers: z.record(z.any()),
  time_spent_seconds: z.number().int().min(0),
});

// Pagination schema
export const PaginationSchema = z.object({
  page: z.number().int().min(1).default(1),
  limit: z.number().int().min(1).max(100).default(20),
  sort: z.string().optional(),
});

/**
 * Validate data against a schema
 */
export function validate<T>(schema: z.ZodSchema<T>, data: unknown): T {
  return schema.parse(data);
}

/**
 * Safe validate - returns result object instead of throwing
 */
export function safeValidate<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; error: z.ZodError } {
  const result = schema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  } else {
    return { success: false, error: result.error };
  }
}
