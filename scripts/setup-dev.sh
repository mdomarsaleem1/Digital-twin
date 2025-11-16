#!/bin/bash

# Digital Knowledge Twin Platform - Development Setup Script

echo "🚀 Setting up Digital Knowledge Twin Platform..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys before continuing!"
    exit 1
fi

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Run PostgreSQL migrations
echo "🗄️  Running PostgreSQL migrations..."
if command -v psql &> /dev/null; then
    PGPASSWORD=postgres psql -h localhost -U postgres -d knowledge_twin -f src/db/postgresql/schema.sql
    echo "✅ PostgreSQL schema created"
else
    echo "⚠️  psql not found. Please run PostgreSQL migrations manually:"
    echo "   psql -h localhost -U postgres -d knowledge_twin -f src/db/postgresql/schema.sql"
fi

# Run Neo4j migrations
echo "📊 Running Neo4j schema setup..."
if command -v cypher-shell &> /dev/null; then
    cypher-shell -u neo4j -p neo4jpassword -f src/db/neo4j/schema.cypher
    echo "✅ Neo4j schema created"
else
    echo "⚠️  cypher-shell not found. Please run Neo4j migrations manually:"
    echo "   cypher-shell -u neo4j -p neo4jpassword -f src/db/neo4j/schema.cypher"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure you've added your API keys to .env file"
echo "2. Run 'npm run dev' to start the development server"
echo "3. Access the API at http://localhost:3000"
echo "4. Check health at http://localhost:3000/health"
echo ""
echo "Database URLs:"
echo "- Neo4j Browser: http://localhost:7474"
echo "- PostgreSQL: localhost:5432"
echo "- MongoDB: localhost:27017"
echo "- Redis: localhost:6379"
echo ""
