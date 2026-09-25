# Zepto Support Assistant

## Setup and Run

```bash
cd support_assistant
pip install -r requirements.txt
uvicorn src.assistant:app --reload
```

`MOCK_LLM` is unset by default (equivalent to `MOCK_LLM=1`), so requests are deterministic and make no network LLM calls.

## Architecture

1. **Ingestion:** `src/assistant.py::_load_records` reads the eight exact policy files in `docs/`, using one document as one chunk and assigning each chunk its `doc_XX` ID.
2. **Embedding:** `build_collection` embeds chunks with the local `all-MiniLM-L6-v2` SentenceTransformer and stores them in the persistent ChromaDB collection `zepto_policies` with cosine distance. A small lexical fallback is used only when optional packages are unavailable.
3. **Retrieval:** The LangGraph `retrieve_and_answer` node embeds the incoming query and asks ChromaDB for the top three chunks. Retrieval runs in both mock and real modes.
4. **Generation:** `retrieve_and_answer` creates the grounded response and `direct_answer` handles general queries. `STRUCTURED_PROMPT` contains the role, context, task, format, length, negative constraint, and few-shot example. Both paths return the `AnswerResponse` Pydantic schema.

The `classify_intent` node routes policy keywords to retrieval and all other queries to `direct_answer`. In default mock mode, classification and generation are deterministic: policy answers start with `Based on the retrieved context:` and general answers use a fixed refusal. With `MOCK_LLM=0`, classification and generation use the optional Groq integration; structured generation retries twice with a corrective instruction if validation fails.

## Example Calls (mock mode)

```bash
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d "{\"query\":\"What is the delivery fee?\"}"
```

```json
{"answer":"Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del","sources":["doc_01","doc_04","doc_03"],"confidence":1.0}
```

```bash
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d "{\"query\":\"What is the weather today?\"}"
```

```json
{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}
```

## Docker

```bash
docker build -t zepto-support .
docker run --rm -p 7860:7860 zepto-support
```

The container serves `POST /ask` on port 7860. A live deployment and real LLM provider are optional and are not required for the graded baseline.
