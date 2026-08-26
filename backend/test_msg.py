import asyncio
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.services.inbox import process_incoming_message
import uuid

async def test():
    biz_id = uuid.UUID('1b8a939c-f0c5-4b70-99b0-480df848b799')
    
    # 1. We manually set the conversation status to resolved_pending_feedback in the DB
    from app.database import async_session
    from app.models.conversation import Conversation
    from sqlalchemy.future import select
    
    async with async_session() as db:
        res = await db.execute(select(Conversation).limit(1))
        conv = res.scalar_one()
        conv.status = 'resolved_pending_feedback'
        await db.commit()
        
    print("Set status to resolved_pending_feedback.")
    
    # 2. Simulate customer sending thumbs up
    res = await process_incoming_message(
        business_id=biz_id,
        channel=conv.channel,
        customer_identifier=conv.customer_identifier,
        customer_name='John Doe',
        content='helpful'
    )
    print("AI RESPONSE AFTER THUMBS UP:", res)
    
    # Check if satisfaction was recorded
    async with async_session() as db:
        res = await db.execute(select(Conversation).where(Conversation.id == conv.id))
        conv = res.scalar_one()
        print("Final satisfaction:", conv.satisfaction)

if __name__ == '__main__':
    asyncio.run(test())
