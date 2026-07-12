import random
from fastapi import HTTPException
from config import client, GREETING_RESPONSES
from prompts import SHOPASSIST_SYSTEM_PROMPT

async def handle_routing(intent_data: dict, user_message: str) -> dict:
    intent = intent_data.get("intent")
    confidence = intent_data.get("confidence", "high")

    # if the gatekeeper has low confidence, we choose to route to the main_llm for ensuring that ambiguous queries receive accurate responses
    if confidence == "low" and intent != "main_llm":
        print(f"[DEV LOG] Low confidence detected on '{intent}'. Falling back to main_llm execution.")
        intent = "main_llm"

    # Route 1: Irrelevant Refusal
    if intent == "irrelevant":
        return {
            "response": "I'm here to help you shop! I can't assist with that request, but I can help you find products, compare options, or answer questions about shopping."
        }

    # Route 2: Static Greetings
    elif intent == "greetings":
        return {"response": random.choice(GREETING_RESPONSES)}

    # Route 3: Database Search
    elif intent == "database_query":
        # Placeholder entry point for PostGIS / Postgres integration later
        print("[DEV LOG] Routing directly to Database Branch...")
        return {"response": "Gatekeeper classified this as a database query"}

    # Route 4: Main Reasoning LLM Agent
    else:
        try:
            print("[DEV LOG] Invoking Main Shopping LLM Execution...")
            response = await client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SHOPASSIST_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.4,
                max_tokens=300
            )
            return {"response": response.choices[0].message.content}
            
        except Exception as llm_err:
            print(f"[DEV ERROR] Main Shopping LLM API Call Failed: {str(llm_err)}")
            raise HTTPException(status_code=502, detail="Shopping intelligence layer down.")