import json
from fastapi import HTTPException
from config import client
from prompts import INTENT_CLASSIFIER_PROMPT
from session_store import trim_history

async def classify_intent(user_message: str, conversation_history: list[dict] | None = None) -> dict:
    """
    Calls the cheap gatekeeper model to extract intent, confidence, and reasoning.
    Falls back to 'main_llm' structure if JSON serialization or parsing collapses.
    """
    raw_content = None
    try:
        trimmed = trim_history(conversation_history, max_turns=2)

        messages = [
            {"role": "system", "content": INTENT_CLASSIFIER_PROMPT},
            *trimmed,
            {"role": "user", "content": user_message},
        ]

        guard_response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2,
            max_tokens=100,
            response_format={"type": "json_object"}
        )

        raw_content = guard_response.choices[0].message.content
        guard_data = json.loads(raw_content)

        VALID_INTENTS = {
            "greetings",
            "database_query",
            "policy_query",
            "main_llm",
            "irrelevant"
        }

        if guard_data.get("intent") not in VALID_INTENTS:
            guard_data["intent"] = "main_llm"
            guard_data["confidence"] = "low"

        return guard_data

    except json.JSONDecodeError as json_err:
        print(f"[DEV WARNING] Gatekeeper JSON broken: {str(json_err)} | Content: {raw_content}")
        return {"intent": "main_llm", "confidence": "low", "reason": "JSON decode failure"}

    except Exception as e:
        print(f"[DEV ERROR] Gatekeeper system level crash: {str(e)}")
        return {"intent": "main_llm", "confidence": "low", "reason": "Upstream service failure"}