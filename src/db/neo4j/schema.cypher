// ============================================
// Digital Knowledge Twin Platform
// Neo4j Knowledge Graph Schema
// ============================================

// Create constraints and indexes

// ============================================
// NODE CONSTRAINTS
// ============================================

// Person (User) nodes
CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.id IS UNIQUE;

CREATE INDEX person_email_index IF NOT EXISTS
FOR (p:Person) ON (p.email);

// Skill nodes
CREATE CONSTRAINT skill_id_unique IF NOT EXISTS
FOR (s:Skill) REQUIRE s.id IS UNIQUE;

CREATE INDEX skill_name_index IF NOT EXISTS
FOR (s:Skill) ON (s.name);

CREATE INDEX skill_category_index IF NOT EXISTS
FOR (s:Skill) ON (s.category);

// Domain nodes
CREATE CONSTRAINT domain_id_unique IF NOT EXISTS
FOR (d:Domain) REQUIRE d.id IS UNIQUE;

CREATE INDEX domain_name_index IF NOT EXISTS
FOR (d:Domain) ON (d.name);

// Resource nodes
CREATE CONSTRAINT resource_id_unique IF NOT EXISTS
FOR (r:Resource) REQUIRE r.id IS UNIQUE;

CREATE INDEX resource_quality_index IF NOT EXISTS
FOR (r:Resource) ON (r.quality_score);

// Goal nodes
CREATE CONSTRAINT goal_id_unique IF NOT EXISTS
FOR (g:Goal) REQUIRE g.id IS UNIQUE;

// LearningPath nodes
CREATE CONSTRAINT learning_path_id_unique IF NOT EXISTS
FOR (lp:LearningPath) REQUIRE lp.id IS UNIQUE;

// Experience nodes
CREATE CONSTRAINT experience_id_unique IF NOT EXISTS
FOR (e:Experience) REQUIRE e.id IS UNIQUE;

// ============================================
// EXAMPLE DATA SEEDING
// ============================================

// Create sample domains
MERGE (softwareEng:Domain {
  id: 'domain_software_engineering',
  name: 'Software Engineering',
  description: 'Building software systems and applications',
  hierarchy_level: 1
});

MERGE (dataScience:Domain {
  id: 'domain_data_science',
  name: 'Data Science',
  description: 'Data analysis, machine learning, and AI',
  hierarchy_level: 1
});

MERGE (webDev:Domain {
  id: 'domain_web_development',
  name: 'Web Development',
  description: 'Frontend and backend web development',
  hierarchy_level: 2
})
MERGE (webDev)-[:PART_OF]->(softwareEng);

// Create sample skills
MERGE (python:Skill {
  id: 'skill_python',
  name: 'Python',
  canonical_name: 'python',
  category: 'programming_language',
  description: 'General-purpose programming language',
  popularity_score: 0.95
})
MERGE (python)-[:BELONGS_TO]->(softwareEng);

MERGE (javascript:Skill {
  id: 'skill_javascript',
  name: 'JavaScript',
  canonical_name: 'javascript',
  category: 'programming_language',
  description: 'Programming language for web development',
  popularity_score: 0.98
})
MERGE (javascript)-[:BELONGS_TO]->(webDev);

MERGE (react:Skill {
  id: 'skill_react',
  name: 'React',
  canonical_name: 'react',
  category: 'framework',
  description: 'JavaScript library for building user interfaces',
  popularity_score: 0.92
})
MERGE (react)-[:BELONGS_TO]->(webDev)
MERGE (react)-[:REQUIRES {strength: 0.9, recommended_proficiency: 'intermediate'}]->(javascript);

MERGE (typescript:Skill {
  id: 'skill_typescript',
  name: 'TypeScript',
  canonical_name: 'typescript',
  category: 'programming_language',
  description: 'Typed superset of JavaScript',
  popularity_score: 0.88
})
MERGE (typescript)-[:BELONGS_TO]->(webDev)
MERGE (typescript)-[:REQUIRES {strength: 0.8, recommended_proficiency: 'intermediate'}]->(javascript);

MERGE (nodejs:Skill {
  id: 'skill_nodejs',
  name: 'Node.js',
  canonical_name: 'nodejs',
  category: 'runtime',
  description: 'JavaScript runtime for server-side development',
  popularity_score: 0.85
})
MERGE (nodejs)-[:BELONGS_TO]->(webDev)
MERGE (nodejs)-[:REQUIRES {strength: 0.7, recommended_proficiency: 'intermediate'}]->(javascript);

MERGE (sql:Skill {
  id: 'skill_sql',
  name: 'SQL',
  canonical_name: 'sql',
  category: 'database',
  description: 'Query language for relational databases',
  popularity_score: 0.90
})
MERGE (sql)-[:BELONGS_TO]->(softwareEng);

MERGE (git:Skill {
  id: 'skill_git',
  name: 'Git',
  canonical_name: 'git',
  category: 'tool',
  description: 'Version control system',
  popularity_score: 0.95
})
MERGE (git)-[:BELONGS_TO]->(softwareEng);

MERGE (machineLearning:Skill {
  id: 'skill_machine_learning',
  name: 'Machine Learning',
  canonical_name: 'machine_learning',
  category: 'technique',
  description: 'Algorithms that learn from data',
  popularity_score: 0.87
})
MERGE (machineLearning)-[:BELONGS_TO]->(dataScience)
MERGE (machineLearning)-[:REQUIRES {strength: 0.8, recommended_proficiency: 'intermediate'}]->(python);

// Create sample prerequisite relationships
MERGE (oop:Skill {
  id: 'skill_oop',
  name: 'Object-Oriented Programming',
  canonical_name: 'oop',
  category: 'concept',
  description: 'Programming paradigm based on objects',
  popularity_score: 0.85
})
MERGE (oop)-[:BELONGS_TO]->(softwareEng);

MERGE (python)-[:REQUIRES {strength: 0.6, recommended_proficiency: 'beginner'}]->(oop);

// ============================================
// UTILITY QUERIES
// ============================================

// Query to find all skills required for a skill (prerequisites)
// MATCH (s:Skill {id: 'skill_react'})-[:REQUIRES*]->(prereq:Skill)
// RETURN s.name AS skill, collect(prereq.name) AS prerequisites;

// Query to find skill gaps for a user
// MATCH (u:Person {id: $userId})-[:HAS_GOAL]->(g:Goal)
// MATCH (g)-[:REQUIRES_SKILL]->(required:Skill)
// OPTIONAL MATCH (u)-[has:HAS_SKILL]->(required)
// WHERE has IS NULL OR has.proficiency_score < required.target_proficiency
// RETURN required.name, required.target_proficiency, COALESCE(has.proficiency_score, 0) AS current;

// Query to find learning path from current skills to goal
// MATCH path = shortestPath((start:Skill)<-[:HAS_SKILL]-(u:Person {id: $userId})-[:HAS_GOAL]->(g:Goal)-[:REQUIRES_SKILL]->(target:Skill))
// RETURN path;
