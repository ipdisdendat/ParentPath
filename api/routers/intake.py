"""Newsletter intake endpoints"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hashlib
import shutil
from pathlib import Path
from datetime import date
import logging

from api.database import get_db
from api.models import Newsletter

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_newsletter(
    file: UploadFile = File(...),
    title: str = None,
    publish_date: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a newsletter for parsing

    Args:
        file: PDF or image file
        title: Newsletter title (optional)
        publish_date: YYYY-MM-DD format (optional, defaults to today)

    Returns:
        Newsletter ID and status
    """
    try:
        # Validate file type
        if not file.content_type in ["application/pdf", "image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF, JPEG, and PNG allowed."
            )

        # Read file content
        content = await file.read()

        # Calculate hash for deduplication
        file_hash = hashlib.sha256(content).hexdigest()

        # Check if already exists
        stmt = select(Newsletter).where(Newsletter.file_hash == file_hash)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return {
                "newsletter_id": str(existing.id),
                "status": "duplicate",
                "message": "This newsletter has already been uploaded"
            }

        # Save file
        file_ext = Path(file.filename).suffix
        file_path = UPLOAD_DIR / f"{file_hash}{file_ext}"

        with open(file_path, "wb") as f:
            f.write(content)

        # Create newsletter record
        newsletter = Newsletter(
            title=title or file.filename,
            publish_date=date.fromisoformat(publish_date) if publish_date else date.today(),
            file_hash=file_hash,
            file_path=str(file_path),
            file_type=file.content_type,
            file_size_bytes=len(content),
            parse_status="pending"
        )

        db.add(newsletter)
        await db.commit()
        await db.refresh(newsletter)

        logger.info(f"Newsletter uploaded: {newsletter.id}")

        # TODO: Queue parsing job
        # await queue_parse_job(str(newsletter.id))

        return {
            "newsletter_id": str(newsletter.id),
            "status": "queued",
            "estimated_parse_time": "10 minutes",
            "message": "Newsletter queued for parsing"
        }

    except Exception as e:
        logger.error(f"Error uploading newsletter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email")
async def email_webhook(
    # Email webhook payload from SendGrid/Mailgun
    # TODO: Implement email parsing
):
    """
    Webhook for email-forwarded newsletters

    Integration with email services to accept newsletters forwarded to
    intake@parentpath.app
    """
    return {"status": "not_implemented"}


@router.post("/whatsapp")
async def whatsapp_photo_webhook(
    # WhatsApp photo upload webhook
    # TODO: Implement WhatsApp photo handling
):
    """
    Webhook for WhatsApp photo uploads (flyers, permission slips)

    Parents can text photos of flyers directly
    """
    return {"status": "not_implemented"}
