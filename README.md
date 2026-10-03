# 📚 NCERT NLP Learning Platform

A full-stack AI-powered learning platform for NCERT textbooks, built as a mini project for NLP evaluation. Upload any NCERT PDF (English or Hindi), and the platform automatically extracts chapters, runs a complete NLP pipeline, and powers an interactive learning dashboard.

---

## 🧠 Project Overview

This platform combines classical NLP techniques with modern language models to create an end-to-end educational tool for Indian school students. The backend processes NCERT PDFs through a multi-stage NLP pipeline and exposes a REST API consumed by a React dashboard.

---

## ✨ Features

| Feature | Description | NLP Technique |
|---|---|---|
| 📤 **PDF Upload** | Upload full textbooks or chapter-wise PDFs | PyMuPDF + Tesseract OCR |
| 📝 **Hybrid Summarizer** | Chapter summaries in English, Hindi, Marathi | MBart-50 + Extractive NLP |
| 📚 **Difficult Words** | Vocabulary detection with definitions & translations | NLTK POS tagging + WordNet |
| ☁️ **Word Cloud** | Concept-weighted visual map of chapter themes | TF-IDF + Noun phrase extraction |
| 🔬 **Chapter NLP Analysis** | Named entities, topics, and key concepts | spaCy NER + LDA Topic Modeling |
| 🎯 **Quiz Generator** | MCQ, True/False, Fill-in-blanks, Multi-select | NLP pipeline + Gemini 2.5 Flash |
| 📺 **Recommendations** | Educational video links matched to chapter concepts | Concept extraction + YouTube API |
| 💬 **RAG Chat** | Ask questions grounded in NCERT chapter text | FAISS + RoBERTa QA model |
| 🔍 **Semantic Search** | Find relevant passages across chapters | Sentence Transformers + FAISS |

---

## 🏗️ System Architecture

```
NCERT PDF
    ↓
┌─────────────────────────────────────────┐
│           Document Processing           │
│  PyMuPDF extraction → OCR fallback      │
│  Chapter detection → Text cleaning      │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│           NLP Pipeline                  │
│  Language detection (Devanagari ratio)  │
│  Tokenization → Sentence segmentation   │
│  TF-IDF keywords → spaCy NER           │
│  LDA topic modeling → Concept extract   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│           Vector Store (FAISS)          │
│  Sentence-BERT embeddings               │
│  Cosine similarity search               │
│  Overlapping chunk retrieval            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│           FastAPI REST Backend          │
│  SQLite + SQLAlchemy async ORM          │
│  Async endpoints with uvicorn           │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│           React Frontend                │
│  Vite + React 18 dashboard              │
│  11-section learning interface          │
└─────────────────────────────────────────┘
```

---

## 🔬 NLP Techniques Used

### Text Preprocessing
- **Unicode normalization** and PDF artifact removal
- **Language detection** via Devanagari character ratio analysis
- **Sentence segmentation** using NLTK `sent_tokenize`
- **Word tokenization** with NLTK and spaCy

### Keyword & Concept Extraction
- **TF-IDF** (`scikit-learn TfidfVectorizer`) for high-importance term extraction
- **Noun phrase chunking** using spaCy dependency parsing
- **Named Entity Recognition** with spaCy `en_core_web_sm` model
- **LDA Topic Modeling** (`sklearn LatentDirichletAllocation`) for thematic clustering

### Summarization
- **Extractive summarization** for English: sentence ranking by TF-IDF keyword density
- **Abstractive summarization** for Hindi: fine-tuned MBart-50 multilingual model
- **Language-aware routing**: detects source language and selects appropriate pipeline

### Semantic Search & RAG
- **Sentence embeddings**: `all-MiniLM-L6-v2` via `sentence-transformers`
- **Vector indexing**: FAISS `IndexFlatIP` (inner product = cosine similarity on normalized vectors)
- **Overlapping chunking**: 5-sentence chunks with 1-sentence overlap for context continuity
- **Extractive QA**: `deepset/roberta-base-squad2` for answer span extraction

### Quiz Generation
- NLP pipeline extracts key concepts, entities, and important sentences
- Gemini 2.5 Flash formats these into structured exam questions
- JSON validation and sanitization ensures well-formed question objects

### Vocabulary Detection
- **POS tagging** with NLTK averaged perceptron tagger
- **Syllable complexity scoring** for difficulty ranking
- **WordNet** synset lookup for definitions, synonyms, and examples
- **Translation enrichment**: Hindi and Marathi meanings via Groq

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Framework | FastAPI 0.111 + Uvicorn |
| Database | SQLite + SQLAlchemy 2.0 (async) |
| PDF Processing | PyMuPDF, pdfplumber |
| OCR | Tesseract + pytesseract |
| Core NLP | NLTK 3.8, spaCy 3.8 |
| ML / Embeddings | scikit-learn, sentence-transformers |
| Vector Search | FAISS CPU |
| Transformers | HuggingFace Transformers, PyTorch |
| Summarization | MBart-50 (fine-tuned Hindi) |
| QA Model | deepset/roberta-base-squad2 |
| Quiz Generation | Gemini 2.5 Flash (google-genai) |
| Vocabulary AI | Groq (Hindi meanings) |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 18 + Vite |
| Routing | React Router v6 |
| Charts | Recharts |
| Animations | Framer Motion |
| API Client | Fetch API (custom client) |

---

## 📁 Project Structure

```
ncert/
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env                           # API keys
│   ├── database/
│   │   ├── database.py                # SQLAlchemy async engine
│   │   └── models.py                  # Book, Chapter ORM models
│   ├── api/
│   │   ├── books.py                   # Book CRUD endpoints
│   │   ├── upload.py                  # PDF upload endpoints
│   │   ├── nlp.py                     # All NLP feature endpoints
│   │   └── search.py                  # Semantic search endpoint
│   └── nlp_engine/
│       ├── pipeline.py                # Text analysis pipeline
│       ├── preprocessing/
│       │   ├── cleaner.py             # Text cleaning
│       │   ├── tokenizer.py           # Sentence/word tokenization
│       │   └── language.py            # Language detection
│       ├── document/
│       │   ├── processor.py           # PDF processing orchestrator
│       │   ├── pdf_extractor.py       # PyMuPDF text extraction
│       │   ├── ocr.py                 # Tesseract OCR fallback
│       │   ├── chapter_detector.py    # Chapter boundary detection
│       │   └── database_saver.py      # Persist processed chapters
│       ├── analysis/
│       │   ├── keywords.py            # TF-IDF keyword extraction
│       │   ├── concepts.py            # Noun phrase / concept mining
│       │   ├── entities.py            # spaCy NER
│       │   ├── topics.py              # LDA topic modeling
│       │   ├── vocabulary.py          # Difficult word detection
│       │   ├── summarizer.py          # Extractive summarization
│       │   ├── recommendations.py     # Video recommendations
│       │   ├── similarity.py          # TF-IDF + semantic similarity
│       │   └── wordcloud_generator.py # Word cloud generation
│       ├── generation/
│       │   ├── hindi_summarizer.py    # MBart-50 Hindi summarizer
│       │   ├── summarizer.py          # Summarizer module router
│       │   ├── quiz_generator.py      # Gemini quiz generation
│       │   ├── question_generator.py  # T5 question generation
│       │   └── answer_generator.py    # RoBERTa QA + translation
│       └── retrieval/
│           ├── embeddings.py          # Sentence-BERT embeddings
│           ├── chunking.py            # Overlapping text chunking
│           ├── vector_store.py        # FAISS vector index
│           └── chapter_retriever.py   # Build chapter FAISS store
└── frontend/
    └── src/
        ├── api/
        │   └── Client.js              # API client
        └── components/
            └── ncert/
                ├── NcertDashboard.jsx
                ├── Sidebar.jsx
                ├── UploadSection.jsx
                ├── OverviewSection.jsx
                ├── SummarySection.jsx
                ├── DifficultWordsSection.jsx
                ├── KeywordsSection.jsx
                ├── ChapterAnalysisSection.jsx
                ├── QuizSection.jsx
                ├── RecommendationsSection.jsx
                ├── ChatSection.jsx
                ├── SemanticSearchSection.jsx
                └── ChaptersSection.jsx
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10
- Node.js 18+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (install with Hindi language data)
- A free [Gemini API key](https://aistudio.google.com/apikey)
- A free [Groq API key](https://console.groq.com) (for Hindi vocabulary)

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/sakship2005/ncert.git
cd ncert/backend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
pip install pytesseract pillow google-genai

# 4. Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"

# 5. Create .env file
```

Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

```bash
# 6. Run the backend
uvicorn main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/books` | List all uploaded textbooks |
| `POST` | `/books/create` | Create a book entry |
| `POST` | `/books/upload/full` | Upload a full textbook PDF |
| `POST` | `/books/upload/chapter` | Upload a single chapter PDF |
| `GET` | `/books/{book_id}/chapters` | List chapters for a book |
| `POST` | `/nlp/summarize` | Generate chapter summary |
| `POST` | `/nlp/difficult-words` | Extract vocabulary |
| `POST` | `/nlp/chapter-analysis` | NER + topics + concepts |
| `POST` | `/nlp/generate-quiz` | Generate interactive quiz |
| `POST` | `/nlp/recommendations` | Educational resource recommendations |
| `POST` | `/nlp/ask` | RAG question answering |
| `POST` | `/search` | Semantic search across chunks |

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | Google AI Studio key for quiz generation |
| `GROQ_API_KEY` | ⚠️ Optional | Groq key for Hindi vocabulary meanings |
| `GROQ_MODEL` | ⚠️ Optional | Groq model name (default: `llama-3.3-70b-versatile`) |

