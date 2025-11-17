"""Family/parent portal endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.database import get_db
from api.models import Parent, Child, Card

router = APIRouter()


@router.get("/settings")
async def get_settings(
    parent_id: str,  # TODO: Extract from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Get parent settings

    Args:
        parent_id: UUID from JWT token

    Returns:
        Parent settings and children
    """
    try:
        stmt = select(Parent).where(Parent.id == parent_id)
        result = await db.execute(stmt)
        parent = result.scalar_one_or_none()

        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")

        # Get children
        children_stmt = select(Child).where(Child.parent_id == parent_id)
        children_result = await db.execute(children_stmt)
        children = children_result.scalars().all()

        return {
            "parent_id": str(parent.id),
            "language": parent.language,
            "channel_type": parent.channel_type,
            "status": parent.status,
            "children": [
                {
                    "id": str(c.id),
                    "grade": c.grade,
                    "division": c.division
                }
                for c in children
            ],
            "preferences": {
                "quiet_hours_start": parent.quiet_hours_start.isoformat() if parent.quiet_hours_start else None,
                "quiet_hours_end": parent.quiet_hours_end.isoformat() if parent.quiet_hours_end else None,
                "heads_up_mode": parent.heads_up_mode
            },
            "points_balance": parent.points_balance
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings")
async def update_settings(
    settings: dict,
    parent_id: str,  # TODO: Extract from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Update parent settings

    Args:
        settings: Settings to update
        parent_id: UUID from JWT token

    Returns:
        Updated settings
    """
    # TODO: Implement settings update
    return {"status": "not_implemented"}


@router.get("/history")
async def get_history(
    parent_id: str,  # TODO: Extract from JWT token
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Get parent's card history

    Args:
        parent_id: UUID from JWT token
        limit: Max results

    Returns:
        List of cards (items delivered to parent)
    """
    try:
        stmt = select(Card).where(Card.parent_id == parent_id).limit(limit)
        stmt = stmt.order_by(Card.created_at.desc())

        result = await db.execute(stmt)
        cards = result.scalars().all()

        return {
            "cards": [
                {
                    "id": str(c.id),
                    "item_id": str(c.item_id),
                    "status": c.status,
                    "delivered_at": c.delivered_at.isoformat() if c.delivered_at else None,
                    "completed_at": c.completed_at.isoformat() if c.completed_at else None
                }
                for c in cards
            ],
            "total": len(cards)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
