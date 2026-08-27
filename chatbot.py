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

# Prepare and load models
def prepare_models():
    print("Loading models...")
    subprocess.run(
        [FOUNDRY_EXE, "model", "load", CHAT_MODEL_NAME],
        capture_output=True, text=True, errors="replace"
    )
    response = httpx.get(f"{BASE_URL}/v1/models", timeout=30)
    active_models = [m["id"] for m in response.json().get("data", [])]
    chat_id = next((m for m in active_models if "phi-3.5" in m.lower() or "phi3" in m.lower()), None)
    if not chat_id:
        raise RuntimeError("Failed to load chat model!")
    print(f"Ready! Chat: {chat_id} | Embedding: {EMBED_MODEL}\n")
    return chat_id

# Compute cosine similarity
def compute_cosine_similarity(vec_a, vec_b):
    dot_product = sum(x * y for x, y in zip(vec_a, vec_b))
    return dot_product / (math.sqrt(sum(x * x for x in vec_a)) * math.sqrt(sum(y * y for y in vec_b)))

# Search paragraphs by query
def search_paragraphs(query_text):
    api_response = client.embeddings.create(model=EMBED_MODEL, input=query_text)
    query_vector = api_response.data[0].embedding

    db_connection = sqlite3.connect(DB_PATH)
    db_cursor = db_connection.cursor()
    db_cursor.execute("SELECT title, context, embedding FROM documents")
    rows = db_cursor.fetchall()
    db_connection.close()

    score_list = []
    for title, context, emb_json in rows:
        if emb_json:
            similarity_score = compute_cosine_similarity(query_vector, json.loads(emb_json))
            score_list.append({"title": title, "context": context, "score": similarity_score})

    score_list.sort(key=lambda x: x["score"], reverse=True)
    return score_list[:3]

# Ask question to RAG
def ask_question(query_text, chat_model_id):
    search_results = search_paragraphs(query_text)
    highest_score = search_results[0]["score"] if search_results else 0

    if highest_score < SCORE_THRESHOLD:
        return "I don't have enough information on this topic in my knowledge base.", []

    combined_context = "\n\n".join(
        f"[{res['title']}]\n{res['context']}" for res in search_results
    )

    chat_response = client.chat.completions.create(
        model=chat_model_id,
        messages=[
            {"role": "system", "content":
                "You are a helpful assistant. Answer ONLY using the provided context. "
                "If the answer isn't in the context, say you don't know."},
            {"role": "user", "content": f"Context:\n{combined_context}\n\nQuestion: {query_text}"},
        ],
        max_tokens=300,
        temperature=0.1,
    )
    sources = list(dict.fromkeys(res["title"] for res in search_results))
    return chat_response.choices[0].message.content.strip(), sources

# Main execution loop
def main():
    print("=" * 55)
    print("  OFFLINE RAG CHATBOT  (Foundry Local + SQLite)")
    print("=" * 55)
    print("  Knowledge base: SQuAD dataset (600 paragraphs)")
    print("  Model: phi-3.5-mini  |  Fully offline")
    print("  To exit type: 'quit' or 'exit'")
    print("=" * 55)

    chat_model_id = prepare_models()

    while True:
        print()
        query = input("User: ").strip()

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print("Thinking", end="", flush=True)
        answer, sources = ask_question(query, chat_model_id)
        print("\r" + " " * 20 + "\r", end="")

        print(f"Assistant: {answer}")
        if sources:
            print(f"[Sources: {', '.join(sources)}]")

if __name__ == "__main__":
    main()