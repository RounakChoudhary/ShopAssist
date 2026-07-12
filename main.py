import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from classifier import classify_intent
from router import handle_routing

app = FastAPI(title="ShopAssist", version="1.0.0")

# Define request model for chat endpoint
class ChatRequest(BaseModel):
    message: str

# define request model for health check endpoint
@app.get("/")
async def root():
    print("[DEV LOG] Health Check hit on Root Endpoint.")
    return {"status": "online", "message": "ShopAssist Backend is running"}

# define chat endpoint for processing user messages
@app.post("/chat")
async def chat(request: ChatRequest):
    start_time = time.perf_counter()
    try:
        # Gatekeeper Engine
        intent_decision = await classify_intent(request.message)
        
        # Route Execution 
        final_payload = await handle_routing(intent_decision, request.message)
        
        # Dev metrics tracking block
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        print(f"[DEV METRICS] Success | Intent: {intent_decision.get('intent')} | Latency: {latency}ms")
        
        return final_payload

    except HTTPException as http_ex:
        # Dev logging for HTTPException raised in downstream routing or classification
        print(f"[DEV WARNING] Handled HTTP Exception Raised: Code {http_ex.status_code} - {http_ex.detail}")
        raise http_ex
        
    except Exception as e:
        # Catch all for any unhandled exceptions
        print(f"[DEV CRITICAL CRASH] Absolute failure in /chat endpoint execution lifecycle: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error.")