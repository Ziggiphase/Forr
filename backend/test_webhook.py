import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import async_session
from app.models.business import Business
from app.core.encryption import encrypt_token

async def test_webhook():
    biz_id = "edc22413-7234-4c44-8d09-b9227adb5008"
    print("--- Testing WhatsApp Webhook ---")
    
    # 1. Connect WhatsApp
    async with async_session() as db:
        res = await db.execute(select(Business).where(Business.id == biz_id))
        biz = res.scalar_one_or_none()
        if not biz:
            print("Business not found!")
            return
        
        biz.encrypted_twilio_sid = encrypt_token("fake_sid")
        biz.encrypted_twilio_auth_token = encrypt_token("fake_token")
        await db.commit()
        print("Connected WhatsApp for business.")

    # 2. Simulate Webhook
    async with httpx.AsyncClient() as client:
        print("Simulating incoming message...")
        res = await client.post(
            f"http://localhost:8000/api/v1/webhooks/twilio/whatsapp/{biz_id}",
            data={"From": "whatsapp:+1234567890", "Body": "Test message!"}
        )
        print(f"Webhook response: {res.status_code}")
        
    # 3. Disconnect WhatsApp
    async with async_session() as db:
        res = await db.execute(select(Business).where(Business.id == biz_id))
        biz = res.scalar_one_or_none()
        biz.encrypted_twilio_sid = None
        biz.encrypted_twilio_auth_token = None
        await db.commit()
        print("Disconnected WhatsApp.")
        
    # 4. Simulate Webhook Again
    async with httpx.AsyncClient() as client:
        print("Simulating incoming message after disconnect...")
        res = await client.post(
            f"http://localhost:8000/api/v1/webhooks/twilio/whatsapp/{biz_id}",
            data={"From": "whatsapp:+1234567890", "Body": "Test message!"}
        )
        print(f"Webhook response after disconnect: {res.status_code}")

if __name__ == "__main__":
    asyncio.run(test_webhook())
