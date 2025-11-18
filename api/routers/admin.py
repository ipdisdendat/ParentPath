"""Admin review and management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import logging

from api.database import get_db
from api.models import Item, Newsletter, Ticket

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/newsletters")
async def list_newsletters(
    limit: int = Query(20, le=100),
    offset: int = 0,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List uploaded newsletters

    Args:
        limit: Max results
        offset: Pagination offset
        status: Filter by parse_status

    Returns:
        List of newsletters
    """
    try:
        stmt = select(Newsletter).limit(limit).offset(offset)

        if status:
            stmt = stmt.where(Newsletter.parse_status == status)

        stmt = stmt.order_by(Newsletter.created_at.desc())

        result = await db.execute(stmt)
        newsletters = result.scalars().all()

        return {
            "newsletters": [
                {
                    "id": str(n.id),
                    "title": n.title,
                    "publish_date": n.publish_date.isoformat(),
                    "parse_status": n.parse_status,
                    "items_extracted": n.items_extracted,
                    "created_at": n.created_at.isoformat()
                }
                for n in newsletters
            ],
            "total": len(newsletters),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error listing newsletters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items")
async def list_items(
    status: str = "pending",
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List items for review

    Args:
        status: Filter by status (pending, approved, rejected)
        limit: Max results
        offset: Pagination offset

    Returns:
        List of items with confidence scores and similar items
    """
    try:
        stmt = select(Item).where(Item.status == status).limit(limit).offset(offset)
        stmt = stmt.order_by(Item.created_at.desc())

        result = await db.execute(stmt)
        items = result.scalars().all()

        # TODO: Enrich with Qdrant similar items

        return {
            "items": [
                {
                    "id": str(item.id),
                    "type": item.type,
                    "title": item.title,
                    "description": item.description,
                    "date": item.date.isoformat() if item.date else None,
                    "audience_tags": item.audience_tags,
                    "confidence_score": float(item.confidence_score) if item.confidence_score else 0,
                    "gemini_reasoning": item.gemini_reasoning,
                    "status": item.status,
                    "created_at": item.created_at.isoformat()
                }
                for item in items
            ],
            "total": len(items),
            "status": status
        }

    except Exception as e:
        logger.error(f"Error listing items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/items/{item_id}/approve")
async def approve_item(
    item_id: str,
    edits: dict = None,
    notes: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Approve an item (with optional edits)

    Args:
        item_id: UUID of item
        edits: Dict of field edits (e.g., {"time": "16:00"})
        notes: Admin notes

    Returns:
        Updated item
    """
    try:
        stmt = select(Item).where(Item.id == item_id)
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Apply edits if provided
        if edits:
            for field, value in edits.items():
                if hasattr(item, field):
                    setattr(item, field, value)

        item.status = "approved"
        item.approved_at = datetime.utcnow()
        # item.approved_by = current_admin_id  # TODO: Add auth

        await db.commit()
        await db.refresh(item)

        logger.info(f"Item {item_id} approved")

        # TODO: Index in Qdrant

        return {
            "id": str(item.id),
            "status": item.status,
            "approved_at": item.approved_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Error approving item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/items/{item_id}/reject")
async def reject_item(
    item_id: str,
    reason: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Reject an item

    Args:
        item_id: UUID of item
        reason: Rejection reason

    Returns:
        Updated item
    """
    try:
        stmt = select(Item).where(Item.id == item_id)
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        item.status = "rejected"

        await db.commit()

        logger.info(f"Item {item_id} rejected: {reason}")

        return {
            "id": str(item.id),
            "status": item.status
        }

    except Exception as e:
        logger.error(f"Error rejecting item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets")
async def list_tickets(
    status: str = "pending",
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    List correction tickets

    Args:
        status: Filter by status
        limit: Max results

    Returns:
        List of tickets
    """
    try:
        stmt = select(Ticket).where(Ticket.status == status).limit(limit)
        stmt = stmt.order_by(Ticket.created_at.desc())

        result = await db.execute(stmt)
        tickets = result.scalars().all()

        return {
            "tickets": [
                {
                    "id": str(t.id),
                    "parent_id": str(t.parent_id),
                    "type": t.ticket_type,
                    "description": t.description,
                    "proposed_changes": t.proposed_changes,
                    "status": t.status,
                    "created_at": t.created_at.isoformat()
                }
                for t in tickets
            ],
            "total": len(tickets)
        }

    except Exception as e:
        logger.error(f"Error listing tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))
