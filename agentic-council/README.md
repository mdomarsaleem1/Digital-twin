# Agentic Council System

A multi-agent AI council for evaluating business ideas through structured debate and consensus building.

## Overview

The Agentic Council is a sophisticated multi-agent system that simulates a C-suite executive council to evaluate business ideas. It leverages multiple LLM agents with specialized personas to provide comprehensive analysis from different perspectives.

### Key Features

- **Multi-Agent Debate**: 6 specialist agents (CFO, CPO, CTO, CMO, CSO, CHRO) + Devil's Advocate
- **3-Phase Deliberation**: Parallel Assessment -> Structured Debate -> Consensus Building
- **Time-Boxed Execution**: 15-minute hard stop with phase-specific limits
- **Weighted Voting**: Domain-specific expertise weights and confidence scoring
- **Historical Backtesting**: Validate predictions against known outcomes (2008-2020)
- **Case Study RAG**: Reference relevant business cases during evaluation

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │           ORCHESTRATOR              │
                    │     (Claude Opus - Moderator)       │
                    └─────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        ▼                            ▼                            ▼
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│   FINANCE    │          │   PRODUCT    │          │  ENGINEERING │
│ (Gemini 2.0) │          │ (Gemini 2.0) │          │ (Gemini 2.0) │
└──────────────┘          └──────────────┘          └──────────────┘
        ▼                            ▼                            ▼
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│  MARKETING   │          │   STRATEGY   │          │      HR      │
│ (Gemini 2.0) │          │ (Gemini 2.0) │          │ (Gemini 2.0) │
└──────────────┘          └──────────────┘          └──────────────┘
                                     │
                    ┌─────────────────────────────────────┐
                    │       DEVIL'S ADVOCATE              │
                    │         (Gemini Pro)                │
                    │    Challenges consensus             │
                    └─────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key (for Claude)
- Google AI API key (for Gemini)

### Installation

```bash
# Clone the repository
cd Digital-twin/agentic-council

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Running the API Server

```bash
# Start the FastAPI server
uvicorn agentic_council.api.server:app --host 0.0.0.0 --port 8000

# Or with hot reload for development
uvicorn agentic_council.api.server:app --reload
```

### Running the Dashboard

```bash
streamlit run agentic_council/dashboard/app.py
```

### Using Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## API Usage

### Evaluate a Business Idea

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A mobile app that uses AI to recommend personalized workout routines based on user fitness level and goals",
    "context": {
      "industry": "fitness",
      "target_users": "millennials and gen-z",
      "budget": "$500K seed"
    },
    "risk_appetite": "moderate"
  }'
```

### Run Historical Backtests

```bash
curl -X POST http://localhost:8000/backtest \
  -H "Content-Type: application/json" \
  -d '{"run_all": true}'
```

### Check Health

```bash
curl http://localhost:8000/health
```

## Python Usage

```python
import asyncio
from agentic_council import AgenticCouncil
from agentic_council.orchestration.council import CouncilConfig

async def evaluate_idea():
    # Create council with default configuration
    council = AgenticCouncil()

    # Evaluate an idea
    session = await council.evaluate(
        idea="A subscription service for personalized vitamin packs",
        context={
            "industry": "health",
            "market_size": "$50B",
            "competition": "high"
        }
    )

    # Access results
    print(f"Recommendation: {session.final_consensus.recommendation}")
    print(f"Confidence: {session.final_consensus.confidence:.0%}")
    print(f"Key Drivers: {session.final_consensus.key_drivers}")
    print(f"Major Risks: {session.final_consensus.major_risks}")

asyncio.run(evaluate_idea())
```

## Configuration

### Time Configuration

```yaml
# config/orchestration.yaml
debate:
  total_time_seconds: 900  # 15 minutes
  phases:
    parallel_assessment:
      duration_seconds: 300  # 5 minutes
    structured_debate:
      duration_seconds: 420  # 7 minutes
    consensus_building:
      duration_seconds: 180  # 3 minutes
```

### Risk Appetite

- **Conservative**: Emphasizes risks, requires higher confidence for GO
- **Moderate**: Balanced risk-reward assessment
- **Aggressive**: Emphasizes opportunities, accepts more risk

## Historical Test Cases

The system includes 5 historical test cases for backtesting:

| Test | Year | Outcome | Company |
|------|------|---------|---------|
| spotify_2008 | 2008 | SUCCESS | Spotify |
| blue_apron_2012 | 2012 | FAILURE | Blue Apron |
| bird_2017 | 2017 | FAILURE | Bird |
| webflow_2017 | 2017 | SUCCESS | Webflow |
| hopin_2020 | 2020 | FAILURE | Hopin |

## Project Structure

```
agentic-council/
├── agentic_council/
│   ├── agents/           # Agent implementations
│   ├── api/              # FastAPI endpoints
│   ├── dashboard/        # Streamlit dashboard
│   ├── evaluation/       # Backtesting framework
│   ├── memory/           # RAG and conversation buffer
│   ├── models/           # LLM adapters
│   └── orchestration/    # Core orchestration logic
├── config/               # Configuration files
├── data/                 # Local data storage
├── tests/                # Test suites
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black agentic_council/
ruff check agentic_council/
```

### Type Checking

```bash
mypy agentic_council/
```

## License

MIT License - See LICENSE file for details.
