from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, cast, String

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.business import Business
from app.models.product import Product
from app.models.conversation import Conversation

router = APIRouter()

@router.get("/")
async def global_search(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not q or len(q) < 2:
        return {"businesses": [], "products": [], "conversations": []}
    
    term = f"%{q}%"

    # Search Businesses
    b_query = select(Business).where(
        Business.owner_id == current_user.id,
        Business.name.ilike(term)
    )
    b_res = await db.execute(b_query)
    businesses = b_res.scalars().all()

    b_ids = [b.id for b in businesses] if businesses else []
    # If no businesses match the name, still get all user's business IDs to search their products and conversations
    if not b_ids:
        all_b_query = select(Business.id).where(Business.owner_id == current_user.id)
        all_b_res = await db.execute(all_b_query)
        b_ids = all_b_res.scalars().all()
    else:
        # get all to search other tables
        all_b_query = select(Business.id).where(Business.owner_id == current_user.id)
        all_b_res = await db.execute(all_b_query)
        all_b_ids = all_b_res.scalars().all()
        b_ids_for_children = all_b_ids
    
    b_ids_for_children = b_ids if not 'all_b_ids' in locals() else all_b_ids
    
    if not b_ids_for_children:
        return {"businesses": [], "products": [], "conversations": []}

    # Search Products
    p_query = select(Product, Business.name.label('b_name')).join(Business).where(
        Product.business_id.in_(b_ids_for_children),
        or_(Product.name.ilike(term), Product.description.ilike(term))
    )
    p_res = await db.execute(p_query)
    products = p_res.all()

    # Search Conversations
    c_query = select(Conversation, Business.name.label('b_name')).join(Business).where(
        Conversation.business_id.in_(b_ids_for_children),
        or_(
            Conversation.customer_identifier.ilike(term),
            Conversation.customer_name.ilike(term)
        )
    )
    c_res = await db.execute(c_query)
    conversations = c_res.all()

    return {
        "businesses": [{"id": str(b.id), "name": b.name, "type": b.business_type} for b in businesses],
        "products": [{"id": str(p[0].id), "name": p[0].name, "business_id": str(p[0].business_id), "business_name": p[1]} for p in products],
        "conversations": [{"id": str(c[0].id), "customer_identifier": c[0].customer_identifier, "customer_name": c[0].customer_name, "business_id": str(c[0].business_id), "business_name": c[1]} for c in conversations]
    }
