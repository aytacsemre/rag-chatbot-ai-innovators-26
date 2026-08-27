# Import required libs
import sqlite3
import json
import math
import httpx
from openai import OpenAI

# Define config vars
BASE_URL = "http://127.0.0.1:51873"
EMBED_MODEL = "qwen3-embedding-0.6b-generic-cpu"
CHAT_MODEL_ID = "Phi-3.5-mini-instruct-generic-cpu"
SCORE_THRESHOLD = 0.45
DB_PATH = "knowledge_base.db"
OUTPUT_PATH = "test_results.json"

# Init OpenAI client
client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="foundry")

# Define test cases
TEST_QUERIES = [
    # Questions present in database
    ("When did the Scholastic Magazine of Notre Dame begin publishing?",
     "ANSWER", "1876"),

    ("What sport does the Notre Dame Fighting Irish compete in?",
     "ANSWER", "football"),

    ("How many students attend Notre Dame?",
     "ANSWER", "12"),

    ("Who is the president of Notre Dame?",
     "ANSWER", "Jenkins"),

    ("Where was Frédéric Chopin born?",
     "ANSWER", "Żelazowa"),

    ("Who directed the film Spectre?",
     "ANSWER", "Mendes"),

    # Questions NOT present in database
    ("What is the capital of France?",
     "UNKNOWN", ""),

    ("Who invented the telephone?",
     "UNKNOWN", ""),

    ("What is photosynthesis?",
     "UNKNOWN", ""),

    ("What is the speed of light?",
     "UNKNOWN", ""),
]

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

# Execute query against RAG pipeline
def ask_question(query_text):
    search_results = search_paragraphs(query_text)
    highest_score = search_results[0]["score"] if search_results else 0

    if highest_score < SCORE_THRESHOLD:
        return "I don't have enough information on this topic in my knowledge base.", highest_score

    relevant_docs = [res for res in search_results if res["score"] >= SCORE_THRESHOLD]
    combined_context = "\n\n".join(f"[{res['title']}]\n{res['context']}" for res in relevant_docs)

    chat_response = client.chat.completions.create(
        model=CHAT_MODEL_ID,
        messages=[
            {"role": "system", "content":
                "Answer ONLY using the provided context. If not in context, say you don't know."},
            {"role": "user", "content": f"Context:\n{combined_context}\n\nQuestion: {query_text}"}
        ],
        max_tokens=200,
        temperature=0.1,
    )
    return chat_response.choices[0].message.content.strip(), highest_score

# Run systematic test suite
print("=" * 65)
print("  SYSTEMATIC TEST REPORT")
print("=" * 65)

success_count = 0
fail_count = 0
results_list = []

for query, expected_status, expected_content in TEST_QUERIES:
    print(f"\nQUERY: {query}")
    answer, score = ask_question(query)

    is_unknown = "knowledge base" in answer.lower() or "don't know" in answer.lower() or "not available" in answer.lower()

    if expected_status == "UNKNOWN":
        is_successful = is_unknown
    else:
        is_successful = not is_unknown and (expected_content.lower() in answer.lower())

    status_str = "✅ PASS" if is_successful else "❌ FAIL"
    if is_successful:
        success_count += 1
    else:
        fail_count += 1

    print(f"ANSWER : {answer[:120]}{'...' if len(answer) > 120 else ''}")
    print(f"SCORE  : {score:.4f} | EXPECTED: {expected_status} | RESULT: {status_str}")

    results_list.append({
        "query": query,
        "answer": answer,
        "score": round(score, 4),
        "expected": expected_status,
        "successful": is_successful
    })

# Print execution summary
print("\n" + "=" * 65)
print(f"  TOTAL: {len(TEST_QUERIES)} tests")
print(f"  PASS : {success_count} ({'%d' % (success_count / len(TEST_QUERIES) * 100)}%)")
print(f"  FAIL : {fail_count}")
print("=" * 65)

# Export results to JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as out_file:
    json.dump(results_list, out_file, ensure_ascii=False, indent=2)
print(f"\nResults saved: {OUTPUT_PATH}")