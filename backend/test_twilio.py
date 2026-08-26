import asyncio
import os
import httpx
from uuid import UUID
from twilio.request_validator import RequestValidator

from app.database import async_session
from app.models.business import Business
from app.core.encryption import encrypt_token
from sqlalchemy.future import select

async def main():
    async with async_session() as session:
        result = await session.execute(select(Business))
        business = result.scalars().first()
        if not business:
            print("No business found.")
            return

        business_id = str(business.id)
        
        # Connect WhatsApp
        auth_token = "my_secret_test_token_123"
        business.encrypted_twilio_sid = encrypt_token("test_sid")
        business.encrypted_twilio_auth_token = encrypt_token(auth_token)
        await session.commit()
        print(f"Connected WhatsApp for business: {business.name}")

    # Prepare webhook request
    url = f"http://127.0.0.1:8001/api/v1/webhooks/twilio/{business_id}"
    params = {
        "From": "whatsapp:+14155238886",
        "Body": "Hello Twilio webhook!"
    }
    
    # Twilio validator expects HTTPS if that's what we check in the backend
    # Our backend does: `url.replace("http://", "https://")`
    validator_url = url.replace("http://", "https://")
    validator = RequestValidator(auth_token)
    signature = validator.compute_signature(validator_url, params)
    
    print(f"Computed Signature: {signature}")
    
    # Send request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url, 
            data=params, 
            headers={"X-Twilio-Signature": signature}
        )
        print(f"Response: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    asyncio.run(main())
