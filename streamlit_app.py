# Import required libs
import os
import streamlit as st
import sqlite3
import json
import math
from openai import OpenAI

# Define config vars
BASE_URL = "http://127.0.0.1:51873"
EMBED_MODEL = "qwen3-embedding-0.6b-generic-cpu"
CHAT_MODEL_ID = "Phi-3.5-mini-instruct-generic-cpu"
DEFAULT_THRESHOLD = 0.45
HISTORY_FILE = "chat_history.json"
MEMORY_LENGTH = 6

# Init OpenAI client
client = OpenAI(base_url=f"{BASE_URL}/v1", api_key="foundry")

# Load chat history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

# Save chat history
def save_history(messages):
    record_list = []
    for msg in messages:
        record_list.append({
            "role": msg["role"],
            "content": msg["content"],
            "sources": [
                {"title": src["title"], "score": src["score"], "context": src.get("context", "")}
                for src in msg.get("sources", [])
            ]
        })
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(record_list, file, ensure_ascii=False, indent=2)

# Compute cosine similarity
def compute_cosine_similarity(vec_a, vec_b):
    dot_product = sum(x * y for x, y in zip(vec_a, vec_b))
    return dot_product / (math.sqrt(sum(x * x for x in vec_a)) * math.sqrt(sum(y * y for y in vec_b)))

# Search similar paragraphs
def search_paragraphs(query_text, top_k=3):
    api_response = client.embeddings.create(model=EMBED_MODEL, input=query_text)
    query_vector = api_response.data[0].embedding

    db_connection = sqlite3.connect("knowledge_base.db")
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
    return score_list[:top_k]

# Upload new document
def upload_document(file_name, file_text):
    chunk_list = [p.strip() for p in file_text.split("\n\n") if len(p.strip()) > 50]
    if not chunk_list:
        return 0

    db_connection = sqlite3.connect("knowledge_base.db")
    db_cursor = db_connection.cursor()
    db_cursor.execute("SELECT MAX(id) FROM documents")
    max_id = db_cursor.fetchone()[0] or 0
    title_str = file_name.replace(".txt", "").replace(".md", "")

    for idx, chunk in enumerate(chunk_list):
        api_response = client.embeddings.create(model=EMBED_MODEL, input=chunk[:2000])
        vector_json = json.dumps(api_response.data[0].embedding)
        db_cursor.execute(
            "INSERT INTO documents (id, title, context, sample_q, sample_a, embedding) VALUES (?, ?, ?, ?, ?, ?)",
            (max_id + idx + 1, title_str, chunk, "", "", vector_json)
        )

    db_connection.commit()
    db_connection.close()
    return len(chunk_list)

# Fetch database metrics
def get_database_info():
    db_connection = sqlite3.connect("knowledge_base.db")
    db_cursor = db_connection.cursor()
    db_cursor.execute("SELECT COUNT(*) FROM documents")
    total_count = db_cursor.fetchone()[0]
    db_cursor.execute("SELECT DISTINCT title FROM documents")
    title_list = [row[0] for row in db_cursor.fetchall()]
    db_connection.close()
    return total_count, title_list

# Stream LLM tokens
def stream_tokens(query_text, search_results, history):
    combined_context = "\n\n".join(f"[{res['title']}]\n{res['context']}" for res in search_results)

    messages = [{"role": "system", "content":
        "You are an elite, intelligent AI assistant. Answer strictly using the provided context. "
        "If the answer is not in the context, state that you do not possess that information. Keep answers sharp, elegant, and concise."}]

    for msg in history[-MEMORY_LENGTH:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": f"Context:\n{combined_context}\n\nQuestion: {query_text}"})

    stream_response = client.chat.completions.create(
        model=CHAT_MODEL_ID,
        messages=messages,
        max_tokens=400,
        temperature=0.1,
        stream=True
    )
    for chunk in stream_response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Configure Streamlit page layout & styling (Blue & Black Cyber Theme)
st.set_page_config(page_title="✨🌌 CyberVault RAG Engine", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    /* Global Theme & Deep Black-Blue Palette */
    .stApp {
        background: linear-gradient(135deg, #020617 0%, #090d16 50%, #030712 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom Header Banner */
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4);
        margin-bottom: 2rem;
        border: 1px solid rgba(96, 165, 250, 0.3);
    }
    .main-header h1 {
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.025em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        font-size: 1.05rem;
        margin-top: 0.5rem;
        opacity: 0.9;
        font-weight: 400;
    }

    /* Sidebar Customizations */
    [data-testid="stSidebar"] {
        background-color: #050b14;
        border-right: 1px solid rgba(59, 130, 246, 0.15);
    }
    
    /* Button Aesthetics */
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        color: white;
        border-radius: 10px;
        border: 1px solid rgba(96, 165, 250, 0.4);
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        border-color: #60a5fa;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Render Lavish Header
st.markdown("""
<div class="main-header">
    <h1>⚡🌌 CYBERVAULT INTELLIGENCE RAG 🌌⚡</h1>
    <p>🔮 State-of-the-Art Offline Neural Search & Autonomous Knowledge Engine 🔮</p>
</div>
""", unsafe_allow_html=True)

# Setup sidebar components
with st.sidebar:
    st.markdown("### 📂 **Neural Ingestion Hub**")
    st.caption("🚀 Inject custom `.txt` or `.md` files directly into the neural database.")
    uploaded_file = st.file_uploader("Select data file", type=["txt", "md"], label_visibility="collapsed")
    if uploaded_file:
        if st.button("💎 Sync to Core DB", use_container_width=True):
            file_text = uploaded_file.read().decode("utf-8", errors="ignore")
            with st.spinner("🔮 Synthesizing Neural Embeddings..."):
                added_count = upload_document(uploaded_file.name, file_text)
            st.success(f"✨ Successfully indexed {added_count} records from **{uploaded_file.name}**!")

    st.markdown("---")
    st.markdown("### 🎛️ **Engine Calibration**")
    THRESHOLD = st.slider(
        "🎯 Precision Match Threshold", min_value=0.25, max_value=0.70,
        value=DEFAULT_THRESHOLD, step=0.01,
        help="🔮 Lower value = wider context search. Higher value = absolute hyper-precision."
    )

    st.markdown("---")
    st.markdown("### 🧹 **Memory Core**")
    if st.button("🗑️ Purge Chat History", use_container_width=True):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 **Knowledge Matrix Metrics**")
    total_paras, titles = get_database_info()
    st.metric("💎 Active Context Nodes", total_paras)
    with st.expander("📚 **Indexed Source Manifest**"):
        for title_item in titles:
            st.caption(f"🔹 {title_item.replace('_', ' ')}")

# Init session state variables
if "messages" not in st.session_state:
    st.session_state.messages = load_history()
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# Render lavish quick query buttons
st.markdown("### 🚀 **Quick Neural Probes:**")
quick_queries = [
    "🏆 What sport does Notre Dame play?",
    "📅 When did Scholastic Magazine begin?",
    "🎹 Where was Frédéric Chopin born?",
    "🎬 Who directed the film Spectre?",
    "🎓 How many students attend Notre Dame?",
    "🌍 What is the capital of France?",
]
columns = st.columns(3)
for idx, q_text in enumerate(quick_queries):
    clean_query = q_text.split(" ", 1)[1] if " " in q_text else q_text
    if columns[idx % 3].button(q_text, use_container_width=True):
        st.session_state.pending_query = clean_query

st.markdown("---")

# Display chat message history with lavish badges
for message in st.session_state.messages:
    role_icon = "👤 **Operator**" if message["role"] == "user" else "🤖 **CyberOracle**"
    with st.chat_message(message["role"]):
        st.markdown(f"{role_icon}")
        st.write(message["content"])
        relevant_sources = [s for s in message.get("sources", []) if s["score"] >= THRESHOLD]
        if message["role"] == "assistant" and relevant_sources:
            with st.expander(f"🔮 **Retrieved Neural References — {len(relevant_sources)} Nodes Active**"):
                for src in relevant_sources:
                    st.markdown(f"🌟 **{src['title'].replace('_', ' ')}**  `⚡ match score: {src['score']:.4f}`")
                    st.caption(src.get("context", "")[:250] + "...")

# Handle new user input
user_input = st.chat_input("💬 Transmit your query to the neural engine...")
query = user_input or st.session_state.pending_query
if st.session_state.pending_query:
    st.session_state.pending_query = None

if query:
    st.session_state.messages.append({"role": "user", "content": query, "sources": []})
    with st.chat_message("user"):
        st.markdown("👤 **Operator**")
        st.write(query)

    with st.chat_message("assistant"):
        st.markdown("🤖 **CyberOracle**")
        search_results = search_paragraphs(query)
        best_score = search_results[0]["score"] if search_results else 0

        if best_score < THRESHOLD:
            answer = "⚠️ [Neural Alert]: Insufficient correlation found within knowledge boundaries to construct a verified response."
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": []})
        else:
            relevant_sources = [s for s in search_results if s["score"] >= THRESHOLD]
            previous_messages = st.session_state.messages[:-1]
            answer = st.write_stream(stream_tokens(query, relevant_sources, previous_messages))
            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": relevant_sources})
            with st.expander(f"🔮 **Retrieved Neural References — {len(relevant_sources)} Nodes Active**"):
                for src in relevant_sources:
                    st.markdown(f"🌟 **{src['title'].replace('_', ' ')}**  `⚡ match score: {src['score']:.4f}`")
                    st.caption(src["context"][:250] + "...")

    save_history(st.session_state.messages)