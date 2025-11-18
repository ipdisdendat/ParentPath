"""Webhooks for WhatsApp/SMS"""
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    WhatsApp Cloud API webhook

    Receives:
    - Inbound messages from parents
    - Delivery status updates
    - Read receipts

    Handles:
    - DONE replies
    - Queries
    - Error reports
    - Help requests
    """
    try:
        body = await request.json()
        logger.info(f"WhatsApp webhook received: {body}")

        # TODO: Implement message handling
        # - Extract message
        # - Detect intent
        # - Route to appropriate handler

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/whatsapp")
async def whatsapp_verification(request: Request):
    """
    WhatsApp webhook verification

    Meta sends GET request with challenge parameter to verify webhook URL
    """
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    # TODO: Verify token matches configured token
    if mode == "subscribe" and token:
        logger.info("WhatsApp webhook verified")
        return int(challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/twilio/sms")
async def twilio_sms_webhook(request: Request):
    """
    Twilio SMS webhook

    Alternative to WhatsApp for families without WhatsApp
    """
    try:
        form_data = await request.form()
        logger.info(f"Twilio SMS webhook received: {form_data}")

        # TODO: Implement SMS handling

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing Twilio webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
