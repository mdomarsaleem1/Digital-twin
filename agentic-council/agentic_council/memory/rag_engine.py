"""RAG engine for case study retrieval."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class CaseStudy:
    """A business case study for reference."""
    id: str
    title: str
    company: str
    year: int
    industry: str
    outcome: str  # "success", "failure", "mixed"
    summary: str
    key_factors: list[str]
    lessons_learned: list[str]
    financial_metrics: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    source_url: str = ""
    embedding: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "year": self.year,
            "industry": self.industry,
            "outcome": self.outcome,
            "summary": self.summary,
            "key_factors": self.key_factors,
            "lessons_learned": self.lessons_learned,
            "financial_metrics": self.financial_metrics,
            "tags": self.tags,
            "source_url": self.source_url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CaseStudy":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            company=data["company"],
            year=data["year"],
            industry=data["industry"],
            outcome=data["outcome"],
            summary=data["summary"],
            key_factors=data.get("key_factors", []),
            lessons_learned=data.get("lessons_learned", []),
            financial_metrics=data.get("financial_metrics", {}),
            tags=data.get("tags", []),
            source_url=data.get("source_url", ""),
        )


@dataclass
class RAGConfig:
    """Configuration for RAG engine."""
    collection_name: str = "case_studies"
    embedding_model: str = "text-embedding-3-small"
    top_k: int = 5
    similarity_threshold: float = 0.7
    db_path: str = "data/case_studies.db"


class RAGEngine:
    """RAG engine for retrieving relevant case studies."""

    def __init__(self, config: RAGConfig | None = None):
        """Initialize RAG engine.

        Args:
            config: RAG configuration
        """
        self.config = config or RAGConfig()
        self._case_studies: dict[str, CaseStudy] = {}
        self._initialized = False

        # Load seed data
        self._load_seed_data()

    def _load_seed_data(self) -> None:
        """Load seed case studies."""
        seed_cases = self._get_seed_cases()
        for case in seed_cases:
            self._case_studies[case.id] = case

        logger.info(
            "RAG engine initialized",
            case_count=len(self._case_studies),
        )
        self._initialized = True

    def _get_seed_cases(self) -> list[CaseStudy]:
        """Get seed case studies for the system."""
        return [
            CaseStudy(
                id="spotify_2008",
                title="Spotify - Music Streaming Revolution",
                company="Spotify",
                year=2008,
                industry="music_streaming",
                outcome="success",
                summary="""Spotify launched in 2008 as a legal alternative to music piracy,
                offering freemium streaming. Despite skepticism about unit economics and
                licensing costs, they grew to dominate streaming through mobile-first
                strategy and playlist curation.""",
                key_factors=[
                    "Freemium model drove viral adoption",
                    "Mobile-first approach aligned with smartphone growth",
                    "Playlist curation created new discovery paradigm",
                    "Licensing deals with major labels secured content",
                    "Data-driven personalization improved engagement",
                ],
                lessons_learned=[
                    "Market timing with smartphone adoption was crucial",
                    "Free tier as acquisition channel justified high CAC",
                    "Platform power increased as catalog grew",
                    "Creator relationships require continuous investment",
                ],
                financial_metrics={
                    "valuation_2024": "$70B",
                    "time_to_profitability": "15 years",
                    "peak_growth_rate": "30% YoY",
                },
                tags=["music", "streaming", "freemium", "marketplace", "mobile"],
            ),
            CaseStudy(
                id="blue_apron_2012",
                title="Blue Apron - Meal Kit Cautionary Tale",
                company="Blue Apron",
                year=2012,
                industry="food_delivery",
                outcome="failure",
                summary="""Blue Apron pioneered meal kit delivery, reaching $2B valuation
                at IPO. However, high CAC ($94/customer), low retention (60% churned within
                6 months), and intense competition led to 90% value destruction post-IPO.""",
                key_factors=[
                    "First mover advantage in meal kits",
                    "High customer acquisition cost ($94+)",
                    "Low retention due to subscription fatigue",
                    "Operational complexity in perishable logistics",
                    "Competition from Amazon, HelloFresh intensified",
                ],
                lessons_learned=[
                    "First mover advantage doesn't guarantee success",
                    "Unit economics must work before scaling",
                    "Subscription businesses need strong retention",
                    "Physical products face operational challenges",
                    "Deep-pocketed competitors can erode margins",
                ],
                financial_metrics={
                    "peak_valuation": "$2B",
                    "current_valuation": "$200M",
                    "cac": "$94",
                    "6_month_churn": "60%",
                },
                tags=["food", "subscription", "logistics", "d2c", "operations"],
            ),
            CaseStudy(
                id="rdio_2010",
                title="Rdio - The Streaming Service That Wasn't",
                company="Rdio",
                year=2010,
                industry="music_streaming",
                outcome="failure",
                summary="""Rdio launched in 2010 with better UX than Spotify but couldn't
                compete on scale. Delayed mobile launch, premium-only model, and
                insufficient funding led to bankruptcy in 2015 despite loyal user base.""",
                key_factors=[
                    "Superior product design and UX",
                    "No free tier limited viral growth",
                    "Late to mobile platform",
                    "Insufficient funding vs. Spotify",
                    "Licensing costs same as larger competitors",
                ],
                lessons_learned=[
                    "Better product doesn't guarantee market win",
                    "Network effects favor scale over quality",
                    "Timing of platform shifts (mobile) is critical",
                    "Capital efficiency matters less than capital availability",
                ],
                financial_metrics={
                    "total_funding": "$125M",
                    "peak_subscribers": "3M",
                    "years_active": "5",
                },
                tags=["music", "streaming", "premium", "ux", "timing"],
            ),
            CaseStudy(
                id="webflow_2013",
                title="Webflow - No-Code Design Platform Success",
                company="Webflow",
                year=2013,
                industry="no_code",
                outcome="success",
                summary="""Webflow started as a visual web design tool, pivoting to
                become a complete CMS and hosting platform. Designer-focused positioning,
                strong community, and education-led growth led to $4B valuation.""",
                key_factors=[
                    "Designer-focused niche positioning",
                    "Education as growth engine (Webflow University)",
                    "Community-driven development",
                    "Land and expand with agencies",
                    "Vertical integration (design + CMS + hosting)",
                ],
                lessons_learned=[
                    "Niche positioning can lead to large markets",
                    "Education creates loyal customers",
                    "Community amplifies product development",
                    "Prosumer tools can scale to enterprise",
                ],
                financial_metrics={
                    "valuation_2024": "$4B+",
                    "time_to_series_a": "4 years (bootstrapped first)",
                    "growth_rate": "100%+ YoY",
                },
                tags=["no_code", "design", "saas", "community", "education"],
            ),
            CaseStudy(
                id="hopin_2019",
                title="Hopin - Virtual Events Boom and Bust",
                company="Hopin",
                year=2019,
                industry="virtual_events",
                outcome="failure",
                summary="""Hopin raised $1B+ during COVID-19, reaching $7.75B valuation
                for virtual events platform. Post-pandemic, demand collapsed as in-person
                events returned. 90% valuation drop and massive layoffs followed.""",
                key_factors=[
                    "Perfect timing with COVID-19 lockdowns",
                    "Rapid scaling through M&A",
                    "High growth masked retention issues",
                    "Product wasn't differentiated for hybrid future",
                    "Over-raised at peak euphoria",
                ],
                lessons_learned=[
                    "Distinguish trends from sustainable demand",
                    "Exogenous tailwinds can reverse quickly",
                    "M&A speed doesn't equal integration success",
                    "Capital abundance can mask business flaws",
                ],
                financial_metrics={
                    "peak_valuation": "$7.75B",
                    "current_valuation": "<$500M",
                    "total_raised": "$1B+",
                    "peak_employees": "800",
                },
                tags=["events", "covid", "remote", "saas", "timing"],
            ),
            CaseStudy(
                id="bird_2017",
                title="Bird - Electric Scooter Hype Cycle",
                company="Bird",
                year=2017,
                industry="micromobility",
                outcome="mixed",
                summary="""Bird pioneered electric scooter sharing, becoming fastest
                company to unicorn status. Operational challenges (vandalism, regulations,
                unit economics) led to bankruptcy and acquisition at fraction of peak value.""",
                key_factors=[
                    "Solved last-mile transportation problem",
                    "Capital-intensive hardware business",
                    "Regulatory challenges in every city",
                    "Vandalism and maintenance costs",
                    "Race to scale with competitors",
                ],
                lessons_learned=[
                    "Hardware businesses have different economics than software",
                    "City-by-city regulation creates fragmented markets",
                    "Physical assets face depreciation and damage",
                    "Fastest to market ≠ best positioned",
                ],
                financial_metrics={
                    "peak_valuation": "$2.5B",
                    "acquisition_price": "~$30M",
                    "scooter_lifespan": "1-3 months initially",
                },
                tags=["mobility", "hardware", "last_mile", "regulation", "operations"],
            ),
            CaseStudy(
                id="slack_2009",
                title="Slack - Enterprise Communication Revolution",
                company="Slack",
                year=2009,
                industry="enterprise_software",
                outcome="success",
                summary="""Slack emerged from a failed gaming company, pivoting internal
                chat tool into $27B enterprise platform. Bottom-up adoption, integrations
                ecosystem, and viral team-by-team spread drove unprecedented growth.""",
                key_factors=[
                    "Pivot from gaming failure (Glitch)",
                    "Bottom-up enterprise adoption",
                    "Integration ecosystem created platform lock-in",
                    "Freemium drove viral team adoption",
                    "Superior search and organization vs. email",
                ],
                lessons_learned=[
                    "Failed products can spawn successful pivots",
                    "Bottom-up can beat top-down in enterprise",
                    "Integrations create platform value",
                    "Communication tools benefit from network effects",
                ],
                financial_metrics={
                    "acquisition_price": "$27.7B (by Salesforce)",
                    "time_to_unicorn": "2 years",
                    "daily_active_users_at_exit": "12M+",
                },
                tags=["enterprise", "saas", "communication", "pivot", "platform"],
            ),
            CaseStudy(
                id="theranos_2003",
                title="Theranos - Healthcare Fraud Lessons",
                company="Theranos",
                year=2003,
                industry="healthcare",
                outcome="failure",
                summary="""Theranos promised revolutionary blood testing technology that
                didn't exist. Despite $9B valuation and elite board, fundamental technology
                claims were fraudulent, leading to criminal convictions and total collapse.""",
                key_factors=[
                    "Technology claims were fundamentally false",
                    "Regulatory shortcuts bypassed validation",
                    "Prestigious board provided false credibility",
                    "Secrecy prevented technical scrutiny",
                    "Healthcare requires rigorous validation",
                ],
                lessons_learned=[
                    "Due diligence must verify core technology claims",
                    "Prestigious boards don't guarantee legitimacy",
                    "Healthcare has mandatory regulatory requirements",
                    "Secrecy about core product is a red flag",
                ],
                financial_metrics={
                    "peak_valuation": "$9B",
                    "total_fraud": "$700M+",
                    "years_of_deception": "15",
                },
                tags=["healthcare", "fraud", "deeptech", "due_diligence", "regulation"],
            ),
        ]

    async def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        top_k: int | None = None,
    ) -> list[CaseStudy]:
        """Search for relevant case studies.

        Args:
            query: Search query (idea description)
            filters: Optional filters (industry, outcome, year range)
            top_k: Number of results to return

        Returns:
            List of relevant case studies
        """
        top_k = top_k or self.config.top_k

        # Extract keywords from query for matching
        keywords = self._extract_keywords(query)

        # Score all case studies
        scored = []
        for case in self._case_studies.values():
            # Apply filters
            if filters:
                if not self._matches_filters(case, filters):
                    continue

            # Calculate relevance score
            score = self._calculate_relevance(case, keywords, query)
            if score > 0:
                scored.append((score, case))

        # Sort by score and return top_k
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [case for _, case in scored[:top_k]]

        logger.debug(
            "RAG search completed",
            query_preview=query[:50],
            results_count=len(results),
        )

        return results

    def _extract_keywords(self, query: str) -> set[str]:
        """Extract keywords from query."""
        # Simple keyword extraction - could use NLP for better results
        stopwords = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all",
            "each", "every", "both", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same",
            "so", "than", "too", "very", "just", "and", "but", "or",
            "if", "because", "until", "while", "although", "though",
            "even", "what", "which", "who", "whom", "this", "that",
            "these", "those", "i", "me", "my", "myself", "we", "our",
            "ours", "ourselves", "you", "your", "yours", "yourself",
            "he", "him", "his", "himself", "she", "her", "hers",
            "herself", "it", "its", "itself", "they", "them", "their",
        }

        words = query.lower().replace(",", " ").replace(".", " ").split()
        keywords = {w for w in words if w not in stopwords and len(w) > 2}

        return keywords

    def _matches_filters(self, case: CaseStudy, filters: dict[str, Any]) -> bool:
        """Check if case matches filters."""
        if "industry" in filters:
            if case.industry != filters["industry"]:
                return False

        if "outcome" in filters:
            if case.outcome != filters["outcome"]:
                return False

        if "year_min" in filters:
            if case.year < filters["year_min"]:
                return False

        if "year_max" in filters:
            if case.year > filters["year_max"]:
                return False

        return True

    def _calculate_relevance(
        self,
        case: CaseStudy,
        keywords: set[str],
        query: str,
    ) -> float:
        """Calculate relevance score for a case study."""
        score = 0.0

        # Tag matching (highest weight)
        tag_matches = sum(1 for tag in case.tags if tag in keywords)
        score += tag_matches * 3.0

        # Industry matching
        if case.industry.replace("_", " ") in query.lower():
            score += 5.0

        # Summary keyword matching
        summary_lower = case.summary.lower()
        summary_matches = sum(1 for kw in keywords if kw in summary_lower)
        score += summary_matches * 1.0

        # Key factors matching
        factors_text = " ".join(case.key_factors).lower()
        factor_matches = sum(1 for kw in keywords if kw in factors_text)
        score += factor_matches * 1.5

        # Title/company matching
        if case.company.lower() in query.lower():
            score += 10.0

        return score

    async def get_similar_cases(
        self,
        idea: str,
        include_failures: bool = True,
        include_successes: bool = True,
    ) -> dict[str, list[CaseStudy]]:
        """Get similar cases grouped by outcome.

        Args:
            idea: The business idea
            include_failures: Include failure cases
            include_successes: Include success cases

        Returns:
            Dictionary with "successes" and "failures" lists
        """
        all_cases = await self.search(idea, top_k=10)

        result = {
            "successes": [],
            "failures": [],
            "mixed": [],
        }

        for case in all_cases:
            if case.outcome == "success" and include_successes:
                result["successes"].append(case)
            elif case.outcome == "failure" and include_failures:
                result["failures"].append(case)
            elif case.outcome == "mixed":
                result["mixed"].append(case)

        return result

    def add_case_study(self, case: CaseStudy) -> None:
        """Add a new case study to the database.

        Args:
            case: The case study to add
        """
        self._case_studies[case.id] = case
        logger.info("Case study added", case_id=case.id, company=case.company)

    def get_case_by_id(self, case_id: str) -> CaseStudy | None:
        """Get a specific case study by ID."""
        return self._case_studies.get(case_id)

    def list_all_cases(self) -> list[CaseStudy]:
        """List all case studies."""
        return list(self._case_studies.values())

    def format_for_prompt(self, cases: list[CaseStudy]) -> str:
        """Format case studies for inclusion in LLM prompts.

        Args:
            cases: List of case studies to format

        Returns:
            Formatted string for prompts
        """
        if not cases:
            return "No relevant case studies found."

        lines = ["Relevant Case Studies:\n"]

        for case in cases:
            outcome_emoji = {
                "success": "+",
                "failure": "-",
                "mixed": "~",
            }.get(case.outcome, "?")

            lines.append(f"[{outcome_emoji}] {case.company} ({case.year}) - {case.title}")
            lines.append(f"   {case.summary[:200]}...")
            lines.append(f"   Key lessons: {', '.join(case.lessons_learned[:2])}")
            lines.append("")

        return "\n".join(lines)
