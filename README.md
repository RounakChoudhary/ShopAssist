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

### 1. Prerequisites

Make sure you have:

- Python 3.10+ installed
- Git available on your machine
- A local Redis instance running on `localhost:6379` (the backend uses Redis via the configured client)

### 2. Clone and Create a Virtual Environment

```bash
git clone https://github.com/RounakChoudhary/ShopAssist.git
cd ShopAssist

python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with your API key:

```env
OPENAI_API_KEY=your_groq_api_key_here
```

Optional variables you can override:

```env
POLICY_FOLDER=data
CHROMA_DB_PATH=chroma_db
CHROMA_COLLECTION_NAME=shop_policies
```

### 5. Build the Local Policy Index

Before using the chat flow, ingest the policy documents into the local Chroma vector store:

```bash
python -m scripts.ingest_policies
```

This step reads the Markdown policy files from the `data/` folder and creates or refreshes the local vector database under `chroma_db/`.

### 6. Run the Backend

Start the FastAPI application:

```bash
uvicorn main:app --reload
```

Open your browser to:

```text
http://127.0.0.1:8000/docs
```

You can test the API through the Swagger UI, including the `GET /` health check and the `POST /chat` endpoint.

### 7. Optional Verification

You can also run a sample retrieval check against the ingested policy index:

```bash
python -m scripts.query_policies
```