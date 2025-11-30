# Technical Architecture

## System overview
The platform ingests learner data, builds a knowledge graph across multiple datastores, and exposes services for recommendations and progress tracking. The current implementation centers on TypeScript/Node.js services with modular data connectors.

## Components
- **API layer (Express REST)**: Routes in `src/api/rest` provide authentication and initial learning-path endpoints; GraphQL schema is planned for richer queries.
- **Service layer**: Knowledge extraction and learning-path generation live under `src/services`, with placeholders for progress tracking, content discovery, and intervention logic.
- **Data layer**:
  - PostgreSQL for relational entities (users, goals, progress).
  - Neo4j for the knowledge graph (skills, relationships, learning paths).
  - MongoDB for unstructured resource content.
  - Redis for caching, session state, and future queues.
- **Background jobs**: Airflow/BullMQ are planned for ingestion, scraping, and periodic twin updates (see `src/jobs`).
- **AI/ML integrations**: Claude and OpenAI GPT APIs power NLP and recommendation logic; Pinecone is targeted for vector search.

## Environment & operations
- **Local runtime**: `npm run dev` with Docker Compose services for databases.
- **Configuration**: `.env` file seeded from `.env.example`; secrets should never be committed.
- **Observability**: Logging utilities in `src/utils/logger.ts` with structured logs; expand with metrics/tracing as services mature.
- **Security**: JWT-based auth middleware in `src/api/middleware/auth.ts`; enforce HTTPS/secret rotation in production.

## Data flows (high level)
1. Ingest profile/resume data via API and conversations.
2. Extract entities/skills using Claude/OpenAI and normalize with spaCy (planned).
3. Write learner profile to PostgreSQL and update the knowledge graph in Neo4j.
4. Generate learning paths based on gaps and prerequisites; persist and expose via REST/GraphQL.
5. Track progress events, update proficiencies, and trigger interventions (planned).

## Roadmap for improvements
- Finalize REST endpoints for goals, learning paths, resources, skills, and progress.
- Add GraphQL schema/resolvers with DataLoader for efficient graph access.
- Stand up background jobs for scraping, twin refresh, and skill decay calculations.
- Integrate Pinecone or similar for embedding-based resource search.
- Expand observability (metrics, tracing) and harden security (rate limits, audits).
