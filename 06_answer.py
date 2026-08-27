# Import required libs
import sqlite3
import json
import math
import subprocess
import httpx
from openai import OpenAI

# Define config vars
FOUNDRY_EXE = r"C:\Users\Semre\AppData\Local\Microsoft\WindowsApps\foundry.exe"
BASE_URL = "http://127.0.0.1:51873"
EMBED_MODEL = "qwen3-embedding-0.6b-generic-cpu"
CHAT_MODEL_NAME = "phi-3.5-mini"
SCORE_THRESHOLD = 0.45
DB_PATH = "knowledge_base.db"

# Init OpenAI client
client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="foundry")

# Load chat model to RAM
def load_chat_model():
    print(f"Loading chat model to RAM: {CHAT_MODEL_NAME} (may take 1-2 minutes...)")
    load_result = subprocess.run(
        [FOUNDRY_EXE, "model", "load", CHAT_MODEL_NAME],
        capture_output=True, text=True, errors="replace"
    )
    print(load_result.stdout.strip() or "(load completed)")

    response = httpx.get(f"{BASE_URL}/v1/models", timeout=30)
    active_models = [m["id"] for m in response.json().get("data", [])]
    model_id = next((m for m in active_models if "phi-3.5" in m.lower() or "phi3" in m.lower()), None)

    if not model_id:
        raise RuntimeError(f"Failed to load chat model! Active models: {active_models}")
    print(f"Ready: {model_id}")
    return model_id

# Compute cosine similarity
def compute_cosine_similarity(vec_a, vec_b):
    dot_product = sum(x * y for x, y in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

# Search paragraphs by query
def search_paragraphs(query_text, top_k=3):
    api_response = client.embeddings.create(model=EMBED_MODEL, input=query_text)
    query_vector = api_response.data[0].embedding

    db_connection = sqlite3.connect(DB_PATH)
    db_cursor = db_connection.cursor()
    db_cursor.execute("SELECT id, title, context, embedding FROM documents")
    rows = db_cursor.fetchall()
    db_connection.close()

    score_list = []
    for doc_id, title, context, emb_json in rows:
        if emb_json is None:
            continue
        similarity_score = compute_cosine_similarity(query_vector, json.loads(emb_json))
        score_list.append({"title": title, "context": context, "score": similarity_score})

    score_list.sort(key=lambda x: x["score"], reverse=True)
    return score_list[:top_k]

# Run RAG answer pipeline
def rag_answer(query_text, chat_model_id):
    search_results = search_paragraphs(query_text, top_k=3)
    highest_score = search_results[0]["score"] if search_results else 0

    if highest_score < SCORE_THRESHOLD:
        return {
            "answer": "I don't have enough information on this topic in my knowledge base.",
            "sources": [],
            "highest_score": highest_score
        }

    context_parts = []
    for idx, res in enumerate(search_results, 1):
        context_parts.append(f"[Source {idx}: {res['title']}]\n{res['context']}")
    combined_context = "\n\n".join(context_parts)

    system_message = (
        "You are a helpful assistant. Answer the user's question using ONLY "
        "the provided context below. If the answer is not in the context, "
        "say 'I don't have that information in my knowledge base.' "
        "Keep your answer concise and accurate."
    )
    user_message = f"Context:\n{combined_context}\n\nQuestion: {query_text}"

    chat_response = client.chat.completions.create(
        model=chat_model_id,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        max_tokens=300,
        temperature=0.1,
    )

    return {
        "answer": chat_response.choices[0].message.content.strip(),
        "sources": [res["title"] for res in search_results],
        "highest_score": highest_score
    }

# Execute RAG tests
print("=" * 60)
print("RAG CHATBOT - Step 6")
print("=" * 60)

print("\nChecking chat model...")
active_chat_model_id = load_chat_model()

test_queries = [
    "When did the Scholastic Magazine of Notre Dame begin publishing?",
    "What is the boiling point of water?",
    "Who is the president of Notre Dame university?",
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print("-" * 60)
    result = rag_answer(query, active_chat_model_id)
    print(f"ANSWER: {result['answer']}")
    print(f"Score : {result['highest_score']:.4f} | Sources: {result['sources']}")

print(f"\n{'='*60}")
print("RAG pipeline is operational! Next step: interactive chatbot.")