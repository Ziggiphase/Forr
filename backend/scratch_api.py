from datetime import datetime, timezone
from app.core.encryption import decrypt_token
from app.services.messaging import send_telegram_message, send_whatsapp_message

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

    # Send message to channel
    if conversation.channel == "telegram":
        token = decrypt_token(business.encrypted_telegram_token)
        await send_telegram_message(token, conversation.customer_identifier, content)
    elif conversation.channel == "whatsapp":
        if not business.twilio_phone_number:
            raise HTTPException(status_code=400, detail="Twilio phone number not configured for this business")
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
        raise HTTPException(status_code=400, detail=f"Unsupported channel: {conversation.channel}")

    # Save message to database
    now = datetime.now(timezone.utc)
    new_message = Message(
        conversation_id=conversation.id,
        sender_type="human",
        content=content,
        created_at=now
    )
    db.add(new_message)
    
    # Update conversation activity
    conversation.last_activity_at = now
    
    await db.commit()
    await db.refresh(new_message)
    
    return new_message
