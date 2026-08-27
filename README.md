# 🧠 Offline RAG Chatbot

> *Sıfır internet, tam gizlilik ve yerel güçle çalışan akıllı soru-cevap asistanı!*

<pre style="font-family: monospace; font-size: 10px; line-height: 1;">
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00___________________________________________________________________________________________00
00___________________________________________________________________________________________00
00_________##############___##############__#####___#######__########________##############__00
00________##############___##############__###_##__###_###__##########______##############___00
00_______###______________###_____________###__##_##__###__###______###____###_______________00
00______###______________###_____________###___####__###__###______###____###________________00
00_____###############__##############__###____###__###__###########_____##############______00
00____###############__##############__###_____##__###__########________##############_______00
00_______________###__###_____________###_________###__###___###_______###___________________00
00______________###__###_____________###_________###__###_____###_____###____________________00
00__##############__##############__###_________###__###______###____##############__________00
00_##############__##############__###_________###__###________###__##############___________00
00___________________________________________________________________________________________00
00___________________________________________________________________________________________00
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00___________________________________________________________________________________________00
00___________________________________________________________________________________________00
00____________########______#######_____########______#############___#############__________00
00_________############___##########___###########___#############___#############___________00
00________###_______###__###_____###__###______###__###_____________###______________________00
00_______###____________###_____###__###______###__###_____________###_______________________00
00______###____________###_____###__###______###__##############__###############____________00
00_____###____________###_____###__###______###__##############__###############_____________00
00____###____________###_____###__###______###__###_________________________###______________00
00___###_______###__###_____###__###______###__###_________________________###_______________00
00___############___##########__############__##############___##############________________00
00____#########______#######___##########____##############___##############_________________00
00___________________________________________________________________________________________00
00___________________________________________________________________________________________00
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
</pre>

---

## 🚀 Proje Hakkında

Tamamen cihazınızda (offline) koşan, harici hiçbir bulut servisine ihtiyaç duymayan modern bir RAG (Retrieval-Augmented Generation) asistanıdır. Microsoft Foundry Local altyapısını kullanarak yerel dil modelini ayağa kaldırır, SQLite tabanlı yerel vektör veritabanından en alakalı paragrafları nokta atışı bulur ve yapay zekanın size tertemiz, kaynaklı bir cevap üretmesini sağlar.

```
rag_project/
├── 📁 01_prepData.py       # 🎯 Ham verileri işler ve hazırlar
├── 📁 02_createDB.py       # 🗄️ SQLite veritabanı altyapısını kurar
├── 📁 03_testFoundry.py    # 🔌 Foundry Local bağlantısını test eder
├── 📁 04_createEmbd.py     # 📐 Paragraflar için vektör dönüşümü yapar
├── 📁 05_search.py         # 🔍 Retrieval (arama) motorunu test eder
├── 📁 06_answer.py         # ⚡ Uçtan uca RAG pipeline test sürüşü
├── 📁 07_test.py           # 📊 Sistematik test raporu üretir
├── 💻 chatbot.py           # 🤖 Komut satırı tabanlı chatbot betiği
├── 🌐 streamlit_app.py     # ✨ Şık ve akıcı web arayüzü
├── 📚 documents.json       # 📚 Ham paragraf verisi deposu
└── 📄 README.md            # 📖 Proje dokümantasyonu

```

---

## 🛠️ Kullanılan Teknolojiler

| Katman | Teknoloji | Açıklama |
| --- | --- | --- |
| **🤖 Dil Modeli** | Foundry Local + `Phi-3.5-mini-instruct` | Tamamen çevrimdışı, hızlı ve akıllı metin üretimi |
| **📐 Embedding** | `qwen3-embedding-0.6b` | Her paragrafı matematiksel vektöre çevirir |
| **🔍 Vektör Arama** | Cosine Similarity | Soruya anlamsal olarak en yakın paragrafları yakalar |
| **🗄️ Veritabanı** | SQLite (`knowledge_base.db`) | Paragrafları, metinleri ve vektörleri güvenle saklar |
| **🌐 Arayüz** | Streamlit | Kullanıcı dostu, interaktif web tabanlı chatbot paneli |

---

## ⚙️ Kurulum Rehberi

### 1. Gereksinimleri Yükleyin

```bash
pip install openai httpx streamlit pandas

```

### 2. Veri Tabanını ve Embeddingleri Hazırlayın *(Sırasıyla çalıştırın)*

```bash
python 01_prepData.py
python 02_createDB.py
python 04_createEmbd.py

```

---

## 🎮 Çalıştırma Rehberi

Her oturumda lokal sunucunuzun ve arayüzün aktif olması gerekmektedir:

**Terminal — Chatbot arayüzünü ayağa kaldırır:**

```bash
streamlit run streamlit_app.py

```

> 🌐 Tarayıcınızı açın ve **`http://localhost:8501`** adresine gidin.

---

## ⚙️ Nasıl Çalışır? (RAG Akışı)

```
👤 Kullanıcı soru sorar
        │
        ▼
📐 Soru, embedding modeline gönderilir → Vektör üretilir
        │
        ▼
🗄️ Bu vektör, veritabanındaki paragraf vektörleriyle karşılaştırılır
        │
        ▼
🔍 En yüksek Cosine Similarity skoruna sahip paragraflar seçilir
        │
        ▼
⚖️ Eşik Kontrolü:
  ├── Skor düşükse ──> 🛑 "Bilgi tabanımda bulamadım."
  └── Skor yüksekse ─> ✅ Paragraflar + Soru, Phi-3.5 modeline gönderilir
        │
        ▼
🤖 Model kaynağa dayalı net bir cevap üretir ve kaynakları listeler!

```

---

## 🧪 Test Süreci

Sistemin performansını ve doğruluğunu test etmek için aşağıdaki komutu çalıştırabilirsiniz:

```bash
python 07_test.py

```

Bu komut, örnek sorularla sistematik bir test koşturur ve sonuçları detaylıca `test_results.json` dosyasına kaydeder.
