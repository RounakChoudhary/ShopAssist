import time
import uuid
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from classifier import classify_intent
from router import handle_routing
from session_store import get_history, append_turn

app = FastAPI(title="ShopAssist", version="1.0.0")

# Define request model for chat endpoint
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None   # client echoes back what we gave them last time;
                                     # omitted/None on their very first message

# define request model for health check endpoint
@app.get("/")
async def root():
    print("[DEV LOG] Health Check hit on Root Endpoint.")
    return {"status": "online", "message": "ShopAssist Backend is running"}

# define chat endpoint for processing user messages
@app.post("/chat")
async def chat(request: ChatRequest):
    start_time = time.perf_counter()
    session_id = request.session_id or str(uuid.uuid4())

    try:
        # pull whatever context we have for this session (empty list if new
        # session, or if Redis is having a bad day - see session_store)
        conversation_history = await get_history(session_id)

        # Gatekeeper Engine
        intent_decision = await classify_intent(request.message, conversation_history=conversation_history)

        # Route Execution
        final_payload = await handle_routing(intent_decision, request.message, conversation_history=conversation_history)

        # stash this exchange for next time, regardless of which route handled it
        await append_turn(session_id, "user", request.message)
        await append_turn(session_id, "assistant", final_payload.get("response", ""))

        # Dev metrics tracking block
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        print(f"[DEV METRICS] Success | Intent: {intent_decision.get('intent')} | Confidence: {intent_decision.get('confidence')} | Latency: {latency}ms")

        return {**final_payload, "session_id": session_id}

    except HTTPException as http_ex:
        # Dev logging for HTTPException raised in downstream routing or classification
        print(f"[DEV WARNING] Handled HTTP Exception Raised: Code {http_ex.status_code} - {http_ex.detail}")
        raise http_ex

    except Exception as e:
        # Catch all for any unhandled exceptions
        print(f"[DEV CRITICAL CRASH] Absolute failure in /chat endpoint execution lifecycle: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error.")