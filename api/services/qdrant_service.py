"""Qdrant vector database service"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchAny
import logging
from typing import List, Dict, Any, Optional
import uuid

from api.config import settings
from api.services.gemini_service import generate_embedding

logger = logging.getLogger(__name__)

# Initialize Qdrant client
client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key
)

# Collection names
COLLECTION_ITEMS = "newsletter_items"
COLLECTION_MESSAGES = "parent_messages"
COLLECTION_TICKETS = "correction_tickets"


async def init_qdrant_collections():
    """Initialize Qdrant collections on startup"""
    collections = [
        COLLECTION_ITEMS,
        COLLECTION_MESSAGES,
        COLLECTION_TICKETS
    ]

    for collection_name in collections:
        try:
            if not client.collection_exists(collection_name):
                logger.info(f"Creating Qdrant collection: {collection_name}")
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=768,  # Gemini embedding dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection {collection_name} created successfully")
            else:
                logger.info(f"Collection {collection_name} already exists")
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            raise


async def index_item(item_id: str, item_data: Dict[str, Any]) -> str:
    """
    Index an approved item in Qdrant

    Args:
        item_id: UUID of the item
        item_data: Item data including title, description, etc.

    Returns:
        Qdrant point ID
    """
    try:
        # Generate embedding
        text = f"{item_data.get('title', '')} {item_data.get('description', '')} {item_data.get('location', '')}"
        embedding = await generate_embedding(text)

        # Create point
        point = PointStruct(
            id=str(item_id),
            vector=embedding,
            payload={
                "type": item_data.get("type"),
                "title": item_data.get("title"),
                "description": item_data.get("description"),
                "date": str(item_data.get("date")) if item_data.get("date") else None,
                "time": str(item_data.get("time")) if item_data.get("time") else None,
                "location": item_data.get("location"),
                "audience_tags": item_data.get("audience_tags", []),
                "confidence_score": float(item_data.get("confidence_score", 0)),
                "created_at": str(item_data.get("created_at")),
                "status": item_data.get("status", "approved")
            }
        )

        # Upsert to Qdrant
        client.upsert(
            collection_name=COLLECTION_ITEMS,
            points=[point]
        )

        logger.info(f"Indexed item {item_id} in Qdrant")

        return str(item_id)

    except Exception as e:
        logger.error(f"Error indexing item in Qdrant: {e}")
        raise


async def search_items(
    query: str,
    parent_grades: Optional[List[int]] = None,
    parent_activities: Optional[List[str]] = None,
    limit: int = 5,
    score_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Semantic search for items

    Args:
        query: Search query
        parent_grades: List of grades to filter (e.g., [5, 7])
        parent_activities: List of activities to filter (e.g., ["Basketball"])
        limit: Number of results
        score_threshold: Minimum similarity score

    Returns:
        List of matching items with scores
    """
    try:
        # Generate query embedding
        query_embedding = await generate_embedding(query)

        # Build filter
        should_conditions = []

        if parent_grades:
            grade_tags = [f"grade_{g}" for g in parent_grades]
            should_conditions.append(
                FieldCondition(
                    key="audience_tags",
                    match=MatchAny(any=grade_tags)
                )
            )

        if parent_activities:
            should_conditions.append(
                FieldCondition(
                    key="audience_tags",
                    match=MatchAny(any=parent_activities)
                )
            )

        # Always include "all" items
        should_conditions.append(
            FieldCondition(
                key="audience_tags",
                match=MatchAny(any=["all"])
            )
        )

        query_filter = Filter(should=should_conditions) if should_conditions else None

        # Search
        results = client.search(
            collection_name=COLLECTION_ITEMS,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True
        )

        # Format results
        return [
            {
                "id": hit.id,
                "score": hit.score,
                **hit.payload
            }
            for hit in results
        ]

    except Exception as e:
        logger.error(f"Error searching items in Qdrant: {e}")
        return []


async def find_duplicate_items(
    item_text: str,
    threshold: float = 0.85,
    exclude_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Find duplicate/similar items

    Args:
        item_text: Title + description to check
        threshold: Similarity threshold
        exclude_id: ID to exclude from results (e.g., the item itself)

    Returns:
        List of similar items
    """
    try:
        # Generate embedding
        embedding = await generate_embedding(item_text)

        # Search
        results = client.search(
            collection_name=COLLECTION_ITEMS,
            query_vector=embedding,
            limit=10,
            score_threshold=threshold
        )

        # Filter out excluded ID
        duplicates = [
            {
                "id": hit.id,
                "score": hit.score,
                **hit.payload
            }
            for hit in results
            if hit.id != exclude_id
        ]

        return duplicates

    except Exception as e:
        logger.error(f"Error finding duplicates in Qdrant: {e}")
        return []


async def get_recommendations(
    engaged_item_ids: List[str],
    delivered_item_ids: List[str],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Get recommended items based on engagement history

    Args:
        engaged_item_ids: IDs of items parent engaged with
        delivered_item_ids: IDs of items already delivered (to exclude)
        limit: Number of recommendations

    Returns:
        List of recommended items
    """
    try:
        if not engaged_item_ids:
            return []

        # Retrieve engaged item vectors
        points = client.retrieve(
            collection_name=COLLECTION_ITEMS,
            ids=[str(id) for id in engaged_item_ids]
        )

        if not points:
            return []

        # Average vectors (simple recommendation approach)
        import numpy as np
        avg_vector = np.mean([p.vector for p in points], axis=0).tolist()

        # Search for similar items
        results = client.search(
            collection_name=COLLECTION_ITEMS,
            query_vector=avg_vector,
            limit=limit * 2  # Over-fetch to filter
        )

        # Filter out already delivered items
        recommendations = [
            {
                "id": hit.id,
                "score": hit.score,
                **hit.payload
            }
            for hit in results
            if hit.id not in [str(id) for id in delivered_item_ids]
        ][:limit]

        return recommendations

    except Exception as e:
        logger.error(f"Error getting recommendations from Qdrant: {e}")
        return []


async def index_message(
    message_id: str,
    parent_id: str,
    message_text: str,
    intent: str,
    matched_item_id: Optional[str] = None
) -> str:
    """
    Index a parent message for conversation history search

    Args:
        message_id: UUID of message
        parent_id: UUID of parent
        message_text: Message content
        intent: Detected intent
        matched_item_id: Item ID if query was matched

    Returns:
        Qdrant point ID
    """
    try:
        embedding = await generate_embedding(message_text)

        point = PointStruct(
            id=str(message_id),
            vector=embedding,
            payload={
                "parent_id": str(parent_id),
                "message": message_text,
                "intent": intent,
                "matched_item_id": str(matched_item_id) if matched_item_id else None,
                "timestamp": str(uuid.uuid1().time)
            }
        )

        client.upsert(
            collection_name=COLLECTION_MESSAGES,
            points=[point]
        )

        return str(message_id)

    except Exception as e:
        logger.error(f"Error indexing message: {e}")
        raise


async def index_ticket(
    ticket_id: str,
    parent_id: str,
    description: str,
    ticket_type: str,
    status: str = "pending"
) -> str:
    """
    Index a correction ticket for similarity matching

    Args:
        ticket_id: UUID of ticket
        parent_id: UUID of parent
        description: Ticket description
        ticket_type: Type of ticket
        status: Ticket status

    Returns:
        Qdrant point ID
    """
    try:
        embedding = await generate_embedding(description)

        point = PointStruct(
            id=str(ticket_id),
            vector=embedding,
            payload={
                "parent_id": str(parent_id),
                "description": description,
                "type": ticket_type,
                "status": status
            }
        )

        client.upsert(
            collection_name=COLLECTION_TICKETS,
            points=[point]
        )

        return str(ticket_id)

    except Exception as e:
        logger.error(f"Error indexing ticket: {e}")
        raise


async def find_similar_tickets(
    description: str,
    threshold: float = 0.85,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Find similar tickets (for auto-validation)

    Args:
        description: Ticket description
        threshold: Similarity threshold
        limit: Max results

    Returns:
        List of similar tickets
    """
    try:
        embedding = await generate_embedding(description)

        results = client.search(
            collection_name=COLLECTION_TICKETS,
            query_vector=embedding,
            limit=limit,
            score_threshold=threshold
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                **hit.payload
            }
            for hit in results
        ]

    except Exception as e:
        logger.error(f"Error finding similar tickets: {e}")
        return []
