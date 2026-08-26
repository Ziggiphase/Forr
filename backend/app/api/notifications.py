from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()

@router.get("/")
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc())
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return [
        {
            "id": str(n.id),
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        } for n in notifications
    ]

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id)
    result = await db.execute(query)
    n = result.scalar_one_or_none()
    
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    n.is_read = True
    await db.commit()
    
    return {"status": "success"}

@router.post("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False)
    result = await db.execute(query)
    unread = result.scalars().all()
    for n in unread:
        n.is_read = True
    await db.commit()
    return {"status": "success"}
