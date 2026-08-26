import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import async_session
from app.models.business import Business
from app.models.subscription import Subscription

async def main():
    async with async_session() as db:
        biz_query = select(Business).options(selectinload(Business.subscription)).limit(1)
        result = await db.execute(biz_query)
        biz = result.scalar_one()
        print(f"Initial Plan: {biz.subscription.plan_tier if biz.subscription else 'free'}")
        
        # Simulate Paystack Webhook
        if not biz.subscription:
            biz.subscription = Subscription(business_id=biz.id)
        biz.subscription.plan_tier = 'pro'
        biz.subscription.status = 'active'
        await db.commit()
        
        biz_query = select(Business).options(selectinload(Business.subscription)).where(Business.id == biz.id)
        result = await db.execute(biz_query)
        biz2 = result.scalar_one()
        print(f"Final Plan: {biz2.subscription.plan_tier}")
        print(f"New Limit: {biz2.conversation_limit}")

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
