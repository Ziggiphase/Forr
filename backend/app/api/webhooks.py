from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
import logging

from app.database import get_db
from app.models.business import Business
from app.services.agent import generate_agent_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

router = APIRouter()

@router.post("/twilio/whatsapp/{business_id}")
async def twilio_whatsapp_webhook(
    business_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    query = select(Business).where(Business.id == business_id)
    result = await db.execute(query)
    business = result.scalar_one_or_none()
    
    if not business or not business.is_whatsapp_connected:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business or integration not found")

    # Parse incoming Twilio form data
    form_data = await request.form()
    
    sender = form_data.get("From", "Unknown")
    body = form_data.get("Body", "")
    
    # Ideally, we would verify the X-Twilio-Signature here using business.encrypted_twilio_auth_token.
    # However, since we are using ngrok for local development, the hostname often mismatches 
    # and causes signature validation to fail. For this testing phase, we log the message.
    
    logger.warning(f"📩 [WHATSAPP] Message to business '{business.name}': {body} (from {sender})")
    
    # Process via Inbox Service
    reply_text = "Sorry, I am currently unavailable."
    if body:
        # We don't have customer_name from Twilio natively unless we parse it from ProfileName
        customer_name = form_data.get("ProfileName", None)
        
        from app.services.inbox import process_incoming_message
        
        response = await process_incoming_message(
            business_id=business.id,
            channel="whatsapp",
            customer_identifier=sender,
            customer_name=customer_name,
            content=body
        )
        
        # Only reply if AI actually responded
        if response is not None:
            reply_text = response
        else:
            # If no response (manual mode), we should probably not reply anything,
            # but Twilio requires a 200 OK. Returning empty <Response></Response> is valid.
            twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>"""
            return Response(content=twiml_response, media_type="application/xml")
    
    # Twilio expects a 200 OK response with TwiML.
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_text}</Message>
</Response>"""
    return Response(content=twiml_response, media_type="application/xml")
