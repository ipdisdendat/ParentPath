"""Tests for Gemini AI service"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from api.services.gemini_service import (
    parse_pdf_newsletter,
    generate_embedding,
    translate_text,
    generate_answer,
    parse_image_flyer
)


@pytest.mark.asyncio
async def test_parse_pdf_extracts_items(mock_gemini):
    """Test PDF parsing extracts structured items"""
    items = await parse_pdf_newsletter("test.pdf")

    assert isinstance(items, list)
    assert len(items) > 0
    assert items[0]["type"] in ["Event", "PermissionSlip", "Fundraiser", "HotLunch", "Announcement"]
    assert "title" in items[0]
    assert "audience_tags" in items[0]


@pytest.mark.asyncio
async def test_confidence_scores_valid(mock_gemini):
    """Test confidence scores are in valid range"""
    items = await parse_pdf_newsletter("test.pdf")

    for item in items:
        assert "confidence_score" in item
        score = item["confidence_score"]
        assert 0.0 <= score <= 1.0, f"Confidence score {score} out of range"


@pytest.mark.asyncio
async def test_embedding_dimension_768(mock_gemini):
    """Test embeddings are 768-dimensional"""
    embedding = await generate_embedding("Basketball practice on Nov 20")

    assert isinstance(embedding, list)
    assert len(embedding) == 768
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_translation_preserves_emojis(mock_gemini):
    """Test translation preserves emoji formatting"""
    text_with_emoji = "🏀 Basketball practice today at 4pm"

    translated = await translate_text(text_with_emoji, "es")

    # Mock returns original, but verify structure
    assert "🏀" in translated or text_with_emoji == translated


@pytest.mark.asyncio
@pytest.mark.skipif(True, reason="CLI mode requires gemini CLI installed")
async def test_cli_mode_works():
    """Test CLI mode for Gemini (free tier)"""
    # This test would require actual CLI setup
    # Skipped in automated tests
    pass


@pytest.mark.asyncio
async def test_api_mode_works(mock_gemini):
    """Test API mode for Gemini"""
    items = await parse_pdf_newsletter("test.pdf")

    # Verify API mode called correctly
    assert len(items) > 0


@pytest.mark.asyncio
async def test_low_confidence_flagged(mock_gemini):
    """Test low confidence items include reasoning"""
    # Mock response with low confidence
    with patch("api.services.gemini_service.model.generate_content") as mock_gen:
        mock_response = MagicMock()
        mock_response.text = """[
            {
                "type": "Event",
                "title": "Maybe basketball?",
                "description": "Blurry image",
                "date": "2024-11-20",
                "audience_tags": ["all"],
                "source_page": 1,
                "source_snippet": "Hard to read",
                "confidence_score": 0.65,
                "reasoning": "Image quality poor"
            }
        ]"""
        mock_gen.return_value = mock_response

        items = await parse_pdf_newsletter("blurry.pdf")

        low_conf_items = [i for i in items if i["confidence_score"] < 0.9]
        for item in low_conf_items:
            # Should have reasoning for low confidence
            assert "reasoning" in item


@pytest.mark.asyncio
async def test_answer_generation_includes_context(mock_gemini):
    """Test answer generation uses context items"""
    context = [
        {
            "title": "Basketball practice",
            "date": "2024-11-20",
            "description": "Weekly practice"
        }
    ]

    answer = await generate_answer("When is basketball?", context)

    assert isinstance(answer, str)
    assert len(answer) > 0
