import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from uuid import UUID
from datetime import datetime, timezone
import asyncio

from app.database import async_session
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.agent import generate_agent_response

logger = logging.getLogger(__name__)

async def process_incoming_message(
    business_id: UUID,
    channel: str,
    customer_identifier: str,
    customer_name: str | None,
    content: str
) -> str | None:
    """
    Processes an incoming message, saves it to the DB, and generates an AI response if applicable.
    Returns the AI response string, or None if the AI is not handling this conversation.
    """
    async with async_session() as session:
        # 1. Find or create the conversation
        query = select(Conversation).where(
            Conversation.business_id == business_id,
            Conversation.channel == channel,
            Conversation.customer_identifier == customer_identifier
        )
        result = await session.execute(query)
        conversation = result.scalar_one_or_none()
        
        now = datetime.now(timezone.utc)
        
        if not conversation:
            conversation = Conversation(
                business_id=business_id,
                channel=channel,
                customer_identifier=customer_identifier,
                customer_name=customer_name,
                status="ai_handling",
                last_activity_at=now,
                is_unread=True
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
        
        # 0. Check for feedback if pending
        if conversation.status == "resolved_pending_feedback":
            user_msg_clean = content.strip().lower()
            if user_msg_clean in ["👍", "+1", "yes", "helpful", "good"]:
                conversation.satisfaction = "up"
                conversation.status = "ai_handling"
                await session.commit()
                return "Thank you for your feedback!"
            elif user_msg_clean in ["👎", "-1", "no", "not helpful", "bad"]:
                conversation.satisfaction = "down"
                conversation.status = "ai_handling"
                await session.commit()
                return "We're sorry to hear that. A human will review this conversation."
                
        # 1. Update Customer info if changed
        if customer_name and conversation.customer_name != customer_name:
            conversation.customer_name = customer_name
            
        # 2. Save incoming message
        now = datetime.now(timezone.utc)
        incoming_message = Message(
            conversation_id=conversation.id,
            sender_type="customer",
            content=content,
            created_at=now
        )
        session.add(incoming_message)
        
        conversation.last_activity_at = now
        conversation.is_unread = True
        await session.commit()
        
        # 3. Generate AI response if handled by AI
        if conversation.status == "ai_handling":
            # Pass to AI Agent
            try:
                ai_response, should_escalate, is_resolved, limit_reached, total_tokens = await generate_agent_response(business_id, content, conversation.id, conversation.customer_identifier)
            except Exception as e:
                logger.error(f"Error generating AI response for business {business_id}: {e}")
                ai_response = "Sorry, I am currently unavailable."
                should_escalate = False
                is_resolved = False
                limit_reached = False
                total_tokens = 0
            
            if limit_reached:
                conversation.status = "limit_reached"
                await session.commit()
                # We can still send the fallback message to the customer
                
            elif should_escalate:
                conversation.status = "needs_human"
                await session.commit()
                return None
            
            # 4. Save AI response
            if ai_response or is_resolved:
                final_response = ai_response or ""
                if is_resolved:
                    conversation.status = "resolved_pending_feedback"
                    final_response += ("\n\nWas this helpful? Reply with 👍 or 👎" if final_response else "Was this helpful? Reply with 👍 or 👎")
                    
                now_ai = datetime.now(timezone.utc)
                response_time_ms = int((now_ai - now).total_seconds() * 1000)
                
                outgoing_message = Message(
                    conversation_id=conversation.id,
                    sender_type="ai",
                    content=final_response.strip(),
                    created_at=now_ai,
                    response_time_ms=response_time_ms,
                    tokens_used=total_tokens
                )
                session.add(outgoing_message)
                
                conversation.last_activity_at = now_ai
                await session.commit()
                
                return final_response.strip()
            
        # If manual or needs_human, we don't generate an AI response automatically.
        return None
