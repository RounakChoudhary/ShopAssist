import json
from fastapi import HTTPException
from config import client
from prompts import INTENT_CLASSIFIER_PROMPT

async def classify_intent(user_message: str) -> dict:
    """
    Calls the cheap gatekeeper model to extract intent, confidence, and reasoning.
    Falls back to 'main_llm' structure if JSON serialization or parsing collapses.
    """
    try:
        # Involve the gatekeeper LLM to classify the intent of user message
        guard_response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": INTENT_CLASSIFIER_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            max_tokens=100, 
            response_format={"type": "json_object"}
        )
        
        raw_content = guard_response.choices[0].message.content
        guard_data = json.loads(raw_content)
        
        # If model outputs invalid structure keys, normalize safely
        if "intent" not in guard_data:
            guard_data["intent"] = "main_llm"
            guard_data["confidence"] = "low"
            
        return guard_data

    except json.JSONDecodeError as json_err:
        print(f"[DEV WARNING] Gatekeeper JSON broken: {str(json_err)} | Content: {raw_content}")
        # Safely fallback to main_llm if JSON parsing fails
        return {"intent": "main_llm", "confidence": "low", "reason": "JSON decode failure"}
        
    except Exception as e:
        print(f"[DEV ERROR] Gatekeeper system level crash: {str(e)}")
        return {"intent": "main_llm", "confidence": "low", "reason": "Upstream service failure"}