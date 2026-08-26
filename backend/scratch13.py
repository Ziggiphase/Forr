import asyncio
from app.database import async_session
from sqlalchemy.future import select
from app.models.conversation import Conversation
from app.models.message import Message

async def fetch():
    async with async_session() as s:
        r = await s.execute(select(Conversation))
        convs = r.scalars().all()
        for c in convs:
            mr = await s.execute(select(Message).where(Message.conversation_id == c.id))
            msgs = mr.scalars().all()
            print(f"Conversation {c.id}: channel={c.channel}, identifier={c.customer_identifier}")
            for m in msgs:
                print(f"  [{m.sender_type}] {m.content}")

asyncio.run(fetch())
