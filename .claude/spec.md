# Spec: MyCarAI

Team members: Will Webster, Trey Adleta, Sang Lian, Ryan Ballard

## Intent

MyCarAI is for drivers who are unsure about their car's technology. A driver picks their vehicle and asks plain-language questions, and gets an answer drawn only from that vehicle's owner's manual, with the manual page shown as the source, while an admin loads each vehicle's manual. Answers stay inside the manual so a driver can trust them, and the app says "I'm not sure" when the manual has nothing close.

## Users and permissions

| User type               | May                                                                                                                                                                             | May not                                                                                                                                                                                                                                                    |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Visitor (not signed in) | Open `/signup` and `/login`. Create a driver account.                                                                                                                           | Open `/vehicle`, `/chat`, `/conversations`, or any `/admin` page (each redirects to `/login`). Create an admin account.                                                                                                                                    |
| Driver                  | Choose their own vehicle on `/vehicle`. Ask questions on `/chat` and follow-up questions on their own `/conversations/<id>`. View and delete their own conversations. Sign out. | View, continue, or delete another driver's conversation. Open any `/admin` page or upload a manual. Give themselves the admin role. Ask questions before choosing a vehicle.                                                                               |
| Admin                   | Add a vehicle and upload one PDF manual per vehicle on `/admin/manuals`. See every manual's vehicle, page count, uploader, upload date, and status. Sign out.                   | Open `/vehicle`, `/chat`, or `/conversations` (403). Read, continue, or delete any driver's conversation (404). Sign up through `/signup` (admin accounts are created only by the seed script). Upload a second manual for a vehicle that already has one. |

## In scope

1. **Accounts:** sign up on `/signup`, sign in on `/login`, and sign out with the Sign out button in the header of every signed-in page (a POST to `/logout`).
2. **Vehicle profile:** a driver picks make, model, year, and trim from the vehicles that have a manual, on `/vehicle`.
3. **Manual library (admin):** an admin adds a vehicle and uploads its PDF owner's manual on `/admin/manuals`, which lists each manual with its vehicle, page count, uploader, upload date, and a "Ready" status once questions can be answered from it.
4. **Ask MyCarAI:** a driver asks a question on `/chat` (which starts a new conversation) or a follow-up on `/conversations/<id>`, and gets an answer drawn only from that conversation's vehicle manual, with a source line naming the manual and PDF page, or "I'm not sure" when the manual has nothing close.
5. **Conversation history:** a driver sees their past conversations newest first on `/conversations`, reopens one at `/conversations/<id>`, and deletes one with its Delete button.

## Out of scope

- AR dashboard scanning, hotspot labels, and the static dashboard diagram.
- Tutorial video library, lesson progress tracking, and video links in answers.
- Shipping with manuals for any vehicle other than the 2024 Toyota Camry XSE. Tests and admins may load others, but the team will load and demo only this one.
- Phone-number sign-in, one-time text codes, password reset, and any email or text message sending. Our strategy plan chose phone sign-in for the full product; we use email and password because a texting service cannot be set up, made consent-compliant, and tested by November 5.
- Sales mode, VIN lookup, QR-code install, and the "Call me" button.
- Manager or dealer dashboards, analytics, and usage reports.
- Answer ratings, flags, and an expert review queue.
- Editing or deleting a manual or vehicle after it is added, and manuals in any format other than PDF.
- Answers that use earlier messages in the conversation. Each question is answered on its own from the manual.
- Streaming answers word by word, voice input, and multi-language support.
- A separate vector database, LangChain, LlamaIndex, or any other RAG framework.
- A mobile app, a JavaScript front-end framework (React, Vue, Svelte, htmx, or similar), or a JSON API for the pages. All pages are server-rendered; the only JavaScript is `static/chat.js` (see Constraints).

## Data

All tables use SQLite. **(R)** marks a required (NOT NULL) column.

**users**

- `id` (R, integer primary key)
- `email` (R, unique, stored lowercase)
- `password_hash` (R)
- `role` (R, either `driver` or `admin`, default `driver`)
- `vehicle_id` (optional until the driver chooses a vehicle; foreign key to `vehicles.id`)

**vehicles**

- `id` (R, integer primary key)
- `make` (R), `model` (R), `year` (R, 4-digit integer), `trim` (R)
- The combination of make, model, year, and trim is unique.

**manuals**

- `id` (R, integer primary key)
- `vehicle_id` (R, unique, foreign key to `vehicles.id`; one manual per vehicle)
- `page_count` (R)
- `uploaded_by` (R, foreign key to `users.id`; shown as the uploader's email)
- `uploaded_at` (R, shown as the upload date)
- The manual's displayed title is built from its vehicle, for example "2024 Toyota Camry XSE Owner's Manual", and is not stored.
- The "Ready" status is not stored. Every manual row shows "Ready", because an upload that fails is rolled back and leaves no row (criterion 15).

**chunks**

- `id` (R, integer primary key)
- `manual_id` (R, foreign key to `manuals.id`)
- `page_number` (R, the PDF page index starting at 1)
- `text` (R)
- `embedding` (R, JSON list of 768 floats)

**conversations**

- `id` (R, integer primary key)
- `user_id` (R, foreign key to `users.id`)
- `vehicle_id` (R, foreign key to `vehicles.id`; the driver's vehicle when the conversation started, used for every answer in it)
- `title` (R, the first 60 characters of the first question)
- `created_at` (R, shown on `/conversations` and used to list newest first)

**messages**

- `id` (R, integer primary key; message order within a conversation is by `id`)
- `conversation_id` (R, foreign key to `conversations.id`)
- `sender` (R, either `driver` or `assistant`)
- `content` (R)

**citations**

- `message_id` (R, foreign key to `messages.id`; always an assistant message)
- `chunk_id` (R, foreign key to `chunks.id`)
- Primary key is (`message_id`, `chunk_id`).

How they connect: a vehicle has at most one manual; a manual has many chunks. A user has at most one selected vehicle and many conversations. A conversation belongs to one vehicle and has many messages. An assistant message has zero or more citations, and each citation points to one chunk, which gives the PDF page shown in the source line. Deleting a conversation deletes its messages and their citations.

## Acceptance criteria

**Setup for checking.** `seed.py` creates the admin `admin@mycarai.test` with password `admin12345`, the vehicle 2024 Toyota Camry XSE with a manual, and the vehicle 2024 Toyota RAV4 XLE with no manual. When `TESTING=1`, the Camry manual is `tests/fixtures/sample_manual.pdf`, a 3-page PDF with one chunk per page and exactly this text. Page 1: "Welcome to your vehicle. Read this guide before driving. Store this booklet inside the glove compartment." Page 2: "Lane keep assist keeps the car in its lane. To turn off lane keep assist, press the lane assist button." Page 3: "Check tire pressure monthly. Inflate tires to the pressure shown on the label inside the door jamb." `ai.py` uses its fake provider (see Constraints) instead of Gemini, and `SIMILARITY_CUTOFF` is fixed at 0.55 whatever value the team tunes for the real manual. Criteria 1 to 31 are automated with Flask's test client. Criteria 16 and 17 are also checked once by hand with the real 2024 Camry manual and the real Gemini API before CP3. Flask's test client runs no JavaScript, so criteria 32 and 33 are checked by hand in a browser: run `seed.py` and the app with `TESTING=1` and `FAKE_DELAY_SECONDS=3`, sign in as a driver, and choose the Camry.

**Accounts**

1. Signing up with `driver1@test.com` and password `camry2024!` lands on `/vehicle`, the page header shows "Signed in as driver1@test.com", and the `users` table has one new row with role `driver` whose `password_hash` is not the text `camry2024!`.
2. Signing up with an empty email is not saved and the form shows "Email is required." Signing up with `not-an-email` is not saved and the form shows "Enter a valid email address."
3. Signing up with the 7-character password `abc1234` is not saved and the form shows "Password must be at least 8 characters."
4. After criterion 1, signing up with `DRIVER1@test.com` is not saved, the form shows "An account with this email already exists.", and the `users` row count is unchanged.
5. Signing in as `driver1@test.com` with `camry2024!` lands on `/vehicle` if no vehicle is chosen, or on `/chat` if one is, and the header shows "Signed in as driver1@test.com". After pressing Sign out, the page shows "You are signed out." on `/login`, and requesting `/chat` redirects to `/login`.
6. Signing in with `driver1@test.com` and a wrong password, or with an email that has no account, stays on `/login` and shows the same message in both cases: "Email or password is incorrect."

**Vehicle profile**

7. The vehicle list on `/vehicle` shows "2024 Toyota Camry XSE" and does not show "2024 Toyota RAV4 XLE". Choosing the Camry and pressing Save redirects to `/chat`, whose header reads "Ask about your 2024 Toyota Camry XSE".
8. A POST to `/vehicle` with `vehicle_id=9999` (no such vehicle), `vehicle_id=abc`, or the RAV4's id (a real vehicle with no manual) shows "Choose a vehicle from the list." and the driver's `vehicle_id` is unchanged.
9. A signed-in driver who has not chosen a vehicle and opens `/chat` is redirected to `/vehicle`, which shows "Choose your vehicle first."

**Manual library**

10. An admin who adds the vehicle 2025 Toyota Camry SE and uploads `sample_manual.pdf` for it sees a new row on `/admin/manuals` showing "2025 Toyota Camry SE Owner's Manual", 3 pages, uploaded by `admin@mycarai.test`, today's date in the form `2026-10-22`, and status "Ready", and the `chunks` table has rows for that manual with page numbers 1, 2, and 3.
11. Adding a vehicle with an empty make, or with the year `20x5`, is not saved and shows "Enter make, model, a 4-digit year, and trim." Adding 2024 Toyota Camry XSE again is not saved and shows "This vehicle already exists." In both cases the `vehicles` row count is unchanged.
12. Uploading `manual.docx`, or a text file renamed to `manual.pdf`, shows "Upload a PDF file." and no row is added to `manuals` or `chunks`.
13. Pressing Upload with no file chosen shows "Choose a PDF to upload." Uploading a PDF larger than 50 MB shows "PDFs must be 50 MB or smaller." In both cases no row is added to `manuals`.
14. Uploading a second PDF for the 2024 Toyota Camry XSE shows "This vehicle already has a manual." and the `manuals` and `chunks` row counts are unchanged.
15. When embedding fails during an upload (the fake provider raises a rate-limit error), the page shows "The manual could not be processed. Try again." and no row is added to `manuals` or `chunks`.

**Ask MyCarAI**

16. A driver with the Camry selected who asks "How do I turn off lane keep assist?" sees the question, the answer "Based on your manual: Lane keep assist keeps the car in its lane.", and the line "Source: 2024 Toyota Camry XSE Owner's Manual, PDF page 2". In the by-hand check with the real manual, the source line names a PDF page N, and page N of that PDF contains the word "lane".
17. Asking "Who won the 2020 World Series?" shows an answer that begins "I'm not sure" with no Source line, and both the question and the answer are saved as messages.
18. Submitting a question that is empty or only spaces shows "Type a question first." and no row is added to `messages` or `conversations`.
19. A question of 501 characters, sent as a direct POST to `/chat`, shows "Questions must be 500 characters or fewer." and no row is added to `messages`. A question of exactly 500 characters (the letter "a" repeated 500 times) is saved as a driver message, and the page shows a reply beginning "I'm not sure".
20. When `GEMINI_API_KEY` is missing, or Gemini returns an error or a rate-limit (429) response, asking a question shows "The assistant is unavailable right now. Please try again.", the response does not contain the word "Traceback", and no row is added to `messages` or `conversations`.
21. Asking `<script>alert(1)</script>` returns a page whose HTML contains `&lt;script&gt;alert(1)&lt;/script&gt;` and does not contain `<script>alert(1)</script>`.
22. The follow-up "Where is the lane assist button?" posted on `/conversations/<id>` adds two rows to that conversation's messages (the question and the answer) and no new row to `conversations`. If the driver has switched to the 2025 Camry SE (added as in criterion 10) since the conversation started, the follow-up's Source line still names the 2024 Toyota Camry XSE manual.

**Conversation history**

23. After a driver asks the 75-character first question "How do I turn off lane keep assist on my Camry when I drive on the highway?" and then the follow-up "Where is the lane assist button?", `/conversations` lists that conversation first, with a title equal to the first 60 characters of the first question, "2024 Toyota Camry XSE", and today's date in the form `2026-10-22`. Opening it shows both questions and both answers in the order they were asked, each answer with its Source line.
24. Opening `/conversations/9999` (no such conversation) shows a 404 page reading "Conversation not found."
25. Pressing Delete on a conversation removes it from `/conversations` and removes its rows from `conversations`, `messages`, and `citations`. A GET request to `/conversations/<id>/delete` returns 405 and removes nothing.

**Users and permissions**

26. A visitor who is not signed in and requests `/chat`, `/conversations`, `/vehicle`, or `/admin/manuals` is redirected to `/login`.
27. Driver A who requests `/conversations/<id>` for a conversation belonging to driver B gets the same 404 page as criterion 24, and the text of driver B's question does not appear anywhere in the response.
28. Driver A who sends a POST to `/conversations/<id>/delete`, or posts a follow-up to `/conversations/<id>`, for driver B's conversation gets a 404 page, and driver B's `conversations` and `messages` row counts are unchanged.
29. A driver who requests `/admin/manuals`, or sends a POST to add a vehicle or upload a manual there, receives a 403 page and no row is added to `vehicles`, `manuals`, or `chunks`.
30. An admin who requests `/conversations/<id>` for a driver's conversation, or sends a POST to `/conversations/<id>/delete` for it, gets a 404 page and the driver's rows are unchanged. An admin who requests `/chat`, `/vehicle`, or `/conversations` receives a 403 page.
31. A POST to `/signup` that includes the extra field `role=admin` creates an account whose role is `driver`.

**Chat page JavaScript (checked by hand in a browser)**

32. On `/chat`, typing "How do I turn off lane keep assist?" and pressing Send disables the Send button and shows "Thinking..." for the 3 seconds the fake provider waits, until the answer page loads. Pressing Send or Enter again during those 3 seconds changes nothing, and afterward `messages` holds one copy of the question. Separately, typing 500 characters shows "500 / 500" in the normal text color, and typing one more shows "501 / 500" in red.
33. With JavaScript turned off in the browser, asking "How do I turn off lane keep assist?" still shows the answer and its "Source: 2024 Toyota Camry XSE Owner's Manual, PDF page 2" line, and the conversation's Delete button still deletes it with no confirmation box.

## Constraints

- **Language and framework:** Python 3.11 or later with Flask. Pages are server-rendered Jinja templates. No JavaScript framework.
- **JavaScript:** one plain JavaScript file, `static/chat.js`, loaded only on `/chat` and `/conversations/<id>`, with no build step and no script loaded from another site. It may only: disable the Send button and show "Thinking..." after a question is sent; show a live "N / 500" character count that turns red above 500; scroll to the newest answer when the page loads; send on Enter and add a new line on Shift+Enter; and ask "Delete this conversation?" before the delete form submits. Every page must still work with JavaScript turned off, using normal form posts.
- **Database:** SQLite through Python's built-in `sqlite3` module. No ORM. The database file path is a single setting in `app.py` so tests can point it at a copy.
- **Where SQL lives:** every SQL statement is in `models.py`, and every query is parameterized with `?` placeholders. No SQL in routes or templates, and no SQL built with f-strings or string concatenation.
- **Where validation lives:** every input rule (email, password, vehicle choice, new vehicle fields, file type and size, question length) is a function in `validators.py`, called by the route on the server before anything is saved. No rule is checked only in the browser or in `chat.js`. The question box may use `required` but has no `maxlength` attribute. Flask's `MAX_CONTENT_LENGTH` is set to 50 MB, and a 413 error handler re-renders `/admin/manuals` with "PDFs must be 50 MB or smaller." (criterion 13).
- **Ownership checks:** every query that reads, adds to, or deletes a conversation or its messages filters by both the conversation id and the signed-in user's id. A conversation that exists but belongs to someone else returns the same 404 as one that does not exist.
- **Role checks:** every `/admin` route checks that the signed-in user's role is `admin` and returns 403 otherwise. `/vehicle`, `/chat`, and every `/conversations` page return 403 for admins, except that a request for a specific conversation returns 404 so it never reveals whether that conversation exists. The signup route ignores any `role` field in the form.
- **Where AI calls live:** all calls to the AI provider (embeddings and answer generation) are in `ai.py`. The provider is the Google Gemini API, free tier, through the `google-genai` package. Answers use `gemini-3.5-flash-lite`. Embeddings use `gemini-embedding-001` with `output_dimensionality=768`, `task_type="RETRIEVAL_DOCUMENT"` for manual chunks and `task_type="RETRIEVAL_QUERY"` for questions. Both model names are settings at the top of `ai.py`, and the team confirms both are free for its keys in Google AI Studio before the build starts.
- **Fake provider for tests:** when `TESTING=1`, `ai.py` uses a fake that makes no network calls. Its embedding lowercases the text, takes each run of 4 or more letters as a word, and adds 1 to position `zlib.crc32(word) % 768`, returning 768 floats, so chunks that share words with the question score higher. With the fixture text above, "How do I turn off lane keep assist?" scores 0.87 against page 2 and 0 against pages 1 and 3, and "Who won the 2020 World Series?" scores 0 against every page. Its answer is "Based on your manual: " followed by the first sentence of the best chunk. It can be told to raise a rate-limit error or a missing-key error (criteria 15 and 20). If the environment variable `FAKE_DELAY_SECONDS` is set, the fake waits that many seconds before returning an answer, so the "Thinking..." label in criterion 32 stays on screen long enough to check by hand. Automated tests leave it unset and never call the real Gemini API.
- **Grounding rules:** each answer uses the 4 most similar chunks from the manual of the conversation's vehicle (not the driver's current vehicle). Similarity is cosine similarity computed in Python. If the best similarity is below `SIMILARITY_CUTOFF` (a setting in `ai.py`, starting at 0.55 and tuned by the team against the real Camry manual before CP2), the app replies "I'm not sure. I couldn't find that in your [vehicle] manual." without calling the answer model. Only chunks at or above `SIMILARITY_CUTOFF` are passed to the model, and each of them is saved as a citation. The answer prompt tells the model to answer only from those chunks. The Source line names the PDF page of the single most similar chunk.
- **Free-tier limits:** manual chunks are embedded in batches of up to 100 texts per request. If any batch fails, the whole upload is rolled back (criterion 15). A rate-limit error (HTTP 429) during a question is handled the same way as any other provider error (criterion 20).
- **What is sent to Google:** free-tier prompts may be used by Google to improve its products and may be read by human reviewers. Only the question text and manual chunk text are sent. The driver's email, user id, and earlier messages are never included in a request to Gemini.
- **Passwords and sessions:** passwords are hashed with `werkzeug.security`. Sessions use Flask's signed session cookie. Sign out is a POST to `/logout` that clears the session.
- **Secrets:** `GEMINI_API_KEY` and `FLASK_SECRET_KEY` are read from a `.env` file through `python-dotenv`. `.env` is listed in `.gitignore`. Each team member uses their own Gemini key. No key appears in code, templates, or the database.
- **Output escaping:** templates use Jinja autoescaping. The `|safe` filter and `Markup()` are not used on any question, answer, or manual text.
- **Allowed installs:** `flask`, `python-dotenv`, `pypdf`, `google-genai`, `pytest`. Nothing else may be installed, including the older `google-generativeai` package, `openai`, SQLAlchemy, Flask-Login, LangChain, LlamaIndex, Chroma, Pinecone, FAISS, or any other vector database.
- **Debug mode:** Flask debug mode is off unless `FLASK_DEBUG=1` is set in `.env`.

## Risks

**Risk 1: Broken object-level access (a user reaches another user's record by changing the id in the URL).**
Where it would appear: `/conversations/<id>`, its follow-up POST, and `/conversations/<id>/delete`. The easy way to write these routes is `SELECT ... FROM conversations WHERE id = ?`, which checks that the conversation exists but not who owns it. Because conversation ids are small sequential integers, driver A can read, add to, or delete driver B's questions about their car just by changing the number. The admin role makes this more likely, since an agent may add "admins can see everything" by default.
Caught by: criteria 27 (read), 28 (delete and follow-up), and 30 (admin).

**Risk 2: Validation that exists only in the browser.**
Where it would appear: the question box on `/chat` and `/conversations/<id>`, and the vehicle list on `/vehicle`. An agent building the chat page is likely to treat the red "N / 500" counter in `chat.js` as the length check, and an agent building `/vehicle` is likely to trust the dropdown to offer only vehicles with a manual. A direct POST skips both. An over-long question would be saved and sent to Gemini, using up the free-tier daily quota and risking a prompt past the model's input limit. A vehicle with no manual would be saved to the profile, and every later question would fail.
Caught by: criterion 19 (a direct POST of a 501-character question) and criterion 8 (a direct POST of the RAV4's id), with criterion 18 for empty input. Both criteria send the request without a browser, so neither the counter nor the dropdown can hide a missing server check.

## AI Use Note

**Tools and sections.** We used Claude to draft the sections from our Design Thinking materials (the Product Strategy and Execution Plan, the wireframes, and our CP0 scope paragraph), and a separate Claude agent to audit the draft against the CP1 rubric. The team reviewed every section, cut features to fit October 22 to November 5, and chose the data model and the two risks.

**One criterion the AI drafted that we changed, and why.** The AI's first draft assumed the OpenAI API, and its criterion for provider failures (now criterion 20) said only that a missing key or a provider error shows "The assistant is unavailable right now." We chose Google's Gemini API instead, because OpenAI requires prepaid credit and Gemini's free tier covers a class project. The free tier has tight daily limits, so for us a rate-limit (429) response is an expected event, not a rare failure. We changed criterion 20 to name `GEMINI_API_KEY` and to include the 429 case, so the build has to handle running out of quota without crashing or saving a half-finished answer.
