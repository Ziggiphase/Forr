from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, text
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.models.business import Business
from app.models.conversation import Conversation
from app.models.message import Message
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/businesses/{business_id}/analytics")
async def get_analytics(
    business_id: UUID,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify ownership
    biz = await db.get(Business, business_id)
    if not biz or biz.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Business not found")
        
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Total Conversations
    conv_query = select(func.count(Conversation.id)).where(
        Conversation.business_id == business_id,
        Conversation.created_at >= cutoff_date
    )
    total_conv = (await db.execute(conv_query)).scalar() or 0
    
    # Escalations (needs_human or manual)
    esc_query = select(func.count(Conversation.id)).where(
        Conversation.business_id == business_id,
        Conversation.created_at >= cutoff_date,
        Conversation.status.in_(["needs_human", "manual"])
    )
    total_esc = (await db.execute(esc_query)).scalar() or 0
    escalation_rate = total_esc / total_conv if total_conv > 0 else 0.0

    # Activity Chart (Unique Customers vs Total Chats)
    # Using raw SQL for date trunc since it's easier
    activity_sql = text('''
        SELECT DATE(created_at) as day, 
               COUNT(id) as total_chats, 
               COUNT(DISTINCT customer_identifier) as unique_customers
        FROM conversations
        WHERE business_id = :biz_id AND created_at >= :cutoff
        GROUP BY DATE(created_at)
        ORDER BY day
    ''')
    activity_res = await db.execute(activity_sql, {"biz_id": business_id, "cutoff": cutoff_date})
    activity_data = [{"date": str(row.day), "total": row.total_chats, "unique": row.unique_customers} for row in activity_res]

    # Response Time (AI vs Manual) in seconds
    rt_sql = text('''
        SELECT sender_type, AVG(response_time_ms) / 1000.0 as avg_rt
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE c.business_id = :biz_id 
          AND m.created_at >= :cutoff 
          AND m.response_time_ms IS NOT NULL
        GROUP BY sender_type
    ''')
    rt_res = await db.execute(rt_sql, {"biz_id": business_id, "cutoff": cutoff_date})
    rt_data = {"ai": 0, "human": 0}
    for row in rt_res:
        if row.sender_type in rt_data:
            rt_data[row.sender_type] = float(row.avg_rt) if row.avg_rt else 0

    # Token Spend Over Time
    token_sql = text('''
        SELECT DATE(m.created_at) as day, SUM(m.tokens_used) as total_tokens
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE c.business_id = :biz_id AND m.created_at >= :cutoff AND m.tokens_used IS NOT NULL
        GROUP BY DATE(m.created_at)
        ORDER BY day
    ''')
    token_res = await db.execute(token_sql, {"biz_id": business_id, "cutoff": cutoff_date})
    token_data = [{"date": str(row.day), "tokens": row.total_tokens} for row in token_res]

    # Satisfaction
    sat_sql = text('''
        SELECT satisfaction, COUNT(id) as cnt
        FROM conversations
        WHERE business_id = :biz_id 
          AND created_at >= :cutoff 
          AND satisfaction IS NOT NULL
        GROUP BY satisfaction
    ''')
    sat_res = await db.execute(sat_sql, {"biz_id": business_id, "cutoff": cutoff_date})
    sat_data = {"thumbs_up": 0, "thumbs_down": 0}
    for row in sat_res:
        if row.satisfaction == "up":
            sat_data["thumbs_up"] = row.cnt
        elif row.satisfaction == "down":
            sat_data["thumbs_down"] = row.cnt

    return {
        "total_conversations": total_conv,
        "escalation_rate": escalation_rate,
        "activity": activity_data,
        "response_time": {
            "ai_avg_seconds": rt_data["ai"],
            "manual_avg_seconds": rt_data["human"]
        },
        "token_spend": token_data,
        "satisfaction": sat_data
    }
