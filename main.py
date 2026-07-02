import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv 
from prompts import SHOPASSIST_SYSTEM_PROMPT, INTENT_CLASSIFIER_PROMPT
load_dotenv()

app = FastAPI(title="ShopAssist", version="1.0.0")

# Retrieve the OpenAI API key from the environment or .env file
llm_api_key = os.getenv("OPENAI_API_KEY")
if not llm_api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment variables.")

# Initialize the user with the provided API key and the Groq Api endpoint
client = AsyncOpenAI(
    api_key = llm_api_key,
    base_url = "https://api.groq.com/openai/v1"
    )

# Create an instance of the client to interact with chatbot
class ChatRequest(BaseModel):
    message: str

# Define a list of greeting responses to use in the chatbot (Hard coded them instead of using LLM to save cost and reduce latency)
GREETING_RESPONSES = [
    "Hello! How can I assist you with your shopping today?",
    "Hi there! Looking for something special?",
    "Greetings! What can I help you find today?",
    "Hey! Ready to explore some great products?",
    "Good day! How can I make your shopping experience better?"
]  
  
# Define the root endpoint to check if the backend is running     
@app.get("/")
async def root():
    print("ShopAssist Backend is running")
    return {"status": "online", "message": "ShopAssist Backend is running"}    
              
# Define the endpoint to handle chat requests              
@app.post("/chat")
async def chat(request: ChatRequest):
    try: 
        #────────────── 
        # THE  GATEKEEPER LLM
        #──────────────
            
            # We use a smaller, faster configuration (low temperature, low max_tokens)
            guard_response = await client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Keeping it cheap and fast
                messages=[
                    {"role": "system", "content": INTENT_CLASSIFIER_PROMPT},
                    {"role": "user", "content": request.message}
                ],
                temperature=0.2,  # 0.0 makes it highly deterministic for classification
                max_tokens=50,
                response_format={"type": "json_object"} # Forces the model to respond in valid JSON
            )
            
            # Parse the gatekeeper's decision
            try:
                guard = json.loads(guard_response.choices[0].message.content)
                prompt_intent = guard.get("intent")
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code = 500,
                    detail = "Gatekeeper LLM returned invalid JSON. Please check the prompt and model configuration."
                )

            # If the gatekeeper blocks it, stop immediately and return the refusal
            if prompt_intent == "irrelevant":
                return {
                    "response": "I'm here to help you shop! I can't assist with that request, but I can help you find products, compare options, or answer questions about shopping."
                }
            
            # If the gatekeeper classifies it as a greeting, return a random greeting response
            elif prompt_intent == "greetings":
                import random
                return {"response": random.choice(GREETING_RESPONSES)}
            
            # If the gatekeeper classifies it as a database query, we can handle it without calling the main LLM 
            elif prompt_intent == "database_query":
                # ===== implementation for database query handling here =====
                return {"response" : "Gatekeeper classified this as a database query"}
            
            # If the gatekeeper classifies it as a main LLM request, we proceed to call the main LLM
            else:
                
                #────────────── 
                # THE MAIN SHOPPING LLM
                #──────────────

                # Passed the guardrail! Now we call our main processing pipeline
                response = await client.chat.completions.create(
                    model="llama-3.1-8b-instant", # For now we keep it fast and cost-effective, later we can scale this up to llama-3.3-70b
                    messages=[
                        {"role": "system", "content": SHOPASSIST_SYSTEM_PROMPT},
                        {"role": "user", "content": request.message}
                    ],
                    temperature=0.4,
                    max_tokens=300
                )

                ai_reply = response.choices[0].message.content
                return {"response": ai_reply}

    except Exception as e:
        print(f"Backend Exception: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error.")
        