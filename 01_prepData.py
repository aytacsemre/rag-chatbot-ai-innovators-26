# Import required libs
import json
from pathlib import Path
import pyarrow.parquet as pq

# Define config vars
INPUT_PATH = r"C:\Users\Semre\Downloads\train-00000-of-00001.parquet"
OUTPUT_PATH = "documents.json"
MAX_ROW_COUNT = 600

# Load parquet dataset
print("Loading dataset...")
table = pq.read_table(INPUT_PATH)
df = table.to_pandas()
print(f"Total rows: {len(df)}")

# Filter unique records
df_unique = df.drop_duplicates(subset=["context"]).head(MAX_ROW_COUNT).copy()
df_unique.reset_index(drop=True, inplace=True)
print(f"Selected unique paragraphs: {len(df_unique)}")

# Process doc list
doc_list = []
for idx, row in df_unique.iterrows():
    answers = row["answers"]["text"]
    
    doc_entry = {
        "id": idx,
        "title": row["title"],
        "context": row["context"],
        "sample_q": row["question"],
        "sample_a": answers[0] if len(answers) > 0 else ""
    }
    doc_list.append(doc_entry)

# Export to JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as out_file:
    json.dump(doc_list, out_file, ensure_ascii=False, indent=2)

# Print exec summary
print(f"\nSuccessfully saved: {OUTPUT_PATH}")
print(f"\n--- FIRST 2 DOCS SAMPLE ---")
for doc in doc_list[:2]:
    print(f"\nID: {doc['id']}")
    print(f"Title: {doc['title']}")
    print(f"Context (150 chars): {doc['context'][:150]}...")
    print(f"Q: {doc['sample_q']}")
    print(f"A: {doc['sample_a']}")