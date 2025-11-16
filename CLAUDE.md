# CLAUDE.md - AI Assistant Guide for Digital Knowledge Twin Platform

## Document Information
- **Version**: 1.1
- **Last Updated**: November 2025
- **Status**: Active Development
- **Project**: Digital Knowledge Twin Platform

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Repository Structure](#repository-structure)
5. [Development Workflow](#development-workflow)
6. [Code Conventions](#code-conventions)
7. [Data Models & Schemas](#data-models--schemas)
8. [API Design Guidelines](#api-design-guidelines)
9. [Testing Strategy](#testing-strategy)
10. [Security & Privacy](#security--privacy)
11. [Performance & Scalability](#performance--scalability)
12. [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Project Overview

### What is Digital Knowledge Twin?

The **Digital Knowledge Twin Platform** creates a dynamic, comprehensive representation of an individual's knowledge and skills, then generates personalized learning paths to bridge gaps between current state and desired goals. Think of it as a "digital mirror" of what someone knows and an intelligent guide for what they should learn next.

### Core Capabilities

1. **Knowledge Extraction**: Multi-source ingestion (resumes, profiles, conversations, GitHub) to build comprehensive skill inventory
2. **Knowledge Graph**: Graph database representing skills, relationships, proficiency levels, and learning pathways
3. **Learning Path Generation**: AI-powered path creation optimized for individual learning velocity and preferences
4. **Content Curation**: Daily/weekly scraping and recommendation of relevant learning resources
5. **Progress Tracking**: Real-time monitoring of learning activities and skill development
6. **Adaptive Interventions**: Proactive support when learners struggle or disengage

### Key Design Principles

- **Privacy-First**: User owns their knowledge data; explicit consent for all uses
- **Accuracy Over Speed**: Better to be correct than fast; validate before asserting
- **Adaptive**: System learns from user behavior and outcomes
- **Explainable**: Users understand why recommendations are made
- **Scalable**: Architecture supports growth from 1K to 1M+ users

### Performance Targets

```
API Response Times (p95):
• Simple queries: < 100ms
• Complex queries (dashboard): < 500ms
• Learning path generation: < 2 seconds
• Knowledge graph queries: < 300ms

Scalability:
• Support 1M users
• 10K concurrent users
• 1000 requests/second
• 100GB+ knowledge graph
```

---

## System Architecture

### High-Level Architecture

The platform follows a **microservices architecture** with the following layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│  - Web App (React/TypeScript)                                   │
│  - Mobile App (React Native)                                     │
│  - API SDK (REST/GraphQL)                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
│  - Authentication (Auth0/JWT)                                   │
│  - Rate Limiting (Redis)                                         │
│  - Request Routing                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   APPLICATION SERVICES                           │
│  - Knowledge Extraction Service                                  │
│  - Learning Path Generation Service                              │
│  - Content Discovery Service                                     │
│  - Progress Tracking Service                                     │
│  - Intervention Service                                          │
│  - Analytics Service                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BACKGROUND PROCESSING                          │
│  - Daily Content Scraper (6 AM UTC)                             │
│  - Weekly Knowledge Twin Update (Sunday 3 AM UTC)               │
│  - Intervention Detection (Monday 1 AM UTC)                     │
│  - Skill Decay Calculator (Daily 2 AM UTC)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         AI/ML LAYER                              │
│  - NLP Engine (spaCy, Transformers)                             │
│  - LLM Integration (Claude API, GPT-4)                          │
│  - Knowledge Graph Reasoning                                     │
│  - Recommendation Engine                                         │
│  - Intervention Predictor                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                               │
│  - PostgreSQL (users, activities, progress)                     │
│  - Neo4j (knowledge graph)                                       │
│  - MongoDB (scraped content, documents)                          │
│  - Redis (cache, sessions, queues)                              │
│  - Pinecone (content embeddings, semantic search)               │
│  - ClickHouse/Snowflake (analytics warehouse)                   │
└─────────────────────────────────────────────────────────────────┘
```

### Service Communication Patterns

**Synchronous**: REST/GraphQL for user-facing operations
**Asynchronous**: Event-driven via message queues (Redis/Kafka) for:
- Learning activity processing
- Knowledge graph updates
- Progress calculations
- Intervention triggers

---

## Technology Stack

### Frontend Stack
- **Web**: React 18, TypeScript, TailwindCSS
- **Mobile**: React Native, TypeScript
- **State Management**: Redux Toolkit, React Query
- **Visualization**: D3.js (graphs), Recharts (analytics), Cytoscape.js (knowledge graph)
- **Real-time**: WebSockets for live updates

### Backend Stack
- **Primary Language**: TypeScript (Node.js) **OR** Python 3.11+
- **API Framework**:
  - Node: Express/Fastify
  - Python: FastAPI
- **API Protocols**: REST + GraphQL (Apollo Server/Strawberry)
- **Authentication**: Auth0 or Clerk

### AI/ML Stack
- **NLP**: spaCy, Hugging Face Transformers
- **LLM**: Claude API (Anthropic), OpenAI GPT-4
- **ML Framework**: scikit-learn, PyTorch
- **Feature Store**: Feast (optional)

### Data Stack
- **Relational DB**: PostgreSQL 15+ (Supabase or AWS RDS)
- **Graph DB**: Neo4j 5.x (AuraDB or self-hosted)
- **Vector DB**: Pinecone or Weaviate
- **Cache**: Redis 7.x (ElastiCache)
- **Document Store**: MongoDB
- **Analytics DB**: ClickHouse or Snowflake
- **Object Storage**: AWS S3 or equivalent

### Infrastructure
- **Cloud Provider**: AWS (primary) or GCP
- **Containers**: Docker
- **Orchestration**: Kubernetes (EKS/GKE)
- **Message Queue**: Redis + BullMQ or Apache Kafka
- **Workflow Orchestration**: Apache Airflow or Temporal
- **CDN**: CloudFront or Cloudflare
- **Monitoring**: Datadog/Grafana/Prometheus
- **Logging**: ELK Stack or CloudWatch

---

## Repository Structure

```
Digital-twin/
├── .git/                           # Git version control
├── .github/                        # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml                  # CI pipeline
│       ├── deploy-staging.yml
│       └── deploy-production.yml
├── docs/                           # Documentation
│   ├── architecture/               # System architecture
│   ├── api/                        # API documentation
│   ├── data-models/                # Data model specs
│   └── TECHNICAL_DESIGN.md         # Full technical spec
├── src/                            # Source code
│   ├── api/                        # API layer
│   │   ├── rest/                   # REST endpoints
│   │   ├── graphql/                # GraphQL schema & resolvers
│   │   └── middleware/             # Auth, rate limiting, etc.
│   ├── services/                   # Business logic services
│   │   ├── knowledge-extraction/
│   │   ├── learning-path/
│   │   ├── content-discovery/
│   │   ├── progress-tracking/
│   │   ├── intervention/
│   │   └── analytics/
│   ├── ml/                         # Machine learning models
│   │   ├── nlp/                    # NLP models (skill extraction)
│   │   ├── recommendation/         # Recommendation algorithms
│   │   └── intervention/           # Intervention prediction
│   ├── db/                         # Database layer
│   │   ├── postgresql/             # SQL schemas & migrations
│   │   ├── neo4j/                  # Cypher queries & graph logic
│   │   ├── mongodb/                # Document schemas
│   │   └── redis/                  # Cache patterns
│   ├── jobs/                       # Background jobs (Airflow DAGs)
│   │   ├── daily-scraper.py
│   │   ├── weekly-twin-update.py
│   │   ├── intervention-detector.py
│   │   └── skill-decay.py
│   ├── utils/                      # Utility functions
│   │   ├── validators/
│   │   ├── formatters/
│   │   └── helpers/
│   └── types/                      # TypeScript types / Python models
├── tests/                          # Test suites
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   ├── e2e/                        # End-to-end tests
│   └── fixtures/                   # Test data
├── scripts/                        # Build & deployment scripts
│   ├── setup-dev.sh
│   ├── migrate-db.sh
│   └── seed-data.sh
├── config/                         # Configuration files
│   ├── development.env
│   ├── staging.env
│   └── production.env.example
├── docker/                         # Docker configurations
│   ├── Dockerfile.api
│   ├── Dockerfile.jobs
│   └── docker-compose.yml
├── .gitignore
├── .env.example
├── package.json                    # (if Node.js)
├── pyproject.toml                  # (if Python)
├── README.md                       # Project README
└── CLAUDE.md                       # This file
```

---

## Development Workflow

### Branch Strategy

1. **Main Branch**: `main`
   - Production-ready code only
   - Protected branch with required reviews
   - All changes via pull requests

2. **Development Branches**: `claude/*` or `feature/*`
   - Feature development happens here
   - Branch naming: `claude/feature-description-sessionid` or `feature/descriptive-name`
   - Always create from latest main branch
   - **IMPORTANT**: For Claude Code sessions, branch must start with `claude/` and end with session ID

3. **Hotfix Branches**: `hotfix/*`
   - Critical bug fixes
   - Merged directly to main

### Commit Guidelines

Follow **conventional commit format**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature (e.g., `feat(learning-path): add adaptive difficulty adjustment`)
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `data`: Database migrations or schema changes

**Scopes** (component-specific):
- `knowledge-extraction`
- `learning-path`
- `content-discovery`
- `progress-tracking`
- `intervention`
- `analytics`
- `api`
- `db`
- `ml`

**Examples**:
```
feat(knowledge-extraction): add GitHub repository analysis
fix(learning-path): resolve infinite loop in prerequisite resolution
data(postgresql): add skill_progress table with indexes
docs(api): update REST endpoint documentation for /goals
perf(knowledge-graph): optimize skill gap analysis query
```

### Pull Request Process

1. **Create PR** from your feature branch to main
2. **Title**: Clear, descriptive summary
3. **Description**: Include:
   - Summary of changes (2-5 bullet points)
   - Related issue/ticket number
   - Breaking changes (if any)
   - Test coverage
   - Screenshots/demos (for UI changes)
4. **Review**: Wait for code review approval
5. **Merge**: Squash and merge after approval

### Development Setup

```bash
# Clone repository
git clone https://github.com/mdomarsaleem1/Digital-twin.git
cd Digital-twin

# Install dependencies
npm install  # or: pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Set up databases (Docker Compose)
docker-compose up -d postgres neo4j redis mongodb

# Run migrations
npm run migrate  # or: python scripts/migrate-db.py

# Seed development data
npm run seed  # or: python scripts/seed-data.py

# Start development server
npm run dev  # or: python -m uvicorn main:app --reload
```

---

## Code Conventions

### General Principles

1. **SOLID Principles**: Follow Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
2. **DRY**: Don't Repeat Yourself - extract common logic
3. **KISS**: Keep It Simple - avoid over-engineering
4. **YAGNI**: Don't add features until needed

### Naming Conventions

**TypeScript/JavaScript**:
```typescript
// Variables & Functions: camelCase
const learningPath = generatePath();
function calculateProficiency(skill: Skill): number { }

// Classes: PascalCase
class KnowledgeGraphService { }

// Constants: UPPER_SNAKE_CASE
const MAX_RETRY_ATTEMPTS = 3;
const DEFAULT_PROFICIENCY_THRESHOLD = 0.6;

// Files: kebab-case
// learning-path-generator.ts
// knowledge-extraction-service.ts
```

**Python**:
```python
# Variables & Functions: snake_case
learning_path = generate_path()
def calculate_proficiency(skill: Skill) -> float:
    pass

# Classes: PascalCase
class KnowledgeGraphService:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_PROFICIENCY_THRESHOLD = 0.6

# Files: snake_case
# learning_path_generator.py
# knowledge_extraction_service.py
```

### Code Organization

1. **One responsibility per file/module**
2. **Group related functions together**
3. **Imports at the top** (grouped: stdlib, third-party, local)
4. **Exports at the bottom** (or inline named exports)

### Comments & Documentation

```typescript
/**
 * Generates a personalized learning path for a user's goal.
 *
 * Uses graph algorithms to find optimal skill acquisition sequence
 * considering prerequisites, proficiency gaps, and time constraints.
 *
 * @param userId - UUID of the user
 * @param goalId - UUID of the target goal
 * @param preferences - User's learning preferences
 * @returns Generated learning path with estimated timeline
 * @throws {InsufficientDataError} If user profile is incomplete
 * @throws {NoPathFoundError} If no valid path exists
 */
async function generateLearningPath(
  userId: string,
  goalId: string,
  preferences: LearningPreferences
): Promise<LearningPath> {
  // Implementation
}
```

### Error Handling

**Always handle errors explicitly**:

```typescript
// ✅ Good: Explicit error handling
try {
  const skills = await extractSkillsFromResume(file);
  return skills;
} catch (error) {
  if (error instanceof FileParseError) {
    logger.error('Failed to parse resume', { error, fileId: file.id });
    throw new ExtractionError('Resume format not supported');
  }
  throw error; // Re-throw unexpected errors
}

// ❌ Bad: Swallowing errors
try {
  const skills = await extractSkillsFromResume(file);
} catch (error) {
  // Silent failure - never do this!
}
```

**Custom Error Classes**:

```typescript
export class KnowledgeTwinError extends Error {
  constructor(message: string, public code: string) {
    super(message);
    this.name = 'KnowledgeTwinError';
  }
}

export class ExtractionError extends KnowledgeTwinError { }
export class PathGenerationError extends KnowledgeTwinError { }
export class InsufficientDataError extends KnowledgeTwinError { }
```

### Security Best Practices

1. **Input Validation**: Validate ALL user inputs
```typescript
// Use validation libraries (Zod, Joi, Pydantic)
const GoalSchema = z.object({
  type: z.enum(['role', 'skill', 'certification']),
  target: z.string().min(3).max(255),
  timeline_months: z.number().int().min(1).max(60)
});
```

2. **SQL Injection Prevention**: Use parameterized queries
```typescript
// ✅ Good: Parameterized
const result = await db.query(
  'SELECT * FROM users WHERE email = $1',
  [email]
);

// ❌ Bad: String concatenation
const result = await db.query(
  `SELECT * FROM users WHERE email = '${email}'`
);
```

3. **Secrets Management**: Never commit secrets
```typescript
// ✅ Good: Environment variables
const apiKey = process.env.CLAUDE_API_KEY;

// ❌ Bad: Hardcoded
const apiKey = 'sk-ant-api03-...'; // NEVER DO THIS
```

4. **Data Encryption**:
   - At rest: AES-256
   - In transit: TLS 1.3
   - Sensitive fields: Encrypt before storing (e.g., PII)

---

## Data Models & Schemas

### PostgreSQL Schema

**Key Tables**:

```sql
-- Users & Authentication
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Goals
CREATE TABLE goals (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  type VARCHAR(50), -- 'role', 'skill', 'certification'
  target TEXT NOT NULL,
  timeline_months INTEGER,
  status VARCHAR(20) DEFAULT 'active'
);

-- Skill Progress
CREATE TABLE skill_progress (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  skill_id VARCHAR(100), -- Links to Neo4j
  proficiency_score DECIMAL(4,3), -- 0.000 to 1.000
  proficiency_level VARCHAR(20), -- 'beginner', 'intermediate', 'advanced', 'expert'
  last_practiced DATE,
  is_active BOOLEAN DEFAULT TRUE,
  updated_at TIMESTAMP
);

-- Learning Activities (Event Log)
CREATE TABLE learning_activities (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  event_type VARCHAR(50), -- 'resource_completed', 'assessment_taken', etc.
  resource_id UUID,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSONB, -- Flexible event data
  time_spent_seconds INTEGER
);

CREATE INDEX idx_activities_user_timestamp
  ON learning_activities(user_id, timestamp DESC);
```

**Schema Conventions**:
- Use UUIDs for primary keys
- Use `created_at`, `updated_at` timestamps
- Use JSONB for flexible/nested data
- Index foreign keys and commonly queried columns
- Use `snake_case` for column names

### Neo4j Graph Schema

**Node Types**:
- `Person`: User whose knowledge we're modeling
- `Skill`: Atomic knowledge unit (Python, SQL, Leadership)
- `Domain`: High-level area (Software Engineering, Data Science)
- `Resource`: Learning materials (courses, books, videos)
- `Goal`: User's learning objectives
- `LearningPath`: Generated learning sequence
- `Experience`: Work history, projects, certifications

**Relationship Types**:
- `HAS_SKILL`: Person → Skill (with proficiency properties)
- `REQUIRES`: Skill → Skill (prerequisite)
- `TEACHES_SKILL`: Resource → Skill
- `BELONGS_TO`: Skill → Domain
- `TARGETS`: LearningPath → Goal
- `UTILIZED_SKILL`: Experience → Skill

**Example Cypher Queries**:

```cypher
// Create a skill with prerequisites
CREATE (python:Skill {
  id: 'skill_python',
  name: 'Python',
  category: 'programming_language'
})
CREATE (oop:Skill {
  id: 'skill_oop',
  name: 'Object-Oriented Programming'
})
CREATE (python)-[:REQUIRES {strength: 0.7}]->(oop)

// Find skills required for a goal
MATCH (g:Goal {id: $goalId})-[:REQUIRES_SKILL]->(s:Skill)
RETURN s

// Calculate skill gap for a user
MATCH (u:Person {id: $userId})-[:HAS_GOAL]->(g:Goal)
MATCH (g)-[:REQUIRES_SKILL]->(required:Skill)
OPTIONAL MATCH (u)-[has:HAS_SKILL]->(required)
WHERE has IS NULL OR has.proficiency_score < required.target_proficiency
RETURN required.name, required.target_proficiency, COALESCE(has.proficiency_score, 0) AS current
```

### MongoDB Document Schemas

**Resources Collection**:
```javascript
{
  _id: ObjectId,
  resource_id: "uuid",
  title: "Machine Learning Specialization",
  description: "Master fundamental AI concepts...",
  type: "course",
  format: "video",
  difficulty: "intermediate",
  duration_hours: 45,
  price_usd: 49.00,
  rating: 4.8,
  quality_score: 0.87,
  skills_taught: [
    { skill_id: "skill_ml", proficiency_target: "intermediate" }
  ],
  scraped_at: ISODate("2025-11-16"),
  is_active: true
}
```

**Indexes**:
```javascript
db.resources.createIndex({ resource_id: 1 }, { unique: true });
db.resources.createIndex({ "skills_taught.skill_id": 1 });
db.resources.createIndex({ quality_score: -1 });
```

---

## API Design Guidelines

### REST API Structure

**Base URL**: `https://api.knowledgetwin.com/v1`

**Endpoint Naming**:
- Use **nouns** (not verbs): `/users`, `/goals`, `/learning-paths`
- Use **plural** names: `/skills` not `/skill`
- Use **kebab-case**: `/learning-paths` not `/learningPaths`
- Nest resources logically: `/learning-paths/{id}/steps`

**HTTP Methods**:
```
GET    /resources          - List resources (with filtering/pagination)
GET    /resources/{id}     - Get specific resource
POST   /resources          - Create new resource
PUT    /resources/{id}     - Update entire resource
PATCH  /resources/{id}     - Partial update
DELETE /resources/{id}     - Delete resource
```

**Response Format**:

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Learning Path Name",
    "status": "active"
  },
  "meta": {
    "timestamp": "2025-11-16T12:00:00Z",
    "version": "v1"
  }
}
```

**Error Response**:

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_DATA",
    "message": "User profile incomplete. Please add skills first.",
    "details": {
      "missing_fields": ["skills", "goals"]
    }
  },
  "meta": {
    "timestamp": "2025-11-16T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

**Pagination**:

```
GET /resources?page=2&limit=20&sort=-created_at

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": true
  }
}
```

### GraphQL Schema

```graphql
type User {
  id: ID!
  email: String!
  profile: UserProfile
  skills: [UserSkill!]!
  goals: [Goal!]!
  learningPaths: [LearningPath!]!
}

type UserSkill {
  skill: Skill!
  proficiencyScore: Float!
  proficiencyLevel: ProficiencyLevel!
  lastPracticed: Date
}

enum ProficiencyLevel {
  BEGINNER
  INTERMEDIATE
  ADVANCED
  EXPERT
}

type Query {
  me: User!
  mySkills(domain: String): [UserSkill!]!
  recommendedResources(skillId: ID, limit: Int): [Resource!]!
}

type Mutation {
  createGoal(input: GoalInput!): Goal!
  generateLearningPath(goalId: ID!): LearningPath!
  completeResource(resourceId: ID!, timeSpent: Int!): Activity!
}
```

---

## Testing Strategy

### Test Coverage Requirements

- **Unit Tests**: 80%+ coverage for services and utilities
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user journeys (onboarding, path generation)

### Test Organization

```
tests/
├── unit/
│   ├── services/
│   │   ├── knowledge-extraction.test.ts
│   │   └── learning-path.test.ts
│   └── utils/
│       └── validators.test.ts
├── integration/
│   ├── api/
│   │   ├── auth.test.ts
│   │   ├── goals.test.ts
│   │   └── learning-paths.test.ts
│   └── db/
│       ├── postgresql.test.ts
│       └── neo4j.test.ts
└── e2e/
    ├── onboarding-flow.test.ts
    └── learning-journey.test.ts
```

### Testing Best Practices

**Unit Test Example**:

```typescript
describe('calculateProficiencyBoost', () => {
  it('should give larger boost for beginners', () => {
    const boost = calculateProficiencyBoost({
      currentProficiency: 0.2, // beginner
      resourceEffectiveness: 0.9,
      assessmentScore: 85
    });

    expect(boost).toBeGreaterThan(0.15);
    expect(boost).toBeLessThan(0.30);
  });

  it('should give smaller boost for experts', () => {
    const boost = calculateProficiencyBoost({
      currentProficiency: 0.9, // expert
      resourceEffectiveness: 0.9,
      assessmentScore: 85
    });

    expect(boost).toBeGreaterThan(0.01);
    expect(boost).toBeLessThan(0.05);
  });
});
```

**Integration Test Example**:

```typescript
describe('POST /learning-paths/generate', () => {
  it('should generate valid learning path for goal', async () => {
    const user = await createTestUser();
    const goal = await createTestGoal(user.id, {
      type: 'role',
      target: 'Machine Learning Engineer'
    });

    const response = await request(app)
      .post('/v1/learning-paths/generate')
      .auth(user.token, { type: 'bearer' })
      .send({ goal_id: goal.id });

    expect(response.status).toBe(201);
    expect(response.body.data).toHaveProperty('id');
    expect(response.body.data.steps.length).toBeGreaterThan(0);
    expect(response.body.data.estimated_hours).toBeGreaterThan(0);
  });
});
```

**Test Data Factories**:

```typescript
// Use factories for consistent test data
export const createTestUser = async (overrides = {}) => {
  return await db.users.create({
    email: faker.internet.email(),
    name: faker.person.fullName(),
    ...overrides
  });
};

export const createTestSkill = (overrides = {}) => {
  return {
    id: `skill_${faker.string.uuid()}`,
    name: faker.lorem.word(),
    category: 'programming',
    ...overrides
  };
};
```

---

## Security & Privacy

### Authentication & Authorization

**Authentication**: JWT tokens via Auth0/Clerk
```typescript
// Middleware to verify JWT
export const authenticate = async (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const decoded = await verifyToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};
```

**Authorization**: Resource-level access control
```typescript
// Ensure users can only access their own data
export const authorizeResource = (resourceType: string) => {
  return async (req, res, next) => {
    const resource = await db[resourceType].findById(req.params.id);

    if (resource.user_id !== req.user.id) {
      return res.status(403).json({ error: 'Forbidden' });
    }

    next();
  };
};

// Usage
app.get('/goals/:id', authenticate, authorizeResource('goals'), getGoal);
```

### Data Privacy

**Privacy Principles**:
1. **User Ownership**: Users own their knowledge data
2. **Transparency**: Clear about data collection and usage
3. **Control**: Users can view, edit, export, delete their data
4. **Minimal Collection**: Only collect necessary data
5. **No Selling**: Never sell user data

**Compliance**:
- **GDPR**: Right to access, rectify, erase, port data
- **CCPA**: Right to know, delete, opt-out
- **COPPA**: Parental consent for users under 13

**Data Encryption**:
```typescript
// Encrypt sensitive fields before storing
import { encrypt, decrypt } from './crypto';

const encryptedData = encrypt(sensitiveData, process.env.ENCRYPTION_KEY);
await db.users.update(userId, { encrypted_field: encryptedData });

// Decrypt when retrieving
const decryptedData = decrypt(user.encrypted_field, process.env.ENCRYPTION_KEY);
```

---

## Performance & Scalability

### Caching Strategy

**Redis Cache Layers**:

```typescript
// Dashboard cache (1 hour TTL)
const CACHE_KEY = `dashboard:${userId}`;
const cached = await redis.get(CACHE_KEY);
if (cached) {
  return JSON.parse(cached);
}

const data = await buildDashboard(userId);
await redis.setex(CACHE_KEY, 3600, JSON.stringify(data));
return data;

// Recommendation cache (6 hours TTL)
const recKey = `recommendations:${userId}`;
// ... similar pattern
```

**Cache Invalidation**:

```typescript
// Invalidate when user data changes
export const invalidateUserCache = async (userId: string) => {
  const keys = [
    `dashboard:${userId}`,
    `recommendations:${userId}`,
    `progress:${userId}:*`
  ];

  await redis.del(...keys);
};

// Call after mutations
await updateSkillProficiency(userId, skillId, newScore);
await invalidateUserCache(userId);
```

### Database Optimization

**PostgreSQL**:
- Use indexes on foreign keys and query columns
- Use EXPLAIN ANALYZE to optimize slow queries
- Partition large tables (e.g., learning_activities by month)
- Use connection pooling (PgBouncer)

```sql
-- Index frequently queried columns
CREATE INDEX idx_skill_progress_user_active
  ON skill_progress(user_id, is_active);

-- Explain query performance
EXPLAIN ANALYZE
SELECT * FROM learning_activities
WHERE user_id = '...' AND timestamp > NOW() - INTERVAL '7 days';
```

**Neo4j**:
- Create indexes for node properties used in WHERE clauses
- Use query hints for complex patterns
- Limit result sets with LIMIT

```cypher
// Create index
CREATE INDEX skill_id_index FOR (s:Skill) ON (s.id);

// Use LIMIT in queries
MATCH (u:Person {id: $userId})-[:HAS_SKILL]->(s:Skill)
RETURN s
LIMIT 100;
```

### Performance Monitoring

**Track Key Metrics**:
- API response times (p50, p95, p99)
- Database query duration
- Cache hit rates
- Background job completion times
- Error rates

**Set Performance Budgets**:
```typescript
// Warn if API response exceeds budget
export const performanceMiddleware = (budget: number) => {
  return (req, res, next) => {
    const start = Date.now();

    res.on('finish', () => {
      const duration = Date.now() - start;
      if (duration > budget) {
        logger.warn('Performance budget exceeded', {
          endpoint: req.path,
          duration,
          budget
        });
      }
    });

    next();
  };
};

app.use('/v1/dashboard', performanceMiddleware(500)); // 500ms budget
```

---

## AI Assistant Guidelines

### When Working on This Repository

#### 1. Understand Context First

Before making changes:
- **Read the technical design document** (docs/TECHNICAL_DESIGN.md)
- **Check existing patterns** in the codebase
- **Review related files** to understand current implementation
- **Look at recent commits** for context on why code is structured a certain way

#### 2. Use TodoWrite Tool Proactively

For ANY multi-step task:
```
1. Create comprehensive todo list at start
2. Mark task as "in_progress" BEFORE starting work
3. Mark as "completed" IMMEDIATELY after finishing
4. Don't batch multiple completions - update in real-time
```

Example:
```typescript
// User asks: "Implement skill decay calculation"

// Step 1: Create todos
TodoWrite([
  { content: "Research skill decay algorithm from design doc", status: "in_progress" },
  { content: "Create skill decay calculation function", status: "pending" },
  { content: "Add unit tests for decay function", status: "pending" },
  { content: "Create Airflow DAG for daily decay job", status: "pending" },
  { content: "Test decay calculation with sample data", status: "pending" }
]);

// Step 2: Complete each task and update immediately
// ... after researching ...
TodoWrite([
  { content: "Research skill decay algorithm from design doc", status: "completed" },
  { content: "Create skill decay calculation function", status: "in_progress" },
  ...
]);
```

#### 3. Code Quality Standards

**Before Committing**:
- ✅ All tests pass
- ✅ No linting errors
- ✅ Type checks pass (TypeScript)
- ✅ Security vulnerabilities addressed
- ✅ Performance considered
- ✅ Documentation updated

**Code Review Checklist**:
- Is the code readable and maintainable?
- Are edge cases handled?
- Is error handling comprehensive?
- Are there tests covering the changes?
- Is the code following existing patterns?
- Are there any security concerns?

#### 4. Domain-Specific Guidelines

**Knowledge Extraction**:
- Always validate extracted data with user
- Set confidence scores for uncertain extractions
- Handle multiple data sources gracefully
- Never assume proficiency without evidence

**Learning Path Generation**:
- Always check for prerequisite cycles
- Validate timeline feasibility
- Ensure all resources exist and are active
- Consider user's time constraints

**Progress Tracking**:
- Track ALL learning activities (even partial)
- Calculate proficiency changes incrementally
- Don't overwrite manual user adjustments
- Maintain audit trail

**Interventions**:
- Be empathetic and encouraging
- Provide actionable suggestions
- Don't spam users with notifications
- Track intervention effectiveness

#### 5. Working with AI/ML Components

**LLM Integration (Claude API)**:
```typescript
// Always include error handling and retries
async function extractSkillsWithLLM(text: string): Promise<Skill[]> {
  const prompt = `
    Extract skills from the following resume text.
    Return a JSON array of skills with confidence scores.

    Text: ${text}
  `;

  try {
    const response = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 2000,
      messages: [{ role: 'user', content: prompt }]
    });

    const skills = JSON.parse(response.content[0].text);
    return skills.map(s => ({
      ...s,
      extraction_method: 'llm',
      confidence: s.confidence || 0.7
    }));
  } catch (error) {
    logger.error('LLM extraction failed', { error });
    // Fallback to rule-based extraction
    return extractSkillsWithRules(text);
  }
}
```

**NLP Processing**:
- Use spaCy for entity recognition
- Cache model predictions when possible
- Handle multiple languages gracefully
- Validate NLP outputs before storing

#### 6. Database Operations

**PostgreSQL**:
```typescript
// Always use transactions for related operations
const client = await pool.connect();
try {
  await client.query('BEGIN');

  // Multiple related operations
  await client.query('INSERT INTO goals ...');
  await client.query('INSERT INTO learning_paths ...');

  await client.query('COMMIT');
} catch (error) {
  await client.query('ROLLBACK');
  throw error;
} finally {
  client.release();
}
```

**Neo4j**:
```typescript
// Use parameters to prevent injection
const session = driver.session();
try {
  const result = await session.run(
    `MATCH (u:Person {id: $userId})-[:HAS_SKILL]->(s:Skill)
     RETURN s`,
    { userId }
  );
  return result.records.map(r => r.get('s'));
} finally {
  await session.close();
}
```

#### 7. Background Jobs

**Job Structure**:
```python
# Airflow DAG structure
from airflow import DAG
from airflow.operators.python import PythonOperator

def daily_skill_decay():
    """Calculate skill decay for all users."""
    users = fetch_all_active_users()

    for user in users:
        calculate_and_update_decay(user)

    logger.info(f"Processed {len(users)} users")

dag = DAG(
    'daily_skill_decay',
    schedule_interval='0 2 * * *',  # 2 AM UTC daily
    catchup=False
)

task = PythonOperator(
    task_id='calculate_decay',
    python_callable=daily_skill_decay,
    dag=dag
)
```

**Job Best Practices**:
- Always log start/completion
- Handle failures gracefully (don't fail entire job for one user error)
- Make jobs idempotent (safe to re-run)
- Monitor job duration and alert if too slow

#### 8. API Development

**Endpoint Structure**:
```typescript
// src/api/rest/learning-paths.ts

import { Router } from 'express';
import { authenticate, validate } from '../middleware';
import { GeneratePathSchema } from '../schemas';
import { LearningPathService } from '../../services/learning-path';

const router = Router();

/**
 * POST /learning-paths/generate
 * Generate a new learning path for a goal
 */
router.post(
  '/generate',
  authenticate,
  validate(GeneratePathSchema),
  async (req, res, next) => {
    try {
      const { goal_id, preferences } = req.body;
      const userId = req.user.id;

      const path = await LearningPathService.generate(
        userId,
        goal_id,
        preferences
      );

      res.status(201).json({
        success: true,
        data: path
      });
    } catch (error) {
      next(error); // Pass to error handler middleware
    }
  }
);

export default router;
```

#### 9. Common Pitfalls to Avoid

❌ **Don't**:
- Hardcode configuration values
- Skip input validation
- Ignore error cases
- Make breaking changes without migration path
- Commit secrets or API keys
- Write code without tests
- Ignore performance implications
- Make assumptions about user data

✅ **Do**:
- Use environment variables for config
- Validate all inputs
- Handle all error cases gracefully
- Provide backward compatibility
- Use secret management
- Write tests for all new code
- Profile and optimize slow operations
- Verify assumptions with data

#### 10. Getting Help

When stuck:
1. **Check documentation**: docs/ folder, technical design doc
2. **Search codebase**: Look for similar implementations
3. **Review tests**: Tests often show usage examples
4. **Ask user**: If requirements unclear, ask for clarification
5. **Propose solution**: Explain your approach before implementing

---

## Changelog

### Version History

- **v1.1** (2025-11-16): Updated for Digital Knowledge Twin Platform
  - Added comprehensive project-specific guidelines
  - Specified exact technology stack
  - Included data model schemas and conventions
  - Added AI/ML integration patterns
  - Defined API design standards
  - Expanded security and privacy guidelines

- **v1.0** (2025-11-16): Initial CLAUDE.md creation
  - Established basic project structure
  - Defined development workflows
  - Set code conventions

---

## Contact and Support

- **Repository**: mdomarsaleem1/Digital-twin
- **Issues**: Use GitHub issues for bug reports and feature requests
- **Technical Design**: See docs/TECHNICAL_DESIGN.md for full specifications

---

**Last Updated**: 2025-11-16
**Maintained By**: Engineering Team
**Version**: 1.1
**Project Status**: Active Development
