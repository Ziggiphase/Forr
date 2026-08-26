import os
import json
import httpx
import logging
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timezone

from app.database import async_session
from app.models.business import Business
from app.models.product import Product
from app.models.subscription import Subscription
from app.models.conversation import Conversation
from app.models.payment import Payment
from app.services.email import send_email
from app.services.paystack import initialize_transaction

logger = logging.getLogger(__name__)

async def generate_agent_response(business_id: str, incoming_message: str, conversation_id: str = None, customer_identifier: str = None) -> tuple[str | None, bool, bool, bool, int]:
    """
    Generates an AI response based on the business's catalogue and knowledge base.
    Returns a tuple (response_text, should_escalate, is_resolved, limit_reached, total_tokens).
    """
    # Fetch business and products
    async with async_session() as db:
        biz_res = await db.execute(select(Business).where(Business.id == business_id))
        business = biz_res.scalar_one_or_none()
        
        prod_res = await db.execute(select(Product).where(Product.business_id == business_id, Product.status == 'active'))
        products = prod_res.scalars().all()
        
        if not business:
            return ("Sorry, this business is currently unavailable.", False, False, False, 0)

        # Check limits
        sub_res = await db.execute(select(Subscription).where(Subscription.business_id == business_id))
        subscription = sub_res.scalar_one_or_none()
        
        now = datetime.now(timezone.utc)
        if subscription and subscription.current_period_start:
            period_start = subscription.current_period_start
        else:
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
        conv_query = select(func.count(Conversation.id)).where(
            Conversation.business_id == business_id,
            Conversation.created_at >= period_start
        )
        usage_result = await db.execute(conv_query)
        usage = usage_result.scalar() or 0
        
        tier = subscription.plan_tier if subscription else "free"
        limit = 50
        if tier == "pro":
            limit = 500
        elif tier == "premium":
            limit = 5000
        
        if usage >= limit:
            from app.models.user import User
            from app.models.notification import Notification
            owner_res = await db.execute(select(User).where(User.id == business.owner_id))
            owner = owner_res.scalar_one_or_none()
            if owner:
                await send_email(owner.email, "Forr: Conversation Limit Reached", "Your business has reached its monthly conversation limit. Please upgrade your plan in the Billing dashboard to resume the AI agent.")
                
                # Create in-app notification
                n = Notification(
                    user_id=owner.id,
                    title="Action Required: AI Paused",
                    message=f"The AI for {business.name} has been paused because you reached your conversation limit. Upgrade in Billing."
                )
                db.add(n)
                await db.commit()
                
            return ("This AI agent is currently paused because the business has reached its conversation limit.", False, False, True, 0)

    # Construct the catalogue context
    catalogue_text = "PRODUCTS:\n"
    if not products:
        catalogue_text += "No active products available at the moment.\n"
    else:
        for p in products:
            catalogue_text += f"- {p.name} | Category: {p.category} | Price: NGN {p.price} | Stock: {p.quantity} | Desc: {p.description or 'None'}\n"

    # Construct the knowledge context
    kb = business.agent_knowledge or {}
    knowledge_text = "BUSINESS FACTS:\n"
    knowledge_text += f"Delivery Fee/Policy: {kb.get('delivery_fee', 'Not specified')}\n"
    knowledge_text += f"Return Policy: {kb.get('return_policy', 'Not specified')}\n"
    knowledge_text += f"Business Hours: {kb.get('business_hours', 'Not specified')}\n"

    tone = business.agent_tone or "Be helpful, professional, and concise."

    system_prompt = f"""You are an AI customer support and sales agent for '{business.name}'.
Your role is to help customers, answer questions about the business, and help them make purchases.

{knowledge_text}
{catalogue_text}

STRICT BOUNDARIES:
- You MUST ONLY provide facts, prices, and policies explicitly listed in your context above.
- If a customer asks about a product, price, or policy that is NOT in your context, you MUST NOT guess, invent, or hallucinate an answer. Instead, you MUST call the `escalate_to_human` tool to pass the conversation to a human.
- DO NOT invent or hallucinate products, prices, or policies under any circumstances.
- If a product is out of stock (Stock: 0), inform the customer.

CHECKOUT:
- If the customer explicitly confirms they want to buy a product, use the `generate_payment_link` tool.
- Pass the exact price in NGN from the catalog to the tool (as an integer).

FEEDBACK/RESOLUTION:
- When the conversation seems fully resolved (e.g., the customer says 'thanks', 'goodbye', or has no more questions), you MUST call the `mark_resolved` tool instead of saying goodbye. Do not use this tool until the issue is fully addressed.

RESPONSE LENGTH & FORMATTING:
1. Replies must be as short as possible while still fully answering the question.
2. NO repeating the question back, NO filler like "Thank you for asking", NO over-explaining.
3. BOLD FORMATTING: NEVER use double-asterisk markdown (**text**). You MUST use a single asterisk on each side instead (*text*). 
4. Apply bold ONLY to: the product name in a listing, the price, and the business name in the opening greeting. Do NOT bold full sentences.
Example product listing: *Product Name* - NGN Price
Example greeting: *This is {business.name}*, Hi! How can I help you today?

TONE: {tone}
"""

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY is missing!")
        return ("The AI agent is currently offline due to a missing API key.", False, False, False, 0)

    model = "openai/gpt-oss-120b"
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "escalate_to_human",
                "description": "Call this tool when the customer asks a question that is NOT explicitly covered by the provided knowledge base or product catalogue.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mark_resolved",
                "description": "Call this tool when the customer's query has been completely answered and the conversation seems resolved (e.g., they say thank you or goodbye).",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]
    
    if business.paystack_subaccount_code:
        tools.append({
            "type": "function",
            "function": {
                "name": "generate_payment_link",
                "description": "Generates a checkout link for the customer to pay for their order via Paystack.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount_ngn": {
                            "type": "integer",
                            "description": "The total amount to charge in NGN."
                        }
                    },
                    "required": ["amount_ngn"]
                }
            }
        })
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": incoming_message}
        ],
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.2
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                timeout=30.0
            )
            
            data = res.json()
            if res.status_code != 200:
                logger.error(f"Groq API Error: {data}")
                if "does not exist" in str(data):
                    logger.warning(f"Model {model} failed. Falling back to llama3-8b-8192 for testing.")
                    payload["model"] = "llama3-8b-8192"
                    res = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}"},
                        json=payload,
                        timeout=30.0
                    )
                    data = res.json()
                else:
                    return ("Sorry, I am having trouble connecting to my brain right now.", False, False, False, 0)

            total_tokens = 0
            if "usage" in data:
                total_tokens = data["usage"].get("total_tokens", 0)
            elif "x_groq" in data and "usage" in data["x_groq"]:
                total_tokens = data["x_groq"]["usage"].get("total_tokens", 0)

            if total_tokens > 0:
                async with async_session() as db:
                    biz_res = await db.execute(select(Business).where(Business.id == business_id))
                    biz = biz_res.scalar_one_or_none()
                    if biz:
                        biz.total_tokens_used += total_tokens
                        await db.commit()

            message_data = data["choices"][0]["message"]
            
            if message_data.get("tool_calls"):
                for tool_call in message_data["tool_calls"]:
                    if tool_call["function"]["name"] == "escalate_to_human":
                        return (None, True, False, False, total_tokens)
                    elif tool_call["function"]["name"] == "mark_resolved":
                        return (None, False, True, False, total_tokens)
                    elif tool_call["function"]["name"] == "generate_payment_link":
                        # Generate the link using Paystack
                        args = json.loads(tool_call["function"]["arguments"])
                        amount = args.get("amount_ngn", 0)
                        
                        if amount > 0 and business.paystack_subaccount_code:
                            # 1 NGN = 100 kobo
                            amount_kobo = amount * 100
                            # generate dummy email if needed
                            cust_email = f"customer_{customer_identifier or 'unknown'}@forrcustomers.test"
                            
                            paystack_res = await initialize_transaction(
                                email=cust_email,
                                amount=amount_kobo,
                                metadata={"conversation_id": str(conversation_id), "business_id": str(business_id)},
                                subaccount=business.paystack_subaccount_code
                            )
                            
                            if paystack_res.get("status"):
                                checkout_url = paystack_res["data"]["authorization_url"]
                                ref = paystack_res["data"]["reference"]
                                
                                # Store the payment
                                async with async_session() as db:
                                    payment = Payment(
                                        business_id=business.id,
                                        conversation_id=conversation_id,
                                        amount=amount_kobo,
                                        status="pending",
                                        paystack_reference=ref,
                                        customer_identifier=customer_identifier
                                    )
                                    db.add(payment)
                                    await db.commit()
                                
                                response_text = f"Here is your secure checkout link to pay NGN {amount}: {checkout_url}\nFunds are settled securely via Paystack."
                                return (response_text, False, False, False, total_tokens)
                            else:
                                return ("Sorry, I was unable to generate a payment link at this time.", False, False, False, total_tokens)
                        
            
            return (message_data.get("content", "Sorry, I didn't understand that."), False, False, False, total_tokens)
            
    except Exception as e:
        logger.error(f"Error calling LLM: {str(e)}")
        return ("Sorry, I encountered an internal error while trying to process your request.", False, False, False, 0)
