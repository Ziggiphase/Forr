# Ifosiwewe: Deep Codebase Breakdown

This document provides a deep, line-by-line breakdown of the core engine of the Forr platform. Because a literal line-by-line breakdown of every single file (including CSS and configs) would be thousands of pages long, this *ifosiwewe* (deep breakdown) focuses on the most critical files that make the AI, Messaging, and Database connect to one another.

---

## 1. The Brain: ackend/app/services/agent.py

This file is the core of the platform. It connects the database (to get the business products and limits), the LLM (Groq), and Paystack.

\\\python
async def generate_agent_response(business_id: str, incoming_message: str, conversation_id: str = None, customer_identifier: str = None) -> tuple[str | None, bool, bool, bool, int]:
\\\
- **Line 1:** We define an asynchronous function that takes the usiness_id, what the customer said (incoming_message), and tracking IDs. It returns a tuple containing the AI's reply, escalation flags, and tokens used.

\\\python
    async with async_session() as db:
        biz_res = await db.execute(select(Business).where(Business.id == business_id))
        business = biz_res.scalar_one_or_none()
\\\
- **Lines 2-4:** We open a connection to the PostgreSQL database. We query the usinesses table to find the specific business the customer is talking to.

\\\python
        tier = subscription.plan_tier if subscription else "free"
        limit = 50
        if tier == "pro": limit = 500
        elif tier == "premium": limit = 5000
        if usage >= limit:
            # send email to owner and return limit reached
\\\
- **Lines 5-10:** This connects the Billing system to the AI. It checks what subscription tier the business is on. If the business has had more conversations (usage) than their tier allows, it stops the AI from replying and emails the owner.

\\\python
    system_prompt = f"""You are an AI customer support and sales agent for '{business.name}'.
    ...
    TONE: {business.agent_tone}"""
\\\
- **Lines 11-13:** We construct the "System Prompt". This is the strict instruction set sent to the Groq LLM. We dynamically inject the business's name, their available products, and the custom tone the business owner set in the frontend dashboard.

\\\python
    tools = [ { "type": "function", "function": { "name": "escalate_to_human" ... } } ]
    if business.paystack_subaccount_code:
        tools.append({ "type": "function", "function": { "name": "generate_payment_link" ... } })
\\\
- **Lines 14-17:** We define "Tools" (Function Calling). We tell the AI that if a user asks a question it doesn't know, it should trigger escalate_to_human. If the business has connected Paystack (paystack_subaccount_code), we give the AI the generate_payment_link tool so it can charge customers.

\\\python
    res = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload)
\\\
- **Line 18:** We make an HTTP POST request to Groq's API, passing our prompt and tools.

\\\python
    if tool_call["function"]["name"] == "generate_payment_link":
        paystack_res = await initialize_transaction(email=cust_email, amount=amount_kobo, subaccount=business.paystack_subaccount_code)
\\\
- **Lines 19-20:** If the AI decided to charge the customer, we intercept that decision. We call our paystack.py service, passing the money amount and the business's subaccount. Paystack returns a secure checkout URL, which we then send back to the customer.

---

## 2. The Inbox Router: ackend/app/services/inbox.py

This file connects the Webhooks (Twilio/WhatsApp) and Telegram Poller to the gent.py brain.

\\\python
async def process_incoming_message(business_id: UUID, channel: str, customer_identifier: str, customer_name: str | None, content: str) -> str | None:
\\\
- **Line 1:** Called whenever a message arrives from *any* channel. 

\\\python
    query = select(Conversation).where(
        Conversation.business_id == business_id,
        Conversation.channel == channel,
        Conversation.customer_identifier == customer_identifier
    )
    conversation = result.scalar_one_or_none()
\\\
- **Lines 2-6:** It searches the database for an existing conversation between this specific business and this specific customer's phone number/chat ID. If it doesn't exist, it creates a new Conversation row.

\\\python
    incoming_message = Message(conversation_id=conversation.id, sender_type="customer", content=content)
    session.add(incoming_message)
\\\
- **Lines 7-8:** Saves the customer's text message to the database so it appears in the frontend dashboard.

\\\python
    if conversation.status == "ai_handling":
        ai_response = await generate_agent_response(business_id, content, conversation.id)
\\\
- **Lines 9-10:** It checks if the conversation is assigned to the AI. If a human hasn't taken over (manual), it calls the generate_agent_response function from gent.py to get an answer.

\\\python
        outgoing_message = Message(conversation_id=conversation.id, sender_type="ai", content=ai_response)
        session.add(outgoing_message)
        return ai_response
\\\
- **Lines 11-13:** It saves the AI's reply to the database and returns it back to the Webhook/Poller so it can be sent to the customer's phone.

---

## 3. The WhatsApp Webhook: ackend/app/api/webhooks.py

\\\python
@router.post("/twilio/whatsapp/{business_id}")
async def twilio_whatsapp_webhook(business_id: UUID, request: Request, db: AsyncSession = Depends(get_db)):
\\\
- **Line 1-2:** Defines an API endpoint. Twilio sends a POST request here every time someone messages a business's Twilio phone number.

\\\python
    form_data = await request.form()
    sender = form_data.get("From", "Unknown")
    body = form_data.get("Body", "")
\\\
- **Lines 3-5:** Extracts the sender's phone number and the text they sent from Twilio's incoming payload.

\\\python
    response = await process_incoming_message(business_id=business.id, channel="whatsapp", customer_identifier=sender, content=body)
\\\
- **Line 6:** Passes the extracted data into inbox.py to be processed and saved.

\\\python
    twiml_response = f"<?xml version='1.0' encoding='UTF-8'?><Response><Message>{response}</Message></Response>"
    return Response(content=twiml_response, media_type="application/xml")
\\\
- **Lines 7-8:** Formats the AI's reply into TwiML (XML format) because that is the only language Twilio understands, and sends it back as an HTTP response.

---

## 4. The Frontend Chat Interface: rontend/src/app/dashboard/businesses/[id]/inbox/page.tsx

This file connects the user interface to the backend database so business owners can chat with customers.

\\\	ypescript
const [conversations, setConversations] = useState<Conversation[]>([]);
const [messages, setMessages] = useState<Message[]>([]);
\\\
- **Lines 1-2:** React State variables. conversations holds the list of people chatting with the business. messages holds the chat bubbles for the currently clicked conversation.

\\\	ypescript
const fetchConversations = async () => {
  const res = await fetch(/api/v1/businesses//conversations);
  setConversations(await res.json());
}
\\\
- **Lines 3-6:** Makes an HTTP GET request to the backend inbox.py API to fetch all conversations and updates the UI.

\\\	ypescript
const fetchMessages = async (conversationId: string) => {
  const res = await fetch(/api/v1/conversations//messages);
  const data = await res.json();
  setMessages(prev => { ... filter and replace logic ... });
}
\\\
- **Lines 7-11:** Fetches all chat bubbles for a specific conversation. The complex filter logic ensures that if you switch between WhatsApp and Telegram rapidly, the messages do not bleed into each other on the screen.

\\\	ypescript
useEffect(() => {
  const intervalId = setInterval(() => fetchMessages(activeConversation.id), 5000);
  return () => clearInterval(intervalId);
}, [activeConversation]);
\\\
- **Lines 12-15:** This is a "Polling" loop. Every 5 seconds (5000ms), it automatically re-fetches messages from the backend so that when the AI or customer replies, it pops up on the business owner's screen in real-time without needing to refresh the page.

\\\	ypescript
const sendMessage = async () => {
  await fetch(/api/v1/conversations//messages, { method: 'POST', body: JSON.stringify({ content }) });
  updateConversationStatus(activeConversation.id, 'manual');
}
\\\
- **Lines 16-19:** When the human business owner types a message and clicks send, it posts to the backend. Crucially, it automatically calls updateConversationStatus to change the chat from i_handling to manual, instantly pausing the AI so it doesn't interrupt the human.
