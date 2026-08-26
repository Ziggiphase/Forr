import os
import json
from groq import Groq
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

def parse_text_with_llm(raw_text: str) -> List[Dict[str, Any]]:
    """
    Sends unstructured text to Groq LLM to extract products matching our schema.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    system_prompt = """
    You are an expert data extraction assistant. Your job is to extract products from unstructured text.
    Return ONLY a valid JSON object with a single key "products", containing a list of products.
    Each product MUST have exactly these keys:
    - name (string)
    - price (number)
    - description (string)
    - quantity (number)
    - category (string)
    
    If the text lacks a price or quantity, default to 0. If category is unclear, default to "Other".
    Do NOT include any markdown formatting like ```json. Return pure JSON.
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"Extract products from this text:\n\n{raw_text}",
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    response_content = chat_completion.choices[0].message.content
    try:
        parsed = json.loads(response_content)
        return parsed.get("products", [])
    except json.JSONDecodeError:
        return []
