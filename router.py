import random
from fastapi import HTTPException
from config import client, GREETING_RESPONSES
from prompts import SHOPASSIST_SYSTEM_PROMPT
from query_builder import run_query

# TEMPORARY: no param extraction wired yet, so every database_query request
# just returns top-ranked products with no filters applied. Real extraction
# of filters from user_message is the next step — this only proves the DB
# plumbing works end-to-end.
DEFAULT_PARAMS = {
    "category": None,
    "price_lt": None,
    "price_gt": None,
    "attributes": {},
    "sort": "best_rank",
    "limit": 5
}

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
        print("[DEV LOG] Routing directly to Database Branch...")
        try:
            params = intent_data.get("filters") or {}
            rows = run_query(params)
            print(f"params: {params}")
      
        except Exception as db_err:
            print(f"[DEV ERROR] Database query execution failed: {str(db_err)}")
            raise HTTPException(status_code=500, detail="Database query failed.")

        if not rows:
            return {"response": "I couldn't find any products matching that. Want to try different filters?"}

        # Format rows into a plain, scannable reply — no LLM call needed for this branch
        lines = []
        for row in rows:
            line = f"- {row['product_name']} ({row['category']}) — ${row['price']}"
            if row.get("stock_quantity") is not None:
                line += f", {row['stock_quantity']} in stock"
            if row.get("rating") is not None:
                line += f", {row['rating']}★ ({row.get('num_reviews', 0)} reviews)"
            lines.append(line)

        return {"response": "\n".join(lines)}

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