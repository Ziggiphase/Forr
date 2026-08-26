import asyncio
import httpx
import logging
from sqlalchemy.future import select
from app.database import async_session as async_session_maker
from app.models.business import Business
from app.core.encryption import decrypt_token
from app.services.agent import generate_agent_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING) # So we can see warnings easily

last_update_ids = {}

async def poll_telegram():
    logger.warning("🚀 Starting Telegram poller background task...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            try:
                async with async_session_maker() as session:
                    query = select(Business).where(Business.encrypted_telegram_token.is_not(None))
                    result = await session.execute(query)
                    businesses = result.scalars().all()

                for business in businesses:
                    token = decrypt_token(business.encrypted_telegram_token)
                    offset = last_update_ids.get(business.id, 0)
                    
                    url = f"https://api.telegram.org/bot{token}/getUpdates"
                    params = {"offset": offset, "timeout": 2}
                    
                    try:
                        res = await client.get(url, params=params)
                        if res.status_code == 200:
                            data = res.json()
                            if data.get("ok") and data.get("result"):
                                for update in data["result"]:
                                    update_id = update["update_id"]
                                    last_update_ids[business.id] = update_id + 1
                                    
                                    if "message" in update:
                                        msg = update["message"]
                                        chat_id = msg.get("chat", {}).get("id")
                                        text = msg.get("text", "")
                                        sender = msg.get("from", {}).get("first_name", "Unknown")
                                        logger.warning(f"📩 [TELEGRAM] Message to business '{business.name}': {text} (from {sender})")
                                        
                                        if text and chat_id:
                                            from app.services.inbox import process_incoming_message
                                            # Process via Inbox
                                            reply_text = await process_incoming_message(
                                                business_id=business.id,
                                                channel="telegram",
                                                customer_identifier=str(chat_id),
                                                customer_name=sender,
                                                content=text
                                            )
                                            # Send back to Telegram if AI responded
                                            if reply_text:
                                                from app.services.messaging import send_telegram_message
                                                await send_telegram_message(token, str(chat_id), reply_text)
                    except Exception as e:
                        logger.error(f"Error polling for business {business.id}: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Telegram poller main loop error: {e}")
            
            await asyncio.sleep(3)
