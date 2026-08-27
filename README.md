# 🧠 Offline RAG Chatbot

> *Sıfır internet, tam gizlilik ve yerel güçle çalışan akıllı soru-cevap asistanı!*

---

## 🚀 Proje Hakkında

Tamamen cihazınızda (offline) koşan, harici hiçbir bulut servisine ihtiyaç duymayan modern bir RAG (Retrieval-Augmented Generation) asistanıdır. Microsoft Foundry Local altyapısını kullanarak yerel dil modelini ayağa kaldırır, SQLite tabanlı yerel vektör veritabanından en alakalı paragrafları nokta atışı bulur ve yapay zekanın size tertemiz, kaynaklı bir cevap üretmesini sağlar.

```
rag_project/
├── 📁 01_veri_hazirla.py       # 🎯 SQuAD veri setinden 600 harika paragraf seçer
├── 📁 02_veritabani_olustur.py # 🗄️ SQLite veritabanı altyapısını kurar
├── 📁 03_foundry_test.py       # 🔌 Foundry Local bağlantısını test eder
├── 📁 04_embedding_uret.py     # 📐 600 paragraf için vektör dönüşümü yapar
├── 📁 05_arama.py              # 🔍 Retrieval (arama) motorunu test eder
├── 📁 06_cevap_uret.py         # ⚡ Uçtan uca RAG pipeline test sürüşü
├── 📁 07_test.py               # 📊 Sistematik test raporu üretir
├── 💻 streamlit_app.py         # ✨ Şık ve akıcı web arayüzü
├── 🗃️ bilgi_tabani.db          # 💾 SQLite veritabanı (600 paragraf + vektörler)
├── 📄 belgeler.json            # 📚 Ham paragraf verisi deposu
└── 📜 sohbet_gecmisi.json      # 💬 Otomatik saklanan sohbet geçmişi

```

---

## 🛠️ Kullanılan Teknolojiler

| Katman | Teknoloji | Açıklama |
| --- | --- | --- |
| **🤖 Dil Modeli** | Foundry Local + `phi-3.5-mini` | Tamamen çevrimdışı, hızlı ve akıllı metin üretimi |
| **📐 Embedding** | `qwen3-embedding-0.6b` | Her paragrafı 1024 boyutlu matematiksel vektöre çevirir |
| **🔍 Vektör Arama** | Cosine Similarity | Soruya anlamsal olarak en yakın paragrafları yakalar |
| **🗄️ Veritabanı** | SQLite | Paragrafları, metinleri ve vektörleri güvenle saklar |
| **🌐 Arayüz** | Streamlit | Kullanıcı dostu, interaktif web tabanlı chatbot paneli |
| **📊 Veri Seti** | SQuAD | 600 zengin İngilizce Wikipedia paragrafı |

---

## ⚙️ Kurulum Rehberi

### 1. Gereksinimleri Yükleyin

```bash
pip install pyarrow pandas openai streamlit foundry-local-sdk httpx

```

### 2. Foundry Local'i Kurun

```bash
winget install Microsoft.FoundryLocal

```

### 3. Modelleri İndirin

```bash
foundry model download qwen3-embedding-0.6b
foundry model download phi-3.5-mini

```

### 4. Veri Tabanını Hazırlayın *(İlk kurulumda bir kez çalıştırılır)*

```bash
python 01_veri_hazirla.py
python 02_veritabani_olustur.py
python 04_embedding_uret.py    

```

---

## 🎮 Çalıştırma Rehberi

Her oturumda iki ayrı terminal penceresi açmanız gerekmektedir:

**Terminal 1 — Foundry sunucusunu başlatır:**

```bash
foundry server start

```

**Terminal 2 — Chatbot arayüzünü ayağa kaldırır:**

```bash
python -m streamlit run streamlit_app.py

```

> 🌐 Tarayıcınızı açın ve **`http://localhost:8501`** adresine gidin.

*💡 Not: Bu projede `python` komutu varsayılan olarak şu yola karşılık gelmektedir: `C:\Users\Azra\.pyenv\pyenv-win\versions\3.10.11\python.exe*`

---

## ⚙️ Nasıl Çalışır? (RAG Akışı)

```
👤 Kullanıcı soru sorar
       │
       ▼
📐 Soru, embedding modeline gönderilir → 1024 boyutlu vektör üretilir
       │
       ▼
🗄️ Bu vektör, veritabanındaki 600 paragrafın vektörleriyle karşılaştırılır
       │
       ▼
🔍 En yüksek Cosine Similarity skoruna sahip paragraflar seçilir
       │
       ▼
⚖️ Eşik Kontrolü:
 ├── Skor düşükse ──> 🛑 "Bilgi tabanımda bulamadım."
 └── Skor yüksekse ─> ✅ Paragraflar + Soru, phi-3.5-mini modeline gönderilir
       │
       ▼
🤖 Model kaynağa dayalı net bir cevap üretir ve kaynakları listeler!

```

---

## ✨ Arayüz Özellikleri

* 🌊 **Streaming Cevaplar:** Token token akan modern ve akıcı yanıt deneyimi.
* 📑 **Kaynak Paneli:** Cevabın hangi paragraftan üretildiğini ve benzerlik skorunu şeffafça gösterir.
* 📂 **Canlı Belge Yükleme:** Çalışma anında sisteme yeni `.txt` veya `.md` dosyaları ekleyebilme imkanı.
* 🎚️ **Alaka Eşiği Ayarı:** Yanıt hassasiyetini ayarlamak için arayüz içi kaydırıcı (Varsayılan: `0.45`).
* 💾 **Kalıcı Sohbet Geçmişi:** Sayfa yenilense bile kaybolmayan sohbet hafızası.
* 🧠 **LLM Belleği:** Önceki 3 tur konuşmayı hatırlayarak bağlam kopmalarını önleyen akıllı diyalog yönetimi.

---

## 🧪 Test Süreci

Sistemin performansını ve doğrulugunu test etmek için aşağıdaki komutu çalıştırabilirsiniz:

```bash
python 07_test.py

```

Bu komut, 10 farklı örnek soruyla sistematik bir test koşturur ve sonuçları detaylıca `test_sonuclari.json` dosyasına kaydeder.