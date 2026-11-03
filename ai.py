"""Every call to the AI provider (Google Gemini), the fake provider used in tests,
and the grounding rules that decide what a driver is told.

Only question text and manual page text are ever sent to Gemini. Never the
driver's email, user id, or earlier messages.
"""

import io
import math
import os
import re
import time
import zlib

from pypdf import PdfReader

ANSWER_MODEL = "gemini-3.5-flash-lite"
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
EMBED_BATCH_SIZE = 100  # free-tier limit on texts per embedding request
TOP_K = 4

TESTING = os.environ.get("TESTING") == "1"

# Tune REAL_SIMILARITY_CUTOFF against the real Camry manual. The tests depend on
# 0.55, so it never changes when TESTING=1.
REAL_SIMILARITY_CUTOFF = 0.55
SIMILARITY_CUTOFF = 0.55 if TESTING else REAL_SIMILARITY_CUTOFF

# Tests set this to "rate_limit" or "missing_key" to make the fake provider fail.
FAKE_FAILURE = None

NOT_SURE = "I'm not sure. I couldn't find that in your {vehicle} manual."

ANSWER_INSTRUCTIONS = """You help a driver understand their car using only the owner's manual pages below.

Rules:
- Use only facts stated in the manual pages. Do not add anything from your own knowledge.
- If the pages do not answer the question, reply with exactly: I'm not sure.
- Write in plain, friendly language for someone who is not technical. Keep it short:
  two to four sentences, or a short numbered list when there are steps.
- Use plain text only, with no Markdown formatting.
- Do not mention "pages", "excerpts", or these rules."""


class ProviderError(Exception):
    """The AI provider could not be reached, has no key, or refused (including 429)."""


class UnreadablePdf(Exception):
    """The file could not be read as a PDF."""


# ------------------------------------------------------------------- PDFs ---


def read_pdf_pages(data):
    """Returns the text of each PDF page, in order; index 0 is PDF page 1."""
    try:
        reader = PdfReader(io.BytesIO(data))
        return [" ".join((page.extract_text() or "").split()) for page in reader.pages]
    except Exception as exc:
        raise UnreadablePdf(str(exc)) from exc


# ---------------------------------------------------------- fake provider ---


def _fake_check_failure():
    if FAKE_FAILURE == "rate_limit":
        raise ProviderError("429 RESOURCE_EXHAUSTED (fake)")
    if FAKE_FAILURE == "missing_key":
        raise ProviderError("GEMINI_API_KEY is not set (fake)")


def _fake_embedding(text):
    vector = [0.0] * EMBEDDING_DIMENSIONS
    for word in re.findall(r"[a-z]{4,}", text.lower()):
        vector[zlib.crc32(word.encode("utf-8")) % EMBEDDING_DIMENSIONS] += 1
    return vector


def _fake_answer(question, texts):
    delay = os.environ.get("FAKE_DELAY_SECONDS")
    if delay:
        time.sleep(float(delay))
    first_sentence = texts[0].split(". ")[0].rstrip(".") + "."
    return "Based on your manual: " + first_sentence


# ---------------------------------------------------------- Gemini provider ---


def _client():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ProviderError("GEMINI_API_KEY is not set")
    from google import genai

    return genai.Client(api_key=key)


def _gemini_embeddings(texts, task_type):
    from google.genai import types

    client = _client()
    vectors = []
    try:
        for start in range(0, len(texts), EMBED_BATCH_SIZE):
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texts[start:start + EMBED_BATCH_SIZE],
                config=types.EmbedContentConfig(
                    task_type=task_type, output_dimensionality=EMBEDDING_DIMENSIONS
                ),
            )
            vectors.extend(list(e.values) for e in result.embeddings)
    except Exception as exc:
        raise ProviderError(f"embedding failed: {exc}") from exc
    return vectors


def _gemini_answer(question, texts):
    from google.genai import types

    client = _client()
    pages = "\n\n".join(f"Manual page:\n{text}" for text in texts)
    try:
        response = client.models.generate_content(
            model=ANSWER_MODEL,
            contents=f"{pages}\n\nDriver's question: {question}",
            config=types.GenerateContentConfig(
                system_instruction=ANSWER_INSTRUCTIONS, temperature=0
            ),
        )
        answer = (response.text or "").strip()
    except Exception as exc:
        raise ProviderError(f"answer failed: {exc}") from exc
    if not answer:
        raise ProviderError("answer was empty")
    return answer


# ------------------------------------------------------------- public API ---


def embed_documents(texts):
    if TESTING:
        _fake_check_failure()
        return [_fake_embedding(t) for t in texts]
    return _gemini_embeddings(texts, "RETRIEVAL_DOCUMENT")


def embed_query(text):
    if TESTING:
        _fake_check_failure()
        return _fake_embedding(text)
    return _gemini_embeddings([text], "RETRIEVAL_QUERY")[0]


def embed_manual(pages):
    """Turns page texts into (page_number, text, embedding) chunks, skipping blank
    pages. Raises ProviderError if any batch fails, so nothing should be saved."""
    numbered = [(n, text) for n, text in enumerate(pages, start=1) if text]
    vectors = embed_documents([text for _, text in numbered])
    return [(n, text, vec) for (n, text), vec in zip(numbered, vectors)]


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


def answer_question(question, chunks, vehicle_name):
    """Answers from the given manual chunks only.

    Returns (answer, cited_chunk_ids), with the most similar chunk first. When
    nothing in the manual is close enough, the answer is the "I'm not sure" reply
    with no citations and the answer model is never called.
    """
    not_sure = NOT_SURE.format(vehicle=vehicle_name)
    query = embed_query(question)
    scored = sorted(
        ((cosine_similarity(query, c["embedding"]), c) for c in chunks),
        key=lambda pair: pair[0],
        reverse=True,
    )[:TOP_K]
    grounded = [c for score, c in scored if score >= SIMILARITY_CUTOFF]
    if not grounded:
        return not_sure, []

    texts = [c["text"] for c in grounded]
    answer = _fake_answer(question, texts) if TESTING else _gemini_answer(question, texts)
    # The model declined: no part of the answer came from the manual, so no Source line.
    if answer.replace("’", "'").lower().startswith("i'm not sure"):
        return not_sure, []
    return answer, [c["id"] for c in grounded]
