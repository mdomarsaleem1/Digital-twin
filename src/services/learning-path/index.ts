/**
 * Learning Path Generation Service
 * Generates personalized learning paths based on knowledge gaps and goals
 */

import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';
import { PathGenerationError, NotFoundError } from '../../utils/errors';
import {
  LearningPath,
  LearningPathGenerationParams,
  SkillGap,
  PathStatus,
  DifficultyLevel,
} from '../../types';
import postgres from '../../db/postgresql/connection';
import neo4jDB from '../../db/neo4j/connection';

export class LearningPathService {
  /**
   * Generate a learning path for a goal
   */
  async generatePath(params: LearningPathGenerationParams): Promise<LearningPath> {
    logger.info('Generating learning path', params);

    const { user_id, goal_id, preferences } = params;

    // 1. Get goal details
    const goal = await this.getGoal(user_id, goal_id);
    if (!goal) {
      throw new NotFoundError('Goal', goal_id);
    }

    // 2. Identify skill gaps
    const skillGaps = await this.analyzeSkillGaps(user_id, goal_id);
    logger.info('Skill gaps identified', { count: skillGaps.length });

    if (skillGaps.length === 0) {
      throw new PathGenerationError('No skill gaps found. User already has required skills.');
    }

    // 3. Resolve prerequisites and order skills
    const orderedSkills = await this.orderSkillsByPrerequisites(skillGaps);

    // 4. Match resources to skills
    const pathSteps = await this.matchResourcesToSkills(orderedSkills, preferences);

    // 5. Estimate timeline
    const totalHours = pathSteps.reduce((sum, step) => sum + step.estimated_hours, 0);
    const hoursPerWeek = preferences?.time_available_hours_per_week || 10;
    const estimatedWeeks = Math.ceil(totalHours / hoursPerWeek);

    // 6. Create learning path in database
    const learningPath = await this.saveLearningPath({
      user_id,
      goal_id,
      name: `Path to ${goal.target}`,
      description: `Personalized learning path to achieve: ${goal.target}`,
      estimated_hours: totalHours,
      estimated_weeks: estimatedWeeks,
      difficulty: this.determineDifficulty(skillGaps),
      status: PathStatus.DRAFT,
      completion_percentage: 0,
    });

    // 7. Save path steps
    await this.savePathSteps(learningPath.id, pathSteps);

    logger.info('Learning path generated', {
      path_id: learningPath.id,
      steps: pathSteps.length,
    });

    return learningPath;
  }

  /**
   * Analyze skill gaps between current and required skills
   */
  private async analyzeSkillGaps(userId: string, goalId: string): Promise<SkillGap[]> {
    const query = `
      MATCH (u:Person {id: $userId})-[:HAS_GOAL]->(g:Goal {id: $goalId})
      MATCH (g)-[:REQUIRES_SKILL]->(required:Skill)
      OPTIONAL MATCH (u)-[has:HAS_SKILL]->(required)
      WHERE has IS NULL OR has.proficiency_score < 0.7
      RETURN
        required.id AS skill_id,
        required.name AS skill_name,
        COALESCE(has.proficiency_score, 0.0) AS current_proficiency,
        0.8 AS target_proficiency,
        (0.8 - COALESCE(has.proficiency_score, 0.0)) AS gap_score,
        required.popularity_score AS priority
      ORDER BY gap_score DESC, priority DESC
    `;

    const results = await neo4jDB.read<SkillGap>(query, { userId, goalId });
    return results;
  }

  /**
   * Order skills by prerequisite dependencies
   */
  private async orderSkillsByPrerequisites(skillGaps: SkillGap[]): Promise<SkillGap[]> {
    // Build dependency graph and topologically sort
    const skillIds = skillGaps.map((gap) => gap.skill_id);

    const query = `
      MATCH (s:Skill)-[:REQUIRES*]->(prereq:Skill)
      WHERE s.id IN $skillIds AND prereq.id IN $skillIds
      RETURN s.id AS skill, prereq.id AS prerequisite
    `;

    const dependencies = await neo4jDB.read<{ skill: string; prerequisite: string }>(query, {
      skillIds,
    });

    // Topological sort (simplified - in production use proper DAG sorting)
    const ordered: SkillGap[] = [];
    const remaining = [...skillGaps];
    const processed = new Set<string>();

    while (remaining.length > 0) {
      const ready = remaining.filter((skill) => {
        const prereqs = dependencies
          .filter((d) => d.skill === skill.skill_id)
          .map((d) => d.prerequisite);
        return prereqs.every((p) => processed.has(p));
      });

      if (ready.length === 0 && remaining.length > 0) {
        // Circular dependency or isolated nodes - just take first
        ordered.push(remaining[0]);
        processed.add(remaining[0].skill_id);
        remaining.splice(0, 1);
      } else {
        ready.forEach((skill) => {
          ordered.push(skill);
          processed.add(skill.skill_id);
          const index = remaining.findIndex((s) => s.skill_id === skill.skill_id);
          remaining.splice(index, 1);
        });
      }
    }

    return ordered;
  }

  /**
   * Match learning resources to skills
   */
  private async matchResourcesToSkills(
    skills: SkillGap[],
    preferences?: any
  ): Promise<Array<{ skill_id: string; resource_ids: string[]; estimated_hours: number }>> {
    const pathSteps = [];

    for (const skill of skills) {
      // Query MongoDB for resources teaching this skill
      // Simplified - in production, use sophisticated matching algorithm
      const resources = [
        // Placeholder - would query MongoDB resources collection
        {
          id: uuidv4(),
          estimated_hours: Math.ceil(skill.gap_score * 20), // Estimate based on gap
        },
      ];

      pathSteps.push({
        skill_id: skill.skill_id,
        resource_ids: resources.map((r) => r.id),
        estimated_hours: resources.reduce((sum, r) => sum + r.estimated_hours, 0),
      });
    }

    return pathSteps;
  }

  /**
   * Get goal from database
   */
  private async getGoal(userId: string, goalId: string) {
    const result = await postgres.query(
      `SELECT * FROM goals WHERE id = $1 AND user_id = $2`,
      [goalId, userId]
    );

    return result.rows[0];
  }

  /**
   * Determine overall difficulty of path
   */
  private determineDifficulty(skillGaps: SkillGap[]): DifficultyLevel {
    const avgGap = skillGaps.reduce((sum, gap) => sum + gap.gap_score, 0) / skillGaps.length;

    if (avgGap < 0.3) return DifficultyLevel.BEGINNER;
    if (avgGap < 0.6) return DifficultyLevel.INTERMEDIATE;
    return DifficultyLevel.ADVANCED;
  }

  /**
   * Save learning path to database
   */
  private async saveLearningPath(data: Partial<LearningPath>): Promise<LearningPath> {
    const result = await postgres.query(
      `
      INSERT INTO learning_paths (
        user_id, goal_id, name, description, estimated_hours,
        estimated_weeks, difficulty, status, completion_percentage
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      RETURNING *
    `,
      [
        data.user_id,
        data.goal_id,
        data.name,
        data.description,
        data.estimated_hours,
        data.estimated_weeks,
        data.difficulty,
        data.status,
        data.completion_percentage,
      ]
    );

    return result.rows[0];
  }

  /**
   * Save path steps
   */
  private async savePathSteps(
    pathId: string,
    steps: Array<{ skill_id: string; resource_ids: string[]; estimated_hours: number }>
  ): Promise<void> {
    for (let i = 0; i < steps.length; i++) {
      await postgres.query(
        `
        INSERT INTO path_steps (
          learning_path_id, sequence_number, skill_id,
          resource_ids, estimated_hours, status
        ) VALUES ($1, $2, $3, $4, $5, $6)
      `,
        [
          pathId,
          i + 1,
          steps[i].skill_id,
          JSON.stringify(steps[i].resource_ids),
          steps[i].estimated_hours,
          'pending',
        ]
      );
    }
  }
}

export const learningPathService = new LearningPathService();
