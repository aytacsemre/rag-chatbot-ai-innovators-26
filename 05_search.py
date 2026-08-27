# Import required libs
import sqlite3
import json
import math
from openai import OpenAI

# Define config vars
BASE_URL = "http://127.0.0.1:51873"
MODEL_NAME = "qwen3-embedding-0.6b-generic-cpu"
DB_PATH = "knowledge_base.db"

# Init OpenAI client
client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="foundry")

# Calculate cosine similarity
def compute_cosine_similarity(vec_a, vec_b):
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

# Vectorize query text
def vectorize_query(query_text):
    response = client.embeddings.create(model=MODEL_NAME, input=query_text)
    return response.data[0].embedding

# Find matching paragraphs
def find_top_similar_paragraphs(query_text, top_k=3):
    query_vector = vectorize_query(query_text)

    db_connection = sqlite3.connect(DB_PATH)
    db_cursor = db_connection.cursor()
    db_cursor.execute("SELECT id, title, context, sample_a, embedding FROM documents")
    rows = db_cursor.fetchall()
    db_connection.close()

    score_list = []
    for doc_id, title, context, answer, embedding_json in rows:
        if embedding_json is None:
            continue
        doc_vector = json.loads(embedding_json)
        similarity_score = compute_cosine_similarity(query_vector, doc_vector)
        score_list.append({
            "id": doc_id,
            "title": title,
            "context": context,
            "sample_a": answer,
            "score": similarity_score
        })

    score_list.sort(key=lambda x: x["score"], reverse=True)
    return score_list[:top_k]

# Define test queries
test_queries = [
    "When did the Scholastic Magazine of Notre Dame begin publishing?",
    "What is the boiling point of water?",
    "Who wrote the Hamlet play?",
]

# Execute search tests
print("=" * 60)
print("SEARCH TEST RUN")
print("=" * 60)

for query in test_queries:
    print(f"\nQUERY: {query}")
    print("-" * 40)
    search_results = find_top_similar_paragraphs(query, top_k=2)
    for idx, res in enumerate(search_results, 1):
        print(f"  [{idx}] Score: {res['score']:.4f} | Title: {res['title']}")
        print(f"        Context: {res['context'][:120]}...")
        print(f"        Sample Answer: {res['sample_a']}")
    print()

print("Search functionality operational! Next step: LLM answer generation.")