# MyCarAI

A driver picks their vehicle and asks questions in everyday words. MyCarAI answers only from that vehicle's owner's manual and shows the manual page the answer came from, so the driver can check it in their glove-box copy. When the manual has nothing close, it says "I'm not sure" instead of guessing. Admins upload one PDF owner's manual per vehicle.

Team: Will Webster, Trey Adleta, Sang Lian, Ryan Ballard. Built with Flask, SQLite, and the Google Gemini API (free tier). The demo vehicle is the 2024 Toyota Camry XSE.

- Full feature spec and acceptance criteria: [.claude/spec.md](.claude/spec.md)
- Context file for the coding agents: [CLAUDE.md](CLAUDE.md)

## Quick start 

You need **Python 3.11 or later** and **git**. Check with `python --version`. On macOS or Linux you may need `python3` instead of `python`.

### 1. Get the code

Unzip the submission, or clone it, then open a terminal in the project folder (the one that holds `app.py`).

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Activate it:

| Terminal               | Command                         |
| ---------------------- | ------------------------------- |
| Windows PowerShell     | `.venv\Scripts\Activate.ps1`    |
| Windows Git Bash       | `source .venv/Scripts/activate` |
| Windows Command Prompt | `.venv\Scripts\activate.bat`    |
| macOS / Linux          | `source .venv/bin/activate`     |

If PowerShell says running scripts is disabled, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Your prompt now starts with `(.venv)`. Run `deactivate` when you are done.

### 3. Install the packages

```bash
pip install -r requirements.txt
```

This installs only `flask`, `python-dotenv`, `pypdf`, `google-genai`, and `pytest`. It takes 1 to 2 minutes.

### 4. Create the `.env` file

Create a file named `.env` in the project folder. It holds your keys and is never committed or submitted.

| Variable                | Required         | What it is                                                                                                                 |
| ----------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `FLASK_SECRET_KEY`      | Always           | Any long random string. It signs the sign-in cookie. The app will not start without it.                                    |
| `GEMINI_API_KEY`        | For real answers | Your own free key from [Google AI Studio](https://aistudio.google.com/apikey). Not needed in test mode (see below).        |
| `TESTING`               | Optional         | Set to `1` to use the built-in fake AI and a 3-page sample manual. No key and no network needed.                           |
| `FAKE_DELAY_SECONDS`    | Optional         | With `TESTING=1`, makes the fake AI wait this many seconds, so the "Thinking..." label stays on screen long enough to see. |
| `FLASK_DEBUG`           | Optional         | Set to `1` for Flask debug mode on your own machine only. Leave it out otherwise.                                          |
| `SESSION_COOKIE_SECURE` | Optional         | Set to `1` only if the app is served over https. Leave it out for the local demo (plain http).                             |

To make a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Option A: real answers from the real Camry manual** (needs a Gemini key):

```
FLASK_SECRET_KEY=paste-your-random-string-here
GEMINI_API_KEY=paste-your-gemini-key-here
```

**Option B: test mode, no key needed.** It uses the fake AI and the 3-page sample manual from the spec, which is how the acceptance criteria are checked by hand:

```
FLASK_SECRET_KEY=paste-your-random-string-here
TESTING=1
FAKE_DELAY_SECONDS=3
```

Each mode uses its own database file (`mycarai.db` for real, `mycarai-test.db` for test mode). If you switch modes, run `seed.py` again.

### 5. Set up the database

```bash
python seed.py
```

This creates the tables, the admin account, the 2024 Toyota Camry XSE with its manual, and the 2024 Toyota RAV4 XLE with no manual. The RAV4 has no manual on purpose: drivers should not see it in the vehicle list. It is safe to run more than once.

- **Option A:** it reads the real 76-page manual from `knowledge/manuals/2024_Toyota_Camry_XSE.pdf` and sends the page text to Gemini once. You should see `Loaded the Camry manual: 76 pages, ...`.
- **Option B:** you should see `Loaded the Camry manual: 3 pages, 3 with text.`

### 6. Start the app

```bash
flask --app app run
```

or just click the arrow when on app.py

Open http://127.0.0.1:5000 and sign in with a test account below. Press `Ctrl+C` in the terminal to stop the app.

## Test accounts

| Role   | Email                             | Password                            | How to get it                                                       |
| ------ | --------------------------------- | ----------------------------------- | ------------------------------------------------------------------- |
| Admin  | `admin@mycarai.test`              | `admin12345`                        | Created by `seed.py`                                                |
| Driver | `driver1@test.com` (or any email) | `camry2024!` (or any 8+ characters) | Sign up at http://127.0.0.1:5000/signup. There is no seeded driver. |

- **Driver:** after signing up, choose the 2024 Toyota Camry XSE on `/vehicle`. You land on `/chat`.
- **Admin:** you land on `/admin/manuals`, where you can add a vehicle and upload its PDF manual (50 MB maximum). Admins cannot use the driver pages: `/vehicle`, `/chat`, and `/conversations` return 403 for them.
- To be signed in as an admin and a driver at the same time, use a private or incognito window for one of them.

## Try it

Signed in as a driver with the Camry chosen:

| Ask                                   | What you should see                                                                                       |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| "How do I turn off lane keep assist?" | An answer, with `Source: 2024 Toyota Camry XSE Owner's Manual, PDF page N` under it. In test mode N is 2. |
| "Who won the 2020 World Series?"      | "I'm not sure. I couldn't find that in your 2024 Toyota Camry XSE manual." with no Source line.           |
| A follow-up in the same conversation  | It is added to the same conversation.                                                                     |

Then open **My conversations** to see your history newest first, reopen a conversation, or delete it.

The **PDF page** in the Source line is the page's position in the PDF file, starting at 1. It is not the number printed on the page.

## Run the tests

With the virtual environment active, from the project folder:

```bash
python -m pytest
```

All 102 tests should pass in about a minute. The tests always use the fake AI (`tests/conftest.py` sets `TESTING=1`), so they need no Gemini key, make no network calls, and never touch your real database. The same suite runs on every push in GitHub Actions ([.github/workflows/tests.yml](.github/workflows/tests.yml)).

- `tests/test_acceptance.py`: one test per acceptance criterion in the spec. `test_eNN_...` checks criterion NN.
- `tests/test_review_findings.py`: evals added after CP2 from our subagent reviews (validation edge cases, the cross-site POST check, security headers, and page behavior). Each is named for the criterion it extends.
- `tests/test_constraints.py`: checks the build rules, such as SQL only in `models.py`, no keys in the source, and only the allowed packages.

Criteria 32 and 33 are browser behavior and are also checked by hand. Use test mode (Option B) with `FAKE_DELAY_SECONDS=3`:

- Pressing Send shows "Thinking..." for 3 seconds.
- Typing 501 characters turns the counter red.
- With JavaScript turned off in the browser, asking and deleting still work.

## Project layout

| Path                                 | What it holds                                                                                                                                   |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `app.py`                             | Routes only, plus the single database path setting                                                                                              |
| `models.py`                          | Every SQL statement (always `?` placeholders)                                                                                                   |
| `validators.py`                      | Every input rule, run on the server before anything is saved                                                                                    |
| `ai.py`                              | Every Gemini call, the fake AI for tests, `SIMILARITY_CUTOFF`, and the model names                                                              |
| `seed.py`                            | Creates the database, admin account, and demo vehicles                                                                                          |
| `templates/`                         | Server-rendered pages (Jinja)                                                                                                                   |
| `static/style.css`, `static/chat.js` | Styles, and the only JavaScript (conveniences only; every page works without it)                                                                |
| `knowledge/manuals/`                 | The real 2024 Camry owner's manual                                                                                                              |
| `tests/`                             | The test suite and the 3-page sample manual                                                                                                     |
| `.claude/spec.md`                    | The spec                                                                                                                                        |
| `.claude/agents/`                    | Our custom subagents (security reviewer, validator reviewer, design specialist). All are read-only and suggest changes rather than making them. |

## Troubleshooting

| Problem                                                     | Fix                                                                                                                                                             |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RuntimeError: Set FLASK_SECRET_KEY in your .env file.`     | The `.env` file is missing, misnamed (for example `.env.txt`), or not in the project folder. See step 4.                                                        |
| `Could not process the Camry manual (...)` when seeding     | Your Gemini key is missing or wrong, or the free tier is busy (429). Check the key, wait a minute, and run `python seed.py` again. Or use test mode (Option B). |
| The vehicle page has no Camry                               | The manual did not load. Run `python seed.py` again and check its message.                                                                                      |
| "The assistant is unavailable right now. Please try again." | Gemini returned an error, often the free-tier rate limit. Wait a minute and ask again. Nothing was saved.                                                       |
| `flask: command not found` or `No module named flask`       | The virtual environment is not active. Activate it (step 2) and try again.                                                                                      |
| Port 5000 is already in use                                 | Run `flask --app app run --port 5001` and open http://127.0.0.1:5001.                                                                                           |

## Privacy note

On the free tier, Google may use prompts to improve its products, and they may be read by human reviewers. MyCarAI sends Gemini only the question text and the manual page text. It never sends a driver's email, user id, or earlier messages.
