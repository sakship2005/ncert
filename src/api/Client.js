/**
 * NCERT Platform — API client
 * Talks to your FastAPI backend (default: http://localhost:8000)
 * Set VITE_API_BASE_URL in your .env to override.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      msg = body.detail || body.error || body.message || msg;
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}

// ── Books ──────────────────────────────────────────────────────────────────
export const books = {
  list: async () => {
    const data = await request("/books");
    // Normalize both list and { books: [...] } formats
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.books)) return data.books;
    return [];
  },
  get: (bookId) => request(`/books/${bookId}`),
};

// ── Chapters ───────────────────────────────────────────────────────────────
export const chapters = {
  listByBook: async (bookId) => {
    const data = await request(`/books/${bookId}/chapters`);
    return Array.isArray(data) ? data : (data?.chapters || []);
  },
  get: (chapterId) => request(`/books/chapters/${chapterId}`),
};

// ── Upload & analyse ───────────────────────────────────────────────────────
export const upload = {
  analyzeBook: async (file, meta, onProgress) => {
    onProgress?.("Uploading PDF…");
    const form = new FormData();
    form.append("file", file);
    form.append("title", meta.title);
    if (meta.chapter_number) form.append("chapter_number", meta.chapter_number);
    form.append("subject", meta.subject || "");
    form.append("class_level", meta.class_level || "");
    form.append("language", meta.language || "auto");

    const uploadRes = await fetch(`${BASE_URL}/books/upload/full`, {
      method: "POST",
      body: form,
    });
    if (!uploadRes.ok) {
      const body = await uploadRes.json().catch(() => ({}));
      throw new Error(body.detail || body.error || `Upload failed (${uploadRes.status})`);
    }
    const data = await uploadRes.json();
    if (data.status === "error") {
      throw new Error(data.error || data.message || "Textbook processing failed.");
    }
    onProgress?.(`Analysed ${data.chapters_detected || data.chapters?.length || 1} chapters. Your textbook is ready.`);
    return data;
  },
};

// ── NLP functions ──────────────────────────────────────────────────────────
export const nlp = {
  /**
   * Semantic search across chapter chunks
   */
  semanticSearch: (chapterId, query) =>
    request("/search", {
      method: "POST",
      body: JSON.stringify({ chapter_id: chapterId, query }),
    }),

  /**
   * Hybrid Hindi / Multilingual chapter summarizer (MBart-50 + Groq synthesis)
   */
  summarize: (bookId, chapterNum, language = "hi", chapterId = null) =>
    request("/nlp/summarize", {
      method: "POST",
      body: JSON.stringify({ book_id: bookId, chapter_num: chapterNum, chapter_id: chapterId, language }),
    }),

  /**
   * Feature 1: Automatic Difficult Word Detection
   */
  getDifficultWords: (bookId, chapterNum, chapterId = null) =>
    request("/nlp/difficult-words", {
      method: "POST",
      body: JSON.stringify({ book_id: bookId, chapter_num: chapterNum, chapter_id: chapterId }),
    }),

  /**
   * Feature 3: Chapter-wise Detailed NLP Analysis (actual names of entities & concepts)
   */
  getChapterAnalysis: (bookId, chapterNum, chapterId = null) =>
    request("/nlp/chapter-analysis", {
      method: "POST",
      body: JSON.stringify({ book_id: bookId, chapter_num: chapterNum, chapter_id: chapterId }),
    }),

  /**
   * Feature 5: Multi-format Question and Interactive Quiz Generator
   */
  generateQuiz: (bookId, chapterNum, chapterId = null, totalQuestions = 8, types = null, language = "en") =>
    request("/nlp/generate-quiz", {
      method: "POST",
      body: JSON.stringify({
        book_id: bookId,
        chapter_num: chapterNum,
        chapter_id: chapterId,
        total_questions: totalQuestions,
        types: types || ["mcq", "true_false", "fill_blank", "short_answer"],
        language,
      }),
    }),

  /**
   * Feature 6: Educational Video & Reference Recommendations
   */
  getRecommendations: (bookId, chapterNum, chapterId = null) =>
    request("/nlp/recommendations", {
      method: "POST",
      body: JSON.stringify({ book_id: bookId, chapter_num: chapterNum, chapter_id: chapterId }),
    }),

  /**
   * Feature 4: Context-grounded Multilingual RAG QA
   */
  contextQA: (chapterId, question, language = "en", bookId = null, chapterNum = null) =>
    request("/nlp/ask", {
      method: "POST",
      body: JSON.stringify({
        chapter_id: chapterId,
        book_id: bookId,
        chapter_num: chapterNum,
        question,
        language,
      }),
    }),

  /**
   * Original Practice Question Generator
   */
  generateQuestions: (chapterId, numQuestions = 10) =>
    request("/nlp/generate-questions", {
      method: "POST",
      body: JSON.stringify({ chapter_id: chapterId, number_of_questions: numQuestions }),
    }),
};

// ── Chat (Multilingual RAG backed) ─────────────────────────────────────────
export const chat = {
  send: (chapterId, message, history = [], language = "en", bookId = null, chapterNum = null) =>
    request("/nlp/ask", {
      method: "POST",
      body: JSON.stringify({
        chapter_id: chapterId,
        book_id: bookId,
        chapter_num: chapterNum,
        question: message,
        language,
      }),
    }),
};