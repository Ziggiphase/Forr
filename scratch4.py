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

