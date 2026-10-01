from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.database import init_db
from nlp_engine.pipeline import analyze_text

from nlp_engine.analysis.keywords import extract_keywords
from nlp_engine.analysis.concepts import extract_concepts
from nlp_engine.analysis.entities import extract_entities
from nlp_engine.analysis.topics import extract_topics
from nlp_engine.analysis.vocabulary import extract_vocabulary

from api.upload import router as upload_router
from api.books import router as books_router
from api.nlp import router as nlp_router

from api.search import router as search_router

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.
    """

    print("[startup] Initializing NCERT database...")

    await init_db()

    print("[startup] Database ready.")

    yield

    print("[shutdown] NCERT NLP Engine stopped.")


app = FastAPI(
    title="NCERT NLP Engine",
    description="A domain-focused NLP engine for NCERT learning",
    version="0.1.0",
    lifespan=lifespan,
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# API ROUTERS
# ==================================================

app.include_router(upload_router)
app.include_router(books_router)
app.include_router(nlp_router)
app.include_router(search_router)



# ==================================================
# NLP REQUEST MODEL
# ==================================================

class TextRequest(BaseModel):
    text: str


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():

    return {
        "project": "NCERT NLP Engine",
        "status": "running",
    }


# ==================================================
# HEALTH
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
    }


# ==================================================
# NLP ANALYSIS
# ==================================================

@app.post("/nlp/analyze")
def analyze(request: TextRequest):

    result = analyze_text(
        request.text
    )

    result["keywords"] = extract_keywords(request.text, top_n=15)
    result["concepts"] = extract_concepts(request.text, top_n=15)
    result["entities"] = extract_entities(request.text)
    result["topics"] = extract_topics(request.text, num_topics=3, words_per_topic=8)
    result["vocabulary"] = extract_vocabulary(request.text, min_word_length=6, top_n=15)

    return result