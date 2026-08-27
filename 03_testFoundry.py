# Import required libs
import subprocess
import httpx
import json
from openai import OpenAI

# Define config vars
FOUNDRY_EXE = r"C:\Users\Semre\AppData\Local\Microsoft\WindowsApps\foundry.exe"
BASE_URL = "http://127.0.0.1:51873"
MODEL_ALIAS = "qwen3-embedding-0.6b"

# Download model weights
print(f"[1/3] Downloading model: {MODEL_ALIAS}")
print("      (may take a few minutes on first run...)\n")
download_result = subprocess.run(
    [FOUNDRY_EXE, "model", "download", MODEL_ALIAS],
    text=True
)
if download_result.returncode != 0:
    print("Download warning, continuing...")

# Load model server
print(f"\n[2/3] Loading model to server: {MODEL_ALIAS}")
load_result = subprocess.run(
    [FOUNDRY_EXE, "model", "load", MODEL_ALIAS],
    capture_output=True, text=True
)
print(load_result.stdout or "(no output)")
if load_result.returncode != 0:
    print("Load output error:", load_result.stderr[:300])

# Verify active models
print("\n[3/3] Checking active models...")
response = httpx.get(f"{BASE_URL}/v1/models", timeout=10)
model_list = response.json().get("data", [])

if not model_list:
    print("ERROR: No models loaded. Check output above.")
    exit(1)

model_id = model_list[0]["id"]
print(f"Active model id: {model_id}")

# Run embedding test
print(f"\nRunning embedding test...")
client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="foundry")

test_sentence = "Notre Dame is a famous university."
api_response = client.embeddings.create(model=model_id, input=test_sentence)
vector_data = api_response.data[0].embedding

print(f"Sentence: '{test_sentence}'")
print(f"Vector dimension: {len(vector_data)} values")
print(f"First 5 values: {[round(x, 4) for x in vector_data[:5]]}")
print("\nFoundry Local is fully operational!")