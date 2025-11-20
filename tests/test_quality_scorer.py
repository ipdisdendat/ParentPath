"""Tests for quality scoring system"""
import pytest


def calculate_quality_score(item):
    """
    Calculate quality score for an item

    Factors:
    - Confidence score from Gemini (40%)
    - Completeness of fields (30%)
    - Source snippet quality (20%)
    - Audience tag specificity (10%)
    """
    score = 0.0

    # Confidence score (40%)
    confidence = item.get("confidence_score", 0.0)
    score += confidence * 0.4

    # Completeness (30%)
    required_fields = ["type", "title", "date", "audience_tags", "source_snippet"]
    optional_fields = ["description", "time", "location", "deadline", "cost"]

    required_count = sum(1 for field in required_fields if item.get(field))
    optional_count = sum(1 for field in optional_fields if item.get(field))

    completeness = (required_count / len(required_fields)) * 0.6 + (optional_count / len(optional_fields)) * 0.4
    score += completeness * 0.3

    # Source snippet quality (20%)
    snippet = item.get("source_snippet", "")
    snippet_quality = min(len(snippet) / 100, 1.0)  # Normalize to 100 chars
    score += snippet_quality * 0.2

    # Audience tag specificity (10%)
    tags = item.get("audience_tags", [])
    tag_quality = 0.5 if "all" in tags else 1.0  # Specific tags score higher
    tag_quality *= min(len(tags) / 2, 1.0)  # Multiple tags better
    score += tag_quality * 0.1

    return score


@pytest.mark.asyncio
async def test_high_quality_item_scores_high():
    """Test high quality item gets high score"""
    high_quality_item = {
        "type": "Event",
        "title": "Basketball practice",
        "description": "Weekly practice session for Grade 5 team",
        "date": "2024-11-20",
        "time": "16:00",
        "location": "School gymnasium",
        "audience_tags": ["grade_5", "Basketball"],
        "source_page": 3,
        "source_snippet": "Join us for Basketball practice on November 20th at 4pm in the school gym. All Grade 5 players required to attend.",
        "confidence_score": 0.95,
        "reasoning": ""
    }

    score = calculate_quality_score(high_quality_item)

    assert score > 0.85, f"High quality item should score >0.85, got {score}"


@pytest.mark.asyncio
async def test_low_quality_item_scores_low():
    """Test low quality item gets low score"""
    low_quality_item = {
        "type": "Event",
        "title": "Something happening",
        "date": "2024-11-20",
        "audience_tags": ["all"],
        "source_snippet": "Event",
        "confidence_score": 0.50,
        "reasoning": "Unclear information in newsletter"
    }

    score = calculate_quality_score(low_quality_item)

    assert score < 0.60, f"Low quality item should score <0.60, got {score}"


@pytest.mark.asyncio
async def test_missing_fields_reduce_score():
    """Test missing optional fields reduce score"""
    complete_item = {
        "type": "Event",
        "title": "Basketball practice",
        "description": "Weekly practice",
        "date": "2024-11-20",
        "time": "16:00",
        "location": "Gym",
        "audience_tags": ["grade_5"],
        "source_snippet": "Basketball practice Nov 20 at 4pm in gym",
        "confidence_score": 0.95
    }

    incomplete_item = {
        "type": "Event",
        "title": "Basketball practice",
        "date": "2024-11-20",
        "audience_tags": ["grade_5"],
        "source_snippet": "Basketball Nov 20",
        "confidence_score": 0.95
    }

    complete_score = calculate_quality_score(complete_item)
    incomplete_score = calculate_quality_score(incomplete_item)

    assert complete_score > incomplete_score, "Complete item should score higher"
    assert (complete_score - incomplete_score) > 0.1, "Difference should be significant"
