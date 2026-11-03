# MyCarAI

Read by Claude Code at the start of every session. Feature behavior and exact on-screen messages are in `.claude/spec.md`. When this file and the spec disagree, the spec wins and this file should be fixed.

## What this is

A Flask app where a driver picks their vehicle and asks questions answered only from that vehicle's owner's manual (RAG over PDF pages), with the PDF page shown as the source. Admins upload one PDF manual per vehicle. It is a class capstone due November 5, 2026. The only demo vehicle is the 2024 Toyota Camry XSE.

## Who the users are, and design decisions the build must respect

These come from our design work in Professor Peck's course (Product Strategy and Execution Plan, wireframes, feedback testing). The team started as MyCarAR, an AR dashboard-scanning app, and pivoted in CP0.

- **Drivers are not technical.** They are unsure about their car's features and ask in everyday words, not the manual's feature names. Write every page and message in plain language with no AI or RAG terms. Never show "chunk", "embedding", or "similarity".
- **A wrong answer is worse than no answer.** The dealer we interviewed said one confidently wrong answer would stop him adopting the product. When retrieval is weak, say "I'm not sure" and stop. Never let the model fill gaps from its own knowledge, and never show a Source line on an answer that did not come from a retrieved chunk.
- **The source is the trust signal.** Every manual-based answer shows its Source line with the PDF page, directly under the answer, so a driver can check it in their glove-box manual. This is a crutial step in our process to ensure the user is able to trust our output and has the ability to verify the sources.
- **Drivers went straight to the chat.** In user testing, drivers skipped the other features and used the AI assistant first. `/chat` is the landing page after sign-in once a vehicle is chosen. Keep it one question box and one Send button, with nothing in front of it.
- **Carried over from MyCarAR:** plain-language answers and vehicle-specific content. **Dropped:** AR scanning, dashboard hotspots, and tutorial videos (see Out of scope in the spec).
- **Phone sign-in was the plan; email and password is what we build.** Do not add SMS, OTP, or password reset.
- The chat is the home of the app. In our wireframe the assistant is the main page and where drivers spend most of their time, so every other page is one click from it and never the other way around.

## Run it

- Setup: `python -m venv .venv`, activate it, then `pip install -r requirements.txt`.
  - Activate on Windows PowerShell: `.venv\Scripts\Activate.ps1` (if scripts are blocked, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once).
  - Activate on Windows Git Bash: `source .venv/Scripts/activate`.
  - Activate on macOS/Linux: `source .venv/bin/activate`.
  - Deactivate with `deactivate`. Create `.env` with `GEMINI_API_KEY` and `FLASK_SECRET_KEY` (each teammate uses their own key).
- Seed: `python seed.py` creates the admin `admin@mycarai.test` / `admin12345` and the Camry and RAV4.
- App: `flask --app app run`. Debug only when `FLASK_DEBUG=1` is in `.env`.
- Tests: `python -m pytest` from the repo root. `tests/conftest.py` sets `TESTING=1`, so tests use the fake AI provider and never call Gemini.
- Hand check for criteria 32/33: `TESTING=1 FAKE_DELAY_SECONDS=3`, then run the app.

## Where things go

- `app.py`: routes only. No SQL and no input rules. Holds the single `DATABASE` path setting.
- `models.py`: every SQL statement, always `?` placeholders, never f-strings.
- `validators.py`: every input rule, called by the route before anything is saved.
- `ai.py`: every Gemini call, the fake provider, `SIMILARITY_CUTOFF`, and the model names.
- `templates/`: Jinja, server-rendered. `static/chat.js` is the only JavaScript.
- `tests/`: evals are `test_eNN_<behavior>`, and eval NN checks spec criterion NN.

## Conventions

- Every query on a conversation or its messages filters by conversation id AND the signed-in user's id. Someone else's conversation returns the same 404 as a missing one. Admins get 404 there too, not "see everything".
- `/admin/*` returns 403 for non-admins. `/vehicle`, `/chat`, and `/conversations` return 403 for admins.
- Answer from the conversation's `vehicle_id`, never the driver's current vehicle.
- Every page must work with JavaScript off, using normal form posts. `chat.js` only adds conveniences and never holds a rule the server lacks.
- Only `flask`, `python-dotenv`, `pypdf`, `google-genai`, and `pytest` may be installed. No ORM, Flask-Login, LangChain, vector DB, or JS framework, and do not install `google-generativeai`.

## Vocabulary

- **Driver** and **admin** are the only roles. "User" means either one.
- A **manual** is one PDF per vehicle. A **chunk** is one PDF page of text plus its embedding.
- A **citation** links an assistant message to the chunk(s) it used.
- The **Source line** is `Source: <year make model trim> Owner's Manual, PDF page N`.
- **PDF page** is the page index starting at 1, not the number printed on the page.

## Do not touch

- `tests/fixtures/sample_manual.pdf` and the fake provider's embedding math. The expected scores (0.87 and 0) in the spec depend on both exactly.
- `SIMILARITY_CUTOFF` stays 0.55 when `TESTING=1`. Tune only the real-manual value.
- Do not edit a test to make it pass. If the build needs a different route or field name, change it once in the CONTRACT block of `tests/conftest.py` and tell the team.
- Never read, print, or commit `.env`. No keys in code, templates, or the database.
- Never send the driver's email, user id, or earlier messages to Gemini. Send only the question and chunk text.

## Fragile

- **Upload rollback:** embeddings go in batches of up to 100. If any batch fails, no `manuals` or `chunks` row may remain, so wrap the whole upload in one transaction.
- **Free tier:** a 429 is normal. Treat it like any provider error, show the unavailable message, and save nothing. Never show a traceback.
- **50 MB limit:** Flask's `MAX_CONTENT_LENGTH` raises 413 before the route runs, so the message comes from the 413 handler, not the validator.
- **Escaping:** never use `|safe` or `Markup()` on question, answer, or manual text.
