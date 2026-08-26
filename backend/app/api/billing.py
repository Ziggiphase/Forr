from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from uuid import UUID
import logging
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models.business import Business
from app.models.subscription import Subscription
from app.models.conversation import Conversation
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.paystack import initialize_transaction

logger = logging.getLogger(__name__)

router = APIRouter()

TIERS = {
    "free": {"price_ngn": 0, "limit": 50},
    "pro": {"price_ngn": 10000, "limit": 500},
    "premium": {"price_ngn": 50000, "limit": 5000}
}

class UpgradeRequest(BaseModel):
    plan: str

@router.get("/businesses/{business_id}/billing/status")
async def get_billing_status(
    business_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    biz_query = select(Business).options(selectinload(Business.subscription)).where(Business.id == business_id)
    result = await db.execute(biz_query)
    business = result.scalar_one_or_none()
    
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Business not found")
        
    tier = business.subscription.plan_tier if business.subscription else "free"
    status = business.subscription.status if business.subscription else "active"
    
    # Calculate usage
    now = datetime.now(timezone.utc)
    if business.subscription and business.subscription.current_period_start:
        period_start = business.subscription.current_period_start
    else:
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
    conv_query = select(func.count(Conversation.id)).where(
        Conversation.business_id == business_id,
        Conversation.created_at >= period_start
    )
    usage_result = await db.execute(conv_query)
    usage = usage_result.scalar() or 0
        
    return {
        "tier": tier,
        "status": status,
        "limit": business.conversation_limit,
        "usage": usage,
        "period_start": period_start.isoformat(),
        "available_tiers": TIERS
    }

@router.post("/businesses/{business_id}/billing/upgrade")
async def upgrade_plan(
    business_id: UUID,
    request: UpgradeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if request.plan not in TIERS:
        raise HTTPException(status_code=400, detail="Invalid plan")
        
    biz_query = select(Business).options(selectinload(Business.subscription)).where(Business.id == business_id)
    result = await db.execute(biz_query)
    business = result.scalar_one_or_none()
    
    if not business or business.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Business not found")
        
    if request.plan == "free":
        if business.subscription:
            business.subscription.plan_tier = "free"
            business.subscription.status = "active"
            await db.commit()
        return {"status": "success", "message": "Downgraded to Free tier"}
        
    amount_kobo = TIERS[request.plan]["price_ngn"] * 100
    
    try:
        tx = await initialize_transaction(
            email=current_user.email,
            amount=amount_kobo,
            metadata={
                "business_id": str(business.id),
                "plan": request.plan,
                "type": "subscription_upgrade"
            }
        )
        return {"authorization_url": tx["data"]["authorization_url"]}
    except Exception as e:
        logger.error(f"Error initializing Paystack transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize payment")

@router.post("/webhooks/paystack")
async def paystack_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    event = payload.get("event")
    
    if event == "charge.success":
        data = payload.get("data", {})
        metadata = data.get("metadata", {})
        if metadata.get("type") == "subscription_upgrade":
            business_id = metadata.get("business_id")
            new_plan = metadata.get("plan")
            
            biz_query = select(Business).options(selectinload(Business.subscription)).where(Business.id == business_id)
            result = await db.execute(biz_query)
            business = result.scalar_one_or_none()
            
            if business:
                if not business.subscription:
                    business.subscription = Subscription(business_id=business.id)
                business.subscription.plan_tier = new_plan
                business.subscription.status = "active"
                
                now = datetime.now(timezone.utc)
                business.subscription.current_period_start = now
                business.subscription.current_period_end = now + timedelta(days=30)
                
                await db.commit()
                logger.info(f"Business {business_id} successfully upgraded to {new_plan}")
                
    return {"status": "ok"}
