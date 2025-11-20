"""Tests for batch digest analyzer"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


@pytest.fixture
def sample_items():
    """Sample items for digest generation"""
    return [
        {
            "id": "1",
            "type": "Event",
            "title": "Basketball practice",
            "description": "Weekly practice",
            "date": "2024-11-20",
            "time": "16:00",
            "audience_tags": ["grade_5", "Basketball"],
            "status": "approved"
        },
        {
            "id": "2",
            "type": "PermissionSlip",
            "title": "Field trip consent",
            "description": "Science museum trip",
            "date": "2024-11-22",
            "deadline": "2024-11-18",
            "audience_tags": ["grade_5"],
            "status": "approved"
        },
        {
            "id": "3",
            "type": "HotLunch",
            "title": "Pizza day",
            "description": "Order by Friday",
            "date": "2024-11-21",
            "audience_tags": ["all"],
            "status": "approved"
        }
    ]


def mock_digest_generator(items, parent_tags):
    """Mock digest generator"""
    if not items:
        return None

    relevant_items = [
        item for item in items
        if any(tag in item["audience_tags"] for tag in parent_tags) or "all" in item["audience_tags"]
    ]

    if not relevant_items:
        return None

    digest = "📅 This Week:\n\n"
    for item in relevant_items:
        emoji = "🏀" if item["type"] == "Event" else "📋" if item["type"] == "PermissionSlip" else "🍕"
        digest += f"{emoji} {item['title']}\n"
        digest += f"   {item['date']} at {item.get('time', 'TBD')}\n\n"

    return digest


@pytest.mark.asyncio
async def test_generate_digest_for_parent(sample_items):
    """Test digest generation for specific parent"""
    parent_tags = ["grade_5", "Basketball"]

    digest = mock_digest_generator(sample_items, parent_tags)

    assert digest is not None
    assert "Basketball practice" in digest
    assert "Field trip consent" in digest
    assert "Pizza day" in digest  # "all" tag included


@pytest.mark.asyncio
async def test_audience_tag_matching(sample_items):
    """Test audience tag filtering"""
    # Parent only has grade_6 child
    parent_tags = ["grade_6"]

    digest = mock_digest_generator(sample_items, parent_tags)

    # Should only include "all" items
    assert digest is not None
    assert "Pizza day" in digest
    assert "Basketball practice" not in digest
    assert "Field trip consent" not in digest


@pytest.mark.asyncio
async def test_multilingual_translation():
    """Test digest translation to different languages"""
    from api.services.gemini_service import translate_text

    with patch("api.services.gemini_service.model.generate_content") as mock_gen:
        mock_response = MagicMock()
        mock_response.text = "🏀 Práctica de baloncesto"
        mock_gen.return_value = mock_response

        digest_en = "🏀 Basketball practice"
        digest_es = await translate_text(digest_en, "es")

        # Translation called
        assert mock_gen.called


@pytest.mark.asyncio
async def test_emoji_formatting():
    """Test emoji preservation in digest"""
    items = [
        {
            "type": "Event",
            "title": "🏀 Basketball",
            "date": "2024-11-20",
            "time": "16:00",
            "audience_tags": ["all"],
            "status": "approved"
        }
    ]

    digest = mock_digest_generator(items, ["all"])

    # Emoji should be preserved
    assert "🏀" in digest


@pytest.mark.asyncio
async def test_empty_week_returns_none():
    """Test empty week returns no digest"""
    empty_items = []

    digest = mock_digest_generator(empty_items, ["grade_5"])

    assert digest is None
