/**
 * Knowledge Extraction Service
 * Extracts skills and experiences from resumes, profiles, and conversations
 */

import Anthropic from '@anthropic-ai/sdk';
import { logger } from '../../utils/logger';
import { ExtractionError } from '../../utils/errors';
import { ExtractionResult, ProficiencyLevel } from '../../types';
import postgres from '../../db/postgresql/connection';
import neo4jDB from '../../db/neo4j/connection';

const anthropic = new Anthropic({
  apiKey: process.env.CLAUDE_API_KEY,
});

export class KnowledgeExtractionService {
  /**
   * Extract skills from resume text using LLM
   */
  async extractFromResumeText(resumeText: string): Promise<ExtractionResult> {
    try {
      logger.info('Starting resume extraction');

      const prompt = `
You are an expert at analyzing resumes and extracting skills with proficiency levels.

Analyze the following resume and extract:
1. All technical and soft skills mentioned
2. Estimated proficiency level for each skill (beginner, intermediate, advanced, expert)
3. Evidence/context for each skill
4. Work experiences with skills used

Resume:
${resumeText}

Return a JSON object with this structure:
{
  "skills": [
    {
      "name": "skill name",
      "proficiency_level": "beginner|intermediate|advanced|expert",
      "proficiency_score": 0.0-1.0,
      "confidence": 0.0-1.0,
      "evidence": ["context where skill was mentioned"]
    }
  ],
  "experiences": [
    {
      "title": "job title",
      "organization": "company name",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or null",
      "description": "brief description",
      "skills_used": ["skill1", "skill2"]
    }
  ]
}

Be conservative with proficiency estimates. Use evidence like years of experience, project complexity, and action verbs.
`;

      const message = await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 4000,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
      });

      const responseText = message.content[0].type === 'text' ? message.content[0].text : '';
      const extracted = JSON.parse(responseText);

      // Map skills to our database and normalize
      const result = await this.normalizeExtraction(extracted);

      logger.info('Resume extraction completed', { skillCount: result.skills.length });
      return result;
    } catch (error) {
      logger.error('Resume extraction failed', { error });
      throw new ExtractionError('Failed to extract knowledge from resume');
    }
  }

  /**
   * Normalize and validate extraction results
   */
  private async normalizeExtraction(extracted: any): Promise<ExtractionResult> {
    // Match extracted skills against our skill taxonomy in Neo4j
    const normalizedSkills = [];

    for (const skill of extracted.skills) {
      const matchedSkill = await this.matchSkillToTaxonomy(skill.name);

      normalizedSkills.push({
        skill_id: matchedSkill.skill_id,
        name: matchedSkill.name,
        proficiency_score: this.proficiencyLevelToScore(skill.proficiency_level),
        confidence: skill.confidence,
        evidence: skill.evidence,
      });
    }

    return {
      skills: normalizedSkills,
      experiences: extracted.experiences.map((exp: any) => ({
        ...exp,
        start_date: exp.start_date ? new Date(exp.start_date) : new Date(),
        end_date: exp.end_date ? new Date(exp.end_date) : undefined,
      })),
    };
  }

  /**
   * Match skill name to skill taxonomy
   */
  private async matchSkillToTaxonomy(
    skillName: string
  ): Promise<{ skill_id: string; name: string }> {
    // Check if skill exists in Neo4j
    const query = `
      MATCH (s:Skill)
      WHERE toLower(s.name) = toLower($skillName)
         OR toLower(s.canonical_name) = toLower($skillName)
      RETURN s.id AS skill_id, s.name AS name
      LIMIT 1
    `;

    const results = await neo4jDB.read<{ skill_id: string; name: string }>(query, {
      skillName,
    });

    if (results.length > 0) {
      return results[0];
    }

    // If not found, create new skill
    logger.info('Creating new skill', { skillName });

    const createQuery = `
      CREATE (s:Skill {
        id: $skillId,
        name: $name,
        canonical_name: $canonicalName,
        category: 'uncategorized',
        domain: 'general',
        popularity_score: 0.5
      })
      RETURN s.id AS skill_id, s.name AS name
    `;

    const skillId = `skill_${skillName.toLowerCase().replace(/[^a-z0-9]/g, '_')}`;
    const created = await neo4jDB.write<{ skill_id: string; name: string }>(createQuery, {
      skillId,
      name: skillName,
      canonicalName: skillName.toLowerCase(),
    });

    return created[0];
  }

  /**
   * Convert proficiency level to numeric score
   */
  private proficiencyLevelToScore(level: string): number {
    switch (level.toLowerCase()) {
      case 'beginner':
        return 0.25;
      case 'intermediate':
        return 0.5;
      case 'advanced':
        return 0.75;
      case 'expert':
        return 0.95;
      default:
        return 0.5;
    }
  }

  /**
   * Store extracted knowledge in user's knowledge graph
   */
  async storeKnowledge(userId: string, extraction: ExtractionResult): Promise<void> {
    logger.info('Storing extracted knowledge', { userId, skillCount: extraction.skills.length });

    // Store in PostgreSQL (skill_progress table)
    for (const skill of extraction.skills) {
      await postgres.query(
        `
        INSERT INTO skill_progress (
          user_id, skill_id, proficiency_score, proficiency_level,
          confidence_score, evidence_count, is_active
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (user_id, skill_id)
        DO UPDATE SET
          proficiency_score = GREATEST(skill_progress.proficiency_score, EXCLUDED.proficiency_score),
          confidence_score = EXCLUDED.confidence_score,
          evidence_count = skill_progress.evidence_count + 1,
          updated_at = CURRENT_TIMESTAMP
      `,
        [
          userId,
          skill.skill_id,
          skill.proficiency_score,
          this.scoreToLevel(skill.proficiency_score),
          skill.confidence,
          skill.evidence.length,
          true,
        ]
      );
    }

    // Create relationships in Neo4j
    for (const skill of extraction.skills) {
      await neo4jDB.write(
        `
        MERGE (p:Person {id: $userId})
        MERGE (s:Skill {id: $skillId})
        MERGE (p)-[r:HAS_SKILL]->(s)
        ON CREATE SET
          r.proficiency_score = $proficiency,
          r.confidence = $confidence,
          r.evidence_count = $evidenceCount,
          r.created_at = datetime()
        ON MATCH SET
          r.proficiency_score = $proficiency,
          r.updated_at = datetime()
      `,
        {
          userId,
          skillId: skill.skill_id,
          proficiency: skill.proficiency_score,
          confidence: skill.confidence,
          evidenceCount: skill.evidence.length,
        }
      );
    }

    logger.info('Knowledge storage completed', { userId });
  }

  /**
   * Convert numeric score to proficiency level
   */
  private scoreToLevel(score: number): ProficiencyLevel {
    if (score < 0.3) return ProficiencyLevel.BEGINNER;
    if (score < 0.6) return ProficiencyLevel.INTERMEDIATE;
    if (score < 0.85) return ProficiencyLevel.ADVANCED;
    return ProficiencyLevel.EXPERT;
  }
}

export const knowledgeExtractionService = new KnowledgeExtractionService();
