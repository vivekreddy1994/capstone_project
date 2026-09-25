import os
import re
from pathlib import Path
from typing import List, TypedDict

from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from .prompts import Prompts
except ImportError:
    from prompts import Prompts

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:
    END, START = "__end__", "__start__"

    class StateGraph:
        def __init__(self, state_type):
            self.nodes, self.edges, self.conditional = {}, {}, None

        def add_node(self, name, function):
            self.nodes[name] = function

        def add_edge(self, source, target):
            self.edges[source] = target

        def add_conditional_edges(self, source, router, mapping):
            self.conditional = (source, router, mapping)

        def compile(self):
            graph = self

            class Compiled:
                def invoke(self, state):
                    current = graph.edges[START]
                    while current != END:
                        state.update(graph.nodes[current](state))
                        if graph.conditional and current == graph.conditional[0]:
                            current = graph.conditional[2][graph.conditional[1](state)]
                        else:
                            current = graph.edges.get(current, END)
                    return state

            return Compiled()

try:
    import chromadb
except Exception:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
MOCK_LLM = os.getenv("MOCK_LLM", "1") != "0"
POLICY_KEYWORDS = ("delivery", "return", "refund", "membership", "tracking", "cancel", "gift card", "support hours")


class AnswerResponse(BaseModel):
    answer: str
    sources: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class AskRequest(BaseModel):
    query: str


class GraphState(TypedDict, total=False):
    query: str
    intent: str
    retrieved: List[dict]
    response: AnswerResponse


STRUCTURED_PROMPT = """ROLE: You are a precise Zepto customer-support policy assistant.
CONTEXT: Answer only from these retrieved Zepto policy chunks:
{context}
TASK: Answer the user's question and cite only the chunk IDs that support it.
FORMAT: Return JSON with exactly answer (string), sources (list of chunk IDs), and confidence (number from 0 to 1).
LENGTH: Keep the answer concise, under 80 words.
CONSTRAINT: Do not answer using information not present in the provided context; do not invent policy.
FEW-SHOT EXAMPLE:
Question: How long can I report a damaged grocery item?
Context: doc_02: Grocery and perishable items may be reported within 24 hours.
Answer: {{"answer":"Damaged grocery items may be reported within 24 hours of delivery.","sources":["doc_02"],"confidence":1.0}}
Question: {query}
"""


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _local_embedding(text: str) -> List[float]:
    vocabulary = ("delivery", "return", "refund", "membership", "tracking", "cancel", "gift", "card", "support", "hours", "order", "item", "payment", "price", "time")
    tokens = _tokens(text)
    return [float(tokens.count(word)) for word in vocabulary]


class LocalCollection:
    def __init__(self, records):
        self.records = records

    def query(self, query_embeddings, n_results=3):
        query = query_embeddings[0]
        scored = []
        for record in self.records:
            vector = record["embedding"]
            dot = sum(a * b for a, b in zip(query, vector))
            norm = (sum(a * a for a in query) * sum(b * b for b in vector)) ** 0.5
            scored.append((dot / norm if norm else 0.0, record))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        chosen = [record for _, record in scored[:n_results]]
        return {"ids": [[record["id"] for record in chosen]], "documents": [[record["document"] for record in chosen]]}


def _load_records():
    records = []
    for path in sorted(DOCS_DIR.glob("doc_*.txt")):
        document = path.read_text(encoding="utf-8")
        records.append({"id": path.stem, "document": document, "embedding": _local_embedding(document)})
    return records


def build_collection():
    records = _load_records()
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2") if SentenceTransformer else None
    except Exception:
        model = None
    if model:
        for record, vector in zip(records, model.encode([r["document"] for r in records]).tolist()):
            record["embedding"] = vector
    if chromadb:
        client = chromadb.PersistentClient(path=str(ROOT / "chroma_db"))
        collection = client.get_or_create_collection(name="zepto_policies", metadata={"hnsw:space": "cosine"})
        if collection.count() == 0:
            collection.add(ids=[r["id"] for r in records], documents=[r["document"] for r in records], embeddings=[r["embedding"] for r in records])
        return collection, model
    return LocalCollection(records), model


COLLECTION, EMBEDDING_MODEL = build_collection()


def classify_intent(state: GraphState) -> dict:
    query = state["query"]
    if MOCK_LLM:
        intent = "policy_question" if any(keyword in query.lower() for keyword in POLICY_KEYWORDS) else "general_question"
    else:
        intent = _real_classification(query)
    return {"intent": intent}


def _embed_query(query: str):
    return EMBEDDING_MODEL.encode([query]).tolist()[0] if EMBEDDING_MODEL else _local_embedding(query)


def retrieve_and_answer(state: GraphState) -> dict:
    result = COLLECTION.query(query_embeddings=[_embed_query(state["query"])], n_results=3)
    retrieved = [{"id": item_id, "document": document} for item_id, document in zip(result["ids"][0], result["documents"][0])]
    if MOCK_LLM:
        response = AnswerResponse(answer=f"Based on the retrieved context: {retrieved[0]['document'][:200]}", sources=[item["id"] for item in retrieved], confidence=1.0)
    else:
        response = _real_structured_answer(state["query"], retrieved)
    return {"retrieved": retrieved, "response": response}


def direct_answer(state: GraphState) -> dict:
    response = AnswerResponse(answer="I can only answer questions about Zepto policies right now.", sources=[], confidence=1.0) if MOCK_LLM else _real_structured_answer(state["query"], [])
    return {"response": response}


def route_intent(state: GraphState) -> str:
    return state["intent"]


def create_graph():
    builder = StateGraph(GraphState)
    builder.add_node("classify_intent", classify_intent)
    builder.add_node("retrieve_and_answer", retrieve_and_answer)
    builder.add_node("direct_answer", direct_answer)
    builder.add_edge(START, "classify_intent")
    builder.add_conditional_edges("classify_intent", route_intent, {"policy_question": "retrieve_and_answer", "general_question": "direct_answer"})
    builder.add_edge("retrieve_and_answer", END)
    builder.add_edge("direct_answer", END)
    return builder.compile()


def _real_classification(query: str) -> str:
    from langchain_groq import ChatGroq
    result = ChatGroq(model="llama-3.1-8b-instant", temperature=0).invoke(f"Classify this query as policy_question or general_question: {query}")
    return "policy_question" if "policy_question" in result.content else "general_question"


def _real_structured_answer(query: str, retrieved: List[dict]) -> AnswerResponse:
    from langchain_groq import ChatGroq
    context = "\n".join(f"{item['id']}: {item['document']}" for item in retrieved)
    prompt = STRUCTURED_PROMPT.format(context=context, query=query)
    model = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    for attempt in range(3):
        try:
            raw = model.invoke(prompt if attempt == 0 else prompt + "\nCorrect your previous output and return only valid JSON matching the schema.")
            content = raw.content if hasattr(raw, "content") else raw
            if hasattr(AnswerResponse, "model_validate_json"):
                return AnswerResponse.model_validate_json(content)
            return AnswerResponse.parse_raw(content)
        except Exception as error:
            last_error = error
    return AnswerResponse(answer=f"ERROR: unable to validate LLM response after 3 attempts ({last_error})", sources=[], confidence=0.0)


graph = create_graph()
app = FastAPI(title="Zepto Support Assistant")


@app.post("/ask", response_model=AnswerResponse)
def ask(request: AskRequest) -> AnswerResponse:
    return graph.invoke({"query": request.query})["response"]


class Assistant:
    def get_prompt(self, name):
        prompts = {
            "greeting": "Hello! How can I assist you today?",
            "faq": Prompts.FAQ_PROMPT,
            "goodbye": Prompts.GOODBYE_MESSAGE,
        }
        return prompts.get(name, Prompts.WELCOME_MESSAGE)

    def handle_query(self, query):
        return ask(AskRequest(query=query)).answer

    def process_request(self, query):
        return bool(self.handle_query(query))


def handle_user_query(query):
    return Assistant().handle_query(query)


def provide_response(response):
    return f"Assistant: {response}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
