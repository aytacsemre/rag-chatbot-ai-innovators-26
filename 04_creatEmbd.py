# Import required libs
import json
import sqlite3
import httpx
from openai import OpenAI

# Define config vars
BASE_URL = "http://127.0.0.1:51873"
DB_PATH = "knowledge_base.db"

# Init OpenAI client
client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="foundry")

# Connect to database
print("Connecting to database...")
db_connection = sqlite3.connect(DB_PATH)
db_cursor = db_connection.cursor()

# Fetch active model
print("Fetching active model...")
response = httpx.get(f"{BASE_URL}/v1/models", timeout=10)
model_list = response.json().get("data", [])
if not model_list:
    print("ERROR: No active models found.")
    exit(1)
model_id = model_list[0]["id"]
print(f"Using model: {model_id}")

# Load missing embeddings
db_cursor.execute("SELECT id, context FROM documents WHERE embedding IS NULL")
records = db_cursor.fetchall()
print(f"Found {len(records)} records without embeddings.")

# Process record embeddings
for idx, (doc_id, context_text) in enumerate(records, 1):
    try:
        api_response = client.embeddings.create(model=model_id, input=context_text)
        vector_data = api_response.data[0].embedding
        vector_json = json.dumps(vector_data)
        
        db_cursor.execute(
            "UPDATE documents SET embedding = ? WHERE id = ?",
            (vector_json, doc_id)
        )
        db_connection.commit()
        print(f"[{idx}/{len(records)}] Processed document ID: {doc_id}")
    except Exception as e:
        print(f"Error processing ID {doc_id}: {e}")

# Close database conn
db_connection.close()
print("\nAll embeddings generated and saved successfully!")