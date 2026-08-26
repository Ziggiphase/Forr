import asyncio
from dotenv import load_dotenv
load_dotenv()
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from app.models.user import User  # To populate SQLAlchemy registry
from app.services.agent import generate_agent_response

async def run_tests():
    business_id = "edc22413-7234-4c44-8d09-b9227adb5008"
    
    print("\n--- TEST 1: Ask about a real product ---")
    reply1 = await generate_agent_response(business_id, "Do you have any shoes?")
    print(f"AI Response: {reply1}\n")
    
    print("\n--- TEST 2: Ask about the delivery fee ---")
    reply2 = await generate_agent_response(business_id, "How much does delivery cost?")
    print(f"AI Response: {reply2}\n")
    
    print("\n--- TEST 3: Ask about something NOT in the catalogue ---")
    reply3 = await generate_agent_response(business_id, "Can I buy a helicopter?")
    print(f"AI Response: {reply3}\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
