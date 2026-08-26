import os
import httpx
import logging

logger = logging.getLogger(__name__)

# Paystack API Keys
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")

async def initialize_transaction(email: str, amount: int, metadata: dict, subaccount: str = None) -> dict:
    """
    Initializes a transaction on Paystack.
    amount is in kobo (NGN).
    """
    if not PAYSTACK_SECRET_KEY:
        logger.warning("PAYSTACK_SECRET_KEY is missing. Using mock checkout URL.")
        return {
            "status": True,
            "data": {
                "authorization_url": "https://checkout.paystack.com/mock-transaction",
                "access_code": "mock_code",
                "reference": "mock_ref_" + str(amount)
            }
        }
        
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": amount,
        "metadata": metadata
    }
    if subaccount:
        data["subaccount"] = subaccount
        data["transaction_charge"] = int(amount * 0.02) # Forr takes 2% cut
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

async def verify_transaction(reference: str) -> dict:
    """Verifies a transaction on Paystack."""
    if not PAYSTACK_SECRET_KEY:
        return {"status": True, "data": {"status": "success", "metadata": {}}}
        
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def list_banks() -> list:
    if not PAYSTACK_SECRET_KEY:
        return [{"name": "Mock Bank", "code": "000"}]
    
    url = "https://api.paystack.co/bank?country=nigeria"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", [])
        return []

async def resolve_account_number(account_number: str, bank_code: str) -> dict:
    if not PAYSTACK_SECRET_KEY:
        return {"status": True, "data": {"account_name": "Mock Account Name"}}
        
    url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            return response.json()
        response.raise_for_status()
        return response.json()

async def create_subaccount(business_name: str, settlement_bank: str, account_number: str, percentage_charge: float = 2.0) -> dict:
    if not PAYSTACK_SECRET_KEY:
        return {"status": True, "data": {"subaccount_code": "SUB_mock123"}}
        
    url = "https://api.paystack.co/subaccount"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "business_name": business_name,
        "settlement_bank": settlement_bank,
        "account_number": account_number,
        "percentage_charge": percentage_charge
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

