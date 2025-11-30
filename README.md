# Digital Knowledge Twin Platform

The Digital Knowledge Twin Platform builds a dynamic profile of a learner's skills and goals to curate personalized growth plans.

## What this project delivers
- Personalized knowledge graph that reflects each learner's skills, gaps, and goals.
- AI-powered recommendations for learning paths and resources.
- Pluggable data sources and APIs for integrating with existing learning workflows.

## Quick start
1. Install dependencies: `npm install`
2. Copy environment template: `cp .env.example .env` and add your keys.
3. Start services: `docker-compose up -d`
4. Run the API locally: `npm run dev` (available at `http://localhost:3000`)

## Documentation
- [Technical architecture](docs/technical.md)
- [Business overview](docs/business.md)

## Status
The platform includes initial services for knowledge extraction and learning-path generation; additional API endpoints, background jobs, and analytics are planned.
