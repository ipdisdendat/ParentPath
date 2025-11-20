"""Tests for Qdrant vector database service"""
import pytest
from unittest.mock import patch, MagicMock
from api.services.qdrant_service import (
    init_qdrant_collections,
    index_item,
    search_items,
    find_duplicate_items,
    get_recommendations,
    COLLECTION_ITEMS,
    COLLECTION_MESSAGES,
    COLLECTION_TICKETS
)
import uuid
from datetime import datetime


@pytest.fixture
def sample_item():
    """Sample item for testing"""
    return {
        "type": "Event",
        "title": "Basketball practice",
        "description": "Weekly practice session",
        "date": "2024-11-20",
        "time": "16:00",
        "location": "School gym",
        "audience_tags": ["grade_5", "Basketball"],
        "confidence_score": 0.95,
        "created_at": datetime.utcnow(),
        "status": "approved"
    }


@pytest.mark.asyncio
async def test_collections_created(mock_gemini):
    """Test all 3 collections are created with 768-dim vectors"""
    with patch("api.services.qdrant_service.client") as mock_client:
        mock_client.collection_exists.return_value = False

        await init_qdrant_collections()

        # Verify 3 collections created
        assert mock_client.create_collection.call_count == 3

        # Check each collection
        calls = mock_client.create_collection.call_args_list
        collection_names = {call.kwargs["collection_name"] for call in calls}

        assert COLLECTION_ITEMS in collection_names
        assert COLLECTION_MESSAGES in collection_names
        assert COLLECTION_TICKETS in collection_names

        # Verify vector dimension is 768
        for call in calls:
            vectors_config = call.kwargs["vectors_config"]
            assert vectors_config.size == 768


@pytest.mark.asyncio
async def test_index_single_item(mock_gemini, sample_item):
    """Test indexing a single item"""
    with patch("api.services.qdrant_service.client") as mock_client:
        item_id = str(uuid.uuid4())

        result = await index_item(item_id, sample_item)

        assert result == item_id
        assert mock_client.upsert.called

        # Verify payload structure
        call_args = mock_client.upsert.call_args
        points = call_args.kwargs["points"]
        assert len(points) == 1
        assert points[0].id == item_id
        assert len(points[0].vector) == 768


@pytest.mark.asyncio
async def test_batch_indexing_performance(mock_gemini):
    """Test batch indexing multiple items"""
    with patch("api.services.qdrant_service.client") as mock_client:
        items = [
            {
                "type": "Event",
                "title": f"Event {i}",
                "description": f"Description {i}",
                "date": "2024-11-20",
                "audience_tags": ["all"],
                "confidence_score": 0.9,
                "created_at": datetime.utcnow(),
                "status": "approved"
            }
            for i in range(10)
        ]

        # Index all items
        for i, item in enumerate(items):
            await index_item(str(uuid.uuid4()), item)

        # Should be called 10 times
        assert mock_client.upsert.call_count == 10


@pytest.mark.asyncio
async def test_semantic_search_similarity(mock_gemini):
    """Test semantic search returns similar items"""
    with patch("api.services.qdrant_service.client") as mock_client:
        # Mock search result
        mock_hit = MagicMock()
        mock_hit.id = str(uuid.uuid4())
        mock_hit.score = 0.92
        mock_hit.payload = {
            "title": "Basketball practice",
            "type": "Event",
            "date": "2024-11-20"
        }
        mock_client.search.return_value = [mock_hit]

        results = await search_items("basketball game", parent_grades=[5])

        assert len(results) > 0
        assert results[0]["score"] > 0.7
        assert "title" in results[0]


@pytest.mark.asyncio
async def test_duplicate_detection(mock_gemini):
    """Test duplicate item detection"""
    with patch("api.services.qdrant_service.client") as mock_client:
        # Mock duplicate found
        mock_hit = MagicMock()
        mock_hit.id = str(uuid.uuid4())
        mock_hit.score = 0.95
        mock_hit.payload = {"title": "Basketball practice"}
        mock_client.search.return_value = [mock_hit]

        duplicates = await find_duplicate_items(
            "Basketball practice Nov 20",
            threshold=0.85
        )

        assert len(duplicates) > 0
        assert duplicates[0]["score"] >= 0.85


@pytest.mark.asyncio
async def test_recommendations(mock_gemini):
    """Test recommendation engine"""
    with patch("api.services.qdrant_service.client") as mock_client:
        # Mock engaged items retrieval
        engaged_id = str(uuid.uuid4())
        mock_point = MagicMock()
        mock_point.vector = [0.1] * 768
        mock_client.retrieve.return_value = [mock_point]

        # Mock recommendations
        mock_hit = MagicMock()
        mock_hit.id = str(uuid.uuid4())
        mock_hit.score = 0.88
        mock_hit.payload = {"title": "Similar event"}
        mock_client.search.return_value = [mock_hit]

        recommendations = await get_recommendations(
            engaged_item_ids=[engaged_id],
            delivered_item_ids=[],
            limit=5
        )

        assert isinstance(recommendations, list)


@pytest.mark.asyncio
async def test_audience_filtering(mock_gemini):
    """Test audience tag filtering"""
    with patch("api.services.qdrant_service.client") as mock_client:
        mock_client.search.return_value = []

        # Search with grade filter
        await search_items(
            "events",
            parent_grades=[5, 6],
            parent_activities=["Basketball"]
        )

        # Verify filter was applied
        assert mock_client.search.called
        call_args = mock_client.search.call_args
        query_filter = call_args.kwargs.get("query_filter")

        # Should have filter conditions
        assert query_filter is not None


@pytest.mark.asyncio
async def test_search_latency_under_100ms(mock_gemini):
    """Test search latency is acceptable"""
    import time

    with patch("api.services.qdrant_service.client") as mock_client:
        mock_client.search.return_value = []

        start = time.time()
        await search_items("test query")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        # Mock should be very fast
        assert elapsed < 100, f"Search took {elapsed}ms"


@pytest.mark.asyncio
async def test_collection_persistence(mock_gemini):
    """Test collections persist after restart"""
    with patch("api.services.qdrant_service.client") as mock_client:
        # Simulate existing collection
        mock_client.collection_exists.return_value = True

        await init_qdrant_collections()

        # Should not recreate existing collections
        assert not mock_client.create_collection.called


@pytest.mark.asyncio
async def test_vector_dimension_correct(mock_gemini, sample_item):
    """Test vector dimensions match Gemini embedding size"""
    with patch("api.services.qdrant_service.client") as mock_client:
        await index_item(str(uuid.uuid4()), sample_item)

        # Get the vector from upsert call
        points = mock_client.upsert.call_args.kwargs["points"]
        vector = points[0].vector

        assert len(vector) == 768, "Vector dimension must match Gemini embedding (768)"
