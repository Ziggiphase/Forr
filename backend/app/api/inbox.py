from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.business import Business
from app.schemas.inbox import ConversationRead, MessageRead, MessageCreate, ConversationStatusUpdate
from app.api.deps import get_current_active_user
from app.models.user import User
from app.core.encryption import decrypt_token
from app.services.messaging import send_telegram_message, send_whatsapp_message

router = APIRouter()

@router.get("/businesses/{business_id}/conversations", response_model=list[ConversationRead])
async def read_conversations(
    business_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    business = await db.get(Business, business_id)
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Business not found")
        
    query = select(Conversation).where(Conversation.business_id == business_id).order_by(Conversation.last_activity_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageRead])
async def read_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    business = await db.get(Business, conversation.business_id)
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    query = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
    result = await db.execute(query)
    return result.scalars().all()

@router.put("/conversations/{conversation_id}/read")
async def mark_conversation_read(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    business = await db.get(Business, conversation.business_id)
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    conversation.is_unread = False
    await db.commit()
    return {"status": "ok"}

@router.post("/conversations/{conversation_id}/messages", response_model=MessageRead)
async def send_manual_message(
    conversation_id: UUID,
    message_in: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    business = await db.get(Business, conversation.business_id)
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    content = message_in.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    if conversation.channel == "telegram":
        token = decrypt_token(business.encrypted_telegram_token)
        await send_telegram_message(token, conversation.customer_identifier, content)
    elif conversation.channel == "whatsapp":
        if not business.twilio_phone_number:
            raise HTTPException(status_code=400, detail="Twilio phone number not configured")
        sid = decrypt_token(business.encrypted_twilio_sid)
        auth_token = decrypt_token(business.encrypted_twilio_auth_token)
        await send_whatsapp_message(
            sid=sid,
            auth_token=auth_token,
            from_number=business.twilio_phone_number,
            to_number=conversation.customer_identifier,
            text=content
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported channel")

    # Get last message to calculate response time
    last_msg_res = await db.execute(
        select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at.desc()).limit(1)
    )
    last_msg = last_msg_res.scalar_one_or_none()
    
    now = datetime.now(timezone.utc)
    response_time_ms = None
    if last_msg and last_msg.sender_type == "customer":
        response_time_ms = int((now - last_msg.created_at.replace(tzinfo=timezone.utc)).total_seconds() * 1000)

    new_message = Message(
        conversation_id=conversation.id,
        sender_type="human",
        content=content,
        created_at=now,
        response_time_ms=response_time_ms
    )
    db.add(new_message)
    
    conversation.last_activity_at = now
    
    await db.commit()
    await db.refresh(new_message)
    
    return new_message

@router.put("/conversations/{conversation_id}/status")
async def update_conversation_status(
    conversation_id: UUID,
    status_update: ConversationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    business = await db.get(Business, conversation.business_id)
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    if status_update.status not in ["ai_handling", "manual", "needs_human"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    conversation.status = status_update.status
    await db.commit()
    return {"status": "ok", "new_status": conversation.status}
