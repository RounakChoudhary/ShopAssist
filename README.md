# ShopAssist 

ShopAssist is an AI-powered assistant designed for e-commerce platforms to help users discover products, compare specifications, and navigate shopping decisions.

This repository currently houses the **core backend service**, which is structured as a multi-step routing pipeline to process user queries efficiently.

---

##  The Architecture (Current Phase)

To save on API token usage and keep response times fast, incoming messages don't just blindly hit a heavy language model. Instead, the backend uses a **4-Way Intent Router** powered by a fast, deterministic model (`llama-3.1-8b-instant`):

```text
               [ User Input ]
                     │
                     ▼
          ┌─────────────────────┐
          │  Intent Classifier  │
          └─────────────────────┘
                     │
     ┌───────────────┼───────────────┬───────────────┐
     ▼               ▼               ▼               ▼
[ greetings ] [ database_query ] [ main_llm ]  [ irrelevant ]
     │               │               │               │
 (Hardcoded      (Direct DB      (Deep LLM       (Polite
  response)      lookup ready)   Reasoning)      Refusal)
```

1. **Greetings:** Basic hellos are caught here and served random pre-defined responses without using any LLM completion text.
2. **Database Query:** Identifies pure catalog lookups (e.g., filtering by price or category) so we can later bypass the LLM and query the store database directly.
3. **Main LLM:** Routes complex requests (comparisons, product recommendations, shopping advice) to the primary reasoning model.
4. **Irrelevant:** Catches out-of-domain queries (like general coding requests or homework help) and politely asks the user to stay on the topic of shopping.

---

##  Project Roadmap

- [x] **Phase 1 & 2:** Initial FastAPI setup, Groq API integration, and basic e-commerce system persona.
- [x] **Phase 3:** 4-Way Intent Routing Gateway with strict JSON validation.
- [ ] **Phase 4 (Next):** Database integration to fulfill `database_query` routes natively.
- [ ] **Phase 5:** Adding conversation memory tracking, caching, and rate-limiting.
- [ ] **Phase 6:** Building the Frontend interface and connecting it end-to-end.

---

##  Tech Stack

- **Framework:** FastAPI (Python)
- **LLM Engine:** Groq Async Client SDK (`llama-3.1-8b-instant`)
- **Validation:** Pydantic v2

---

##  Local Setup Guide

### 1. Environment Setup

Clone the repository and set up your Python virtual environment:

```bash
git clone https://github.com/RounakChoudhary/ShopAssist.git
cd ShopAssist

python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn openai python-dotenv
```

### 3. Add API Keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_groq_api_key_here
```

> **Note:** If you're using the Groq SDK, replace the variable name with whatever your application expects (for example, `GROQ_API_KEY`).

### 4. Run the Backend

```bash
uvicorn main:app --reload
```

Open your browser to:

```
http://127.0.0.1:8000/docs
```

to interact with and test the chat endpoints through the built-in Swagger interface.