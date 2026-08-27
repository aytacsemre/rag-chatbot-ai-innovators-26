# Import required libs
import json
import sqlite3

# Load JSON docs
print("Loading documents.json file...")
with open("documents.json", "r", encoding="utf-8") as file:
    doc_list = json.load(file)
print(f"Loaded {len(doc_list)} documents successfully.")

# Init SQLite conn
db_connection = sqlite3.connect("knowledge_base.db")
db_cursor = db_connection.cursor()

# Create table schema
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        title TEXT,
        context TEXT,
        sample_q TEXT,
        sample_a TEXT,
        embedding TEXT
    )
""")

# Insert records into DB
print("Writing records to database...")
for doc in doc_list:
    db_cursor.execute("""
        INSERT OR IGNORE INTO documents (id, title, context, sample_q, sample_a, embedding)
        VALUES (?, ?, ?, ?, ?, NULL)
    """, (
        doc["id"],
        doc["title"],
        doc["context"],
        doc["sample_q"],
        doc["sample_a"]
    ))

db_connection.commit()

# Verify total records
db_cursor.execute("SELECT COUNT(*) FROM documents")
total_count = db_cursor.fetchone()[0]
print(f"Total records in DB: {total_count}")

# Print sample records
db_cursor.execute("SELECT id, title, sample_q FROM documents LIMIT 3")
print("\n--- FIRST 3 RECORDS SAMPLE ---")
for row in db_cursor.fetchall():
    print(f"ID={row[0]} | Title={row[1]} | Q={row[2][:60]}...")

# Close connection
db_connection.close()
print("\nCompleted! knowledge_base.db generated successfully.")