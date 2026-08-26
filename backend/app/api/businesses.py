from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.business import Business
from app.schemas.business import BusinessCreate, BusinessRead, BusinessAgentConfigUpdate

router = APIRouter()

@router.put("/{business_id}/agent-config", response_model=BusinessRead)
async def update_agent_config(
    business_id: UUID,
    payload: BusinessAgentConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Business).where(Business.id == business_id, Business.owner_id == current_user.id)
    result = await db.execute(query)
    business = result.scalar_one_or_none()
    
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        
    business.agent_knowledge = payload.agent_knowledge
    business.agent_tone = payload.agent_tone
    await db.commit()
    await db.refresh(business)
    return business

@router.post("", response_model=BusinessRead, status_code=status.HTTP_201_CREATED)
async def create_business(
    business_in: BusinessCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business = Business(
        **business_in.model_dump(),
        owner_id=current_user.id
    )
    db.add(business)
    await db.commit()
    await db.refresh(business)
    return business

@router.get("", response_model=List[BusinessRead])
async def read_businesses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Business).where(Business.owner_id == current_user.id)
    )
    return result.scalars().all()

@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Business).where(Business.id == business_id, Business.owner_id == current_user.id)
    result = await db.execute(query)
    business = result.scalar_one_or_none()
    
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        
    await db.delete(business)
    await db.commit()
    return None


from pydantic import BaseModel
import httpx
from app.core.encryption import encrypt_token

class TelegramIntegration(BaseModel):
    token: str

@router.post("/{business_id}/integrations/telegram")
async def connect_telegram(
    business_id: UUID,
    payload: TelegramIntegration,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Business).where(Business.id == business_id, Business.owner_id == current_user.id)
    result = await db.execute(query)
    business = result.scalar_one_or_none()
    
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        
    # Verify token
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"https://api.telegram.org/bot{payload.token}/getMe", timeout=5.0)
            data = res.json()
            if not data.get("ok"):
                raise HTTPException(status_code=400, detail="Invalid Telegram token")
        except Exception:
            raise HTTPException(status_code=400, detail="Could not verify token with Telegram")

    business.encrypted_telegram_token = encrypt_token(payload.token)
    await db.commit()
    return {"message": "Telegram connected successfully"}

@router.delete("/{business_id}/integrations/telegram", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_telegram(
    business_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Business).where(Business.id == business_id, Business.owner_id == current_user.id)
    result = await db.execute(query)
    business = result.scalar_one_or_none()
    
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    business.encrypted_telegram_token = None
    await db.commit()
    return None

class WhatsAppIntegration(BaseModel):
    twilio_sid: str
    twilio_auth_token: str

@router.post("/{business_id}/integrations/whatsapp")
async def connect_whatsapp(
    business_id: UUID,
    payload: WhatsAppIntegration,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Business).where(Business.id == business_id, Business.owner_id == current_user.id)
    result = await db.execute(query)
    business = result.scalar_one_or_none()
    
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    # In a real app we'd verify the twilio credentials here
    business.encrypted_twilio_sid = encrypt_token(payload.twilio_sid)
    business.encrypted_twilio_auth_token = encrypt_token(payload.twilio_auth_token)
    await db.commit()
    return {"message": "WhatsApp connected successfully"}

@router.delete("/{business_id}/integrations/whatsapp", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_whatsapp(
    business_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Business).where(Business.id == business_id, Business.owner_id == current_user.id)
    result = await db.execute(query)
    business = result.scalar_one_or_none()
    
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    business.encrypted_twilio_sid = None
    business.encrypted_twilio_auth_token = None
    await db.commit()
    return None

@router.get("/{id}", response_model=BusinessRead)
async def read_business(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Business).where(
            Business.id == id,
            Business.owner_id == current_user.id
        )
    )
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

from pydantic import BaseModel
from app.services.paystack import list_banks, resolve_account_number, create_subaccount

class SubaccountCreate(BaseModel):
    bank_code: str
    account_number: str
    account_name: str
    bank_name: str

@router.get("/banks")
async def get_banks():
    banks = await list_banks()
    return banks

@router.post("/{business_id}/subaccount")
async def create_business_subaccount(
    business_id: UUID,
    payload: SubaccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Business).where(Business.id == business_id, Business.owner_id == current_user.id)
    result = await db.execute(query)
    business = result.scalar_one_or_none()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
        
    # Verify account
    resolve_res = await resolve_account_number(payload.account_number, payload.bank_code)
    if not resolve_res.get("status"):
        raise HTTPException(status_code=400, detail="Could not resolve bank account")
        
    resolved_name = resolve_res["data"]["account_name"]
    # We do a loose match or just check if it's broadly similar? The user requested: "Verify the returned account name matches what the business entered before saving"
    # To avoid strict case sensitivity or minor spacing issues:
    if resolved_name.strip().lower() != payload.account_name.strip().lower():
        raise HTTPException(status_code=400, detail=f"Account name mismatch. Expected: {payload.account_name}, got: {resolved_name}")
        
    # Create subaccount
    sub_res = await create_subaccount(
        business_name=business.name,
        settlement_bank=payload.bank_code,
        account_number=payload.account_number,
        percentage_charge=2.0
    )
    
    if not sub_res.get("status"):
        raise HTTPException(status_code=400, detail="Failed to create Paystack subaccount")
        
    sub_code = sub_res["data"]["subaccount_code"]
    
    business.paystack_subaccount_code = sub_code
    business.bank_account_number = payload.account_number
    business.bank_code = payload.bank_code
    business.bank_name = payload.bank_name
    business.bank_account_name = resolved_name
    
    await db.commit()
    return {"status": "success", "subaccount_code": sub_code}

