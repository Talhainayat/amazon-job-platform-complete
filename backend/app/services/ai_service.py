"""
Modular, optional AI service.

The application must NEVER depend on this for core functionality --
the rule-based matcher in app/services/matching.py always works standalone.
This service only ever *augments* results when AI_API_KEY is configured.

Possible future operations (not implemented yet, intentionally):
- analyze_job_description(description) -> structured tags
- analyze_candidate_preferences(candidate) -> structured preferences
- improve_match_score(candidate, job, rule_based_result) -> adjusted score
- explain_match(candidate, job, rule_based_result) -> human-readable explanation
"""
from app.core.config import settings


def is_ai_enabled() -> bool:
    return bool(settings.AI_API_KEY) and settings.AI_PROVIDER != "none"


def explain_match(candidate, job, rule_based_result) -> str:
    """
    Returns a human-readable explanation of a match.

    Falls back to a simple templated explanation built from the
    rule-based result when no AI provider is configured, so callers
    never have to special-case "AI unavailable".
    """
    if not is_ai_enabled():
        matched = ", ".join(rule_based_result.matched_criteria.keys()) or "none"
        return f"Matched on: {matched}. Score: {rule_based_result.score}/100 (rule-based)."

    # Placeholder for a real AI provider call once AI_PROVIDER/AI_API_KEY
    # are configured. Intentionally not implemented in this milestone.
    matched = ", ".join(rule_based_result.matched_criteria.keys()) or "none"
    return f"Matched on: {matched}. Score: {rule_based_result.score}/100 (AI explanation not yet implemented)."
