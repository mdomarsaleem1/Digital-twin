# Digital Knowledge Twin Platform

A dynamic, personalized learning platform that creates a comprehensive representation of an individual's knowledge and skills, then generates AI-powered learning paths to bridge gaps between current state and desired goals.

## 🎯 Project Overview

The Digital Knowledge Twin Platform helps learners:

- **Extract Knowledge**: Multi-source ingestion from resumes, profiles, GitHub, and conversations
- **Visualize Skills**: Interactive knowledge graph showing skills, proficiency levels, and relationships
- **Generate Learning Paths**: AI-powered personalized learning paths optimized for individual goals
- **Track Progress**: Real-time monitoring of learning activities and skill development
- **Discover Content**: Daily/weekly curation of relevant learning resources from across the web
- **Receive Support**: Adaptive interventions when learners struggle or disengage

## 🏗️ Architecture

### Technology Stack

**Backend**:
- TypeScript 5.3+ / Node.js 18+
- Express.js (REST API)
- Apollo Server (GraphQL - to be implemented)

**Databases**:
- PostgreSQL 15+ (relational data: users, goals, progress)
- Neo4j 5.x (knowledge graph: skills, relationships, paths)
- MongoDB 7+ (document store: scraped content, resources)
- Redis 7+ (caching, sessions, queues)

**AI/ML**:
- Claude API (Anthropic) - Knowledge extraction & NLP
- OpenAI GPT-4 - Alternative LLM
- spaCy - NLP processing (to be implemented)
- Pinecone - Vector search (to be implemented)

**Infrastructure**:
- Docker & Docker Compose
- Apache Airflow (background jobs - to be implemented)
- BullMQ (job queues - to be implemented)

### System Architecture Layers

```
┌─────────────────────────────────────────┐
│      Presentation Layer (TBD)           │
│      React, TypeScript, TailwindCSS     │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         API Gateway Layer               │
│    Auth, Rate Limiting, Routing         │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│      Application Services               │
│  - Knowledge Extraction ✅               │
│  - Learning Path Generation ✅           │
│  - Progress Tracking (TBD)              │
│  - Content Discovery (TBD)              │
│  - Intervention System (TBD)            │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         Data Layer                      │
│  PostgreSQL, Neo4j, MongoDB, Redis      │
└─────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm 9+
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mdomarsaleem1/Digital-twin.git
cd Digital-twin
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys and configuration
```

Required environment variables:
- `CLAUDE_API_KEY`: Your Anthropic Claude API key
- `POSTGRES_*`: PostgreSQL connection details
- `NEO4J_*`: Neo4j connection details
- `MONGODB_URI`: MongoDB connection string
- `REDIS_*`: Redis connection details
- `JWT_SECRET`: Secret key for JWT tokens

4. **Start databases with Docker Compose**
```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Neo4j on ports 7474 (HTTP) and 7687 (Bolt)
- MongoDB on port 27017
- Redis on port 6379

5. **Run database migrations**
```bash
# PostgreSQL schema
psql -h localhost -U postgres -d knowledge_twin -f src/db/postgresql/schema.sql

# Neo4j schema
cypher-shell -u neo4j -p neo4jpassword -f src/db/neo4j/schema.cypher
```

6. **Start the development server**
```bash
npm run dev
```

The API will be available at `http://localhost:3000`

### Testing the API

**Health Check**:
```bash
curl http://localhost:3000/health
```

**Register a User**:
```bash
curl -X POST http://localhost:3000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "name": "John Doe"
  }'
```

**Login**:
```bash
curl -X POST http://localhost:3000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

## 📁 Project Structure

```
Digital-twin/
├── src/
│   ├── index.ts                    # Main entry point ✅
│   ├── types/                      # TypeScript type definitions ✅
│   │   └── index.ts
│   ├── db/                         # Database layer ✅
│   │   ├── postgresql/
│   │   │   ├── schema.sql          # PostgreSQL schema ✅
│   │   │   └── connection.ts        # Connection pool ✅
│   │   ├── neo4j/
│   │   │   ├── schema.cypher       # Neo4j graph schema ✅
│   │   │   └── connection.ts        # Driver connection ✅
│   │   ├── mongodb/
│   │   │   └── connection.ts        # MongoDB client ✅
│   │   └── redis/
│   │       └── connection.ts        # Redis client ✅
│   ├── services/                   # Business logic services
│   │   ├── knowledge-extraction/   # Skill extraction service ✅
│   │   │   └── index.ts
│   │   ├── learning-path/          # Path generation service ✅
│   │   │   └── index.ts
│   │   ├── progress-tracking/      # TODO: Progress tracking
│   │   ├── content-discovery/      # TODO: Content scraping
│   │   └── intervention/           # TODO: Intervention system
│   ├── api/                        # API layer
│   │   ├── middleware/             # Express middleware ✅
│   │   │   ├── auth.ts
│   │   │   └── errorHandler.ts
│   │   ├── rest/                   # REST endpoints
│   │   │   ├── auth.ts             # Auth endpoints ✅
│   │   │   ├── goals.ts            # TODO
│   │   │   ├── learning-paths.ts   # TODO
│   │   │   ├── resources.ts        # TODO
│   │   │   └── skills.ts           # TODO
│   │   └── graphql/                # TODO: GraphQL schema & resolvers
│   ├── utils/                      # Utility functions ✅
│   │   ├── logger.ts
│   │   ├── errors.ts
│   │   ├── validators.ts
│   │   ├── auth.ts
│   │   └── response.ts
│   └── jobs/                       # TODO: Background jobs
│       ├── daily-scraper.py
│       └── weekly-twin-update.py
├── tests/                          # TODO: Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker/
│   └── Dockerfile.api              # API Dockerfile ✅
├── docker-compose.yml              # Local development setup ✅
├── package.json                    # Dependencies ✅
├── tsconfig.json                   # TypeScript config ✅
├── .env.example                    # Environment template ✅
├── .gitignore                      # Git ignore rules ✅
├── CLAUDE.md                       # AI assistant guide ✅
└── README.md                       # This file ✅
```

## 🔧 Development

### Available Scripts

```bash
npm run dev          # Start development server with hot reload
npm run build        # Build for production
npm start            # Start production server
npm test             # Run tests (to be implemented)
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors
npm run docker:up    # Start Docker containers
npm run docker:down  # Stop Docker containers
```

### Code Style

- **TypeScript**: Strict mode enabled
- **Naming**: camelCase for variables/functions, PascalCase for classes
- **Formatting**: Prettier with 2-space indentation
- **Linting**: ESLint with TypeScript rules

## 🎓 Key Concepts

### Knowledge Graph

The knowledge graph is the core of the platform, stored in Neo4j:

**Nodes**:
- `Person`: Users whose knowledge we're modeling
- `Skill`: Atomic knowledge units (Python, SQL, Leadership)
- `Domain`: High-level areas (Software Engineering, Data Science)
- `Resource`: Learning materials (courses, books, videos)
- `Goal`: User's learning objectives

**Relationships**:
- `HAS_SKILL`: Person → Skill (with proficiency properties)
- `REQUIRES`: Skill → Skill (prerequisites)
- `TEACHES_SKILL`: Resource → Skill
- `TARGETS`: LearningPath → Goal

### Proficiency Levels

Skills are tracked with both categorical and numerical proficiency:

- **Beginner** (0.0 - 0.3): Basic understanding
- **Intermediate** (0.3 - 0.6): Can work independently
- **Advanced** (0.6 - 0.85): Deep expertise
- **Expert** (0.85 - 1.0): Mastery level

### Learning Path Generation

Paths are generated using:
1. **Gap Analysis**: Compare current skills to goal requirements
2. **Prerequisite Resolution**: Topologically sort skills by dependencies
3. **Resource Matching**: Find optimal learning materials
4. **Timeline Estimation**: Calculate realistic completion dates

## 📝 TODO: Implementation Roadmap

### High Priority

- [ ] **Progress Tracking Service**
  - Track learning activities in real-time
  - Calculate proficiency boosts after completing resources
  - Implement skill decay algorithm

- [ ] **Content Discovery Service**
  - Scrape learning resources from Coursera, Udemy, etc.
  - Store in MongoDB
  - Generate embeddings for semantic search

- [ ] **REST API Endpoints**
  - `/v1/goals` - CRUD for goals
  - `/v1/learning-paths` - CRUD and generation
  - `/v1/resources` - Browse and search
  - `/v1/skills` - Query user's skills
  - `/v1/progress` - Get analytics and reports

### Medium Priority

- [ ] **GraphQL API**
  - Complete schema definition
  - Implement resolvers
  - Add DataLoader for N+1 prevention

- [ ] **Intervention System**
  - Risk detection (disengagement, struggle)
  - Message generation
  - Notification delivery

- [ ] **Background Jobs**
  - Daily content scraper
  - Weekly knowledge twin update
  - Skill decay calculator
  - Intervention detector

### Low Priority

- [ ] **Testing**
  - Unit tests for all services (Jest)
  - Integration tests for API endpoints
  - E2E tests for critical flows

- [ ] **Frontend Application**
  - React dashboard
  - Knowledge graph visualization (D3.js/Cytoscape)
  - Learning interface

- [ ] **Additional Features**
  - GitHub integration for code analysis
  - LinkedIn profile import
  - Conversational knowledge extraction
  - Assessment system

## 🔒 Security

- **Authentication**: JWT-based with bcrypt password hashing
- **Authorization**: Resource-level access control
- **Input Validation**: Zod schemas for all API inputs
- **SQL Injection**: Parameterized queries only
- **Rate Limiting**: To be implemented
- **HTTPS**: Required in production
- **Secrets**: Environment variables, never committed

## 📊 Database Schemas

### PostgreSQL Tables

- `users` - User accounts and authentication
- `user_profiles` - User preferences and settings
- `goals` - Learning goals
- `learning_paths` - Generated learning paths
- `path_steps` - Individual steps in paths
- `skill_progress` - User skill proficiency tracking
- `learning_activities` - Event log of all activities
- `assessments` - Skill assessments
- `assessment_attempts` - User assessment results
- `interventions` - Support interventions
- `notifications` - User notifications
- `weekly_reports` - Progress reports

### Neo4j Graph

See `src/db/neo4j/schema.cypher` for complete schema with sample data.

### MongoDB Collections

- `resources` - Scraped learning content
- `raw_scrapes` - Raw scraping data (TTL 30 days)
- `user_documents` - User-uploaded files

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Write tests
4. Submit a pull request

See `CLAUDE.md` for detailed development guidelines.

## 📄 License

MIT License - See LICENSE file for details

## 📧 Support

- **Issues**: Use GitHub issues for bug reports
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: See `/docs` folder

## 🙏 Acknowledgments

- Built with Claude (Anthropic) for AI-powered knowledge extraction
- Neo4j for knowledge graph database
- Express.js and TypeScript for robust backend

---

**Status**: 🚧 **Active Development** 🚧

Core services implemented:
- ✅ Authentication & Authorization
- ✅ Knowledge Extraction (Resume → Skills)
- ✅ Learning Path Generation
- ✅ Database connections (PostgreSQL, Neo4j, MongoDB, Redis)

Next steps:
- Implement Progress Tracking Service
- Build remaining API endpoints
- Add Content Discovery & Scraping
- Implement Intervention System
- Add comprehensive testing

**Last Updated**: November 2025
