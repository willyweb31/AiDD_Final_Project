"""Evals added after CP2, from the validator-reviewer and security-reviewer runs
and the design review (see CP3_Written.md). The existing evals are unchanged.

Each test is named after the spec criterion it extends: eNN checks criterion NN.
"""

import io

import pytest
from pypdf import PdfWriter

from conftest import (
    DRIVER_EMAIL,
    add_vehicle,
    ask,
    choose_vehicle,
    latest_conversation_id,
    page_text,
    signup,
    upload_manual,
)

HUGE_ID = "99999999999999999999"  # larger than SQLite can store (2**63 - 1)


def blank_pdf():
    """A valid one-page PDF with no text, like a scanned manual."""
    out = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(out)
    return out.getvalue()


def add_se_vehicle(admin, ids):
    add_vehicle(admin, "Toyota", "Camry", "2025", "SE")
    return ids.lookup(2025, "Toyota", "Camry", "SE")


# ----------------------------------------------------- accounts (1-6) ---


def test_e04_signup_trims_and_lowercases_email(client, db):
    signup(client, email="  Driver1@Test.COM  ")
    assert db("SELECT 1 FROM users WHERE email = ?", ("driver1@test.com",))


def test_e02_signup_rejects_an_overlong_email(client, db):
    before = db.count("users")
    resp = signup(client, email="a" * 250 + "@x.com")
    assert "Enter a valid email address." in page_text(resp)
    assert db.count("users") == before


# --------------------------------------------- vehicle profile (7-9) ---


@pytest.mark.parametrize("value", [HUGE_ID, "-1", "1_0", "١"])  # last is Arabic-Indic 1
def test_e08_vehicle_post_rejects_ids_that_are_not_plain_numbers(client, db, value):
    signup(client)
    resp = choose_vehicle(client, value)
    assert "Choose a vehicle from the list." in page_text(resp)
    assert db("SELECT vehicle_id FROM users WHERE email = ?", (DRIVER_EMAIL,))[0]["vehicle_id"] is None


# ------------------------------------------- manual library (10-15) ---


def test_e10_upload_accepts_uppercase_extension(admin, db, ids):
    se_id = add_se_vehicle(admin, ids)
    upload_manual(admin, se_id, "MANUAL.PDF")
    assert db("SELECT 1 FROM manuals WHERE vehicle_id = ?", (se_id,))


@pytest.mark.parametrize(
    "fields",
    [
        ("   ", "Camry", "2025", "SE"),
        ("Toyota", "Camry", "202", "SE"),
        ("Toyota", "Camry", "20255", "SE"),
        ("Toyota", "Camry", "0000", "SE"),
        ("T" * 51, "Camry", "2025", "SE"),
    ],
)
def test_e11_add_vehicle_rejects_blank_short_and_oversized_fields(admin, db, fields):
    before = db.count("vehicles")
    resp = add_vehicle(admin, *fields)
    assert "Enter make, model, a 4-digit year, and trim." in page_text(resp)
    assert db.count("vehicles") == before


def test_e11_extra_spaces_do_not_make_a_new_vehicle(admin, db):
    add_vehicle(admin, "Land", "Cruiser", "2024", "LE")
    before = db.count("vehicles")
    resp = add_vehicle(admin, "Land", "Cruiser", "2024", "  le ")
    assert "This vehicle already exists." in page_text(resp)
    resp = add_vehicle(admin, "Land", "Cr  uiser", "2024", "LE")  # inner double space
    assert "This vehicle already exists." not in page_text(resp)  # collapses to "Cr uiser", a different model
    assert db.count("vehicles") == before + 1


def test_e12_upload_rejects_a_corrupt_pdf(admin, db, ids):
    se_id = add_se_vehicle(admin, ids)
    before = (db.count("manuals"), db.count("chunks"))
    resp = upload_manual(admin, se_id, "manual.pdf", b"%PDF-1.4 not really a pdf")
    assert "Upload a PDF file." in page_text(resp)
    assert (db.count("manuals"), db.count("chunks")) == before


def test_e12_a_chosen_file_with_no_bytes_is_not_a_pdf(admin, db, ids):
    se_id = add_se_vehicle(admin, ids)
    resp = upload_manual(admin, se_id, "empty.pdf", b"")
    assert "Upload a PDF file." in page_text(resp)
    assert "Choose a PDF to upload." not in page_text(resp)
    assert db.count("manuals") == 1  # only the Camry from the seed


def test_e12_a_pdf_with_no_readable_text_is_refused_with_a_clear_message(admin, db, ids):
    se_id = add_se_vehicle(admin, ids)
    before = (db.count("manuals"), db.count("chunks"))
    resp = upload_manual(admin, se_id, "scan.pdf", blank_pdf())
    assert "This PDF has no text we can read." in page_text(resp)
    assert (db.count("manuals"), db.count("chunks")) == before


def test_e14_upload_for_a_missing_vehicle_is_refused(admin, db):
    before = db.count("manuals")
    assert "Choose a vehicle from the list." in page_text(upload_manual(admin, 9999))
    assert "Choose a vehicle from the list." in page_text(upload_manual(admin, HUGE_ID))
    assert db.count("manuals") == before


def test_e15_a_short_embedding_reply_rolls_back_the_upload(admin, db, ids, monkeypatch):
    import ai

    se_id = add_se_vehicle(admin, ids)
    before = (db.count("manuals"), db.count("chunks"))
    real = ai.embed_documents
    monkeypatch.setattr(ai, "embed_documents", lambda texts: real(texts)[:-1])
    resp = upload_manual(admin, se_id)
    assert "The manual could not be processed. Try again." in page_text(resp)
    assert (db.count("manuals"), db.count("chunks")) == before


def test_e15_wrong_size_embeddings_roll_back_the_upload(admin, db, ids, monkeypatch):
    import ai

    se_id = add_se_vehicle(admin, ids)
    before = (db.count("manuals"), db.count("chunks"))
    monkeypatch.setattr(ai, "embed_documents", lambda texts: [[0.0] * 5 for _ in texts])
    resp = upload_manual(admin, se_id)
    assert "The manual could not be processed. Try again." in page_text(resp)
    assert (db.count("manuals"), db.count("chunks")) == before


# --------------------------------------------------- ask MyCarAI (16-22) ---


def test_e19_a_new_line_counts_once_like_the_live_counter(driver, db):
    # 491 letters and 9 new lines: the counter reads 500 / 500. A browser sends
    # each new line as \r\n, so the raw text is 509 characters long.
    lines = ["a" * 49] * 9 + ["a" * 50]
    resp = ask(driver, "\r\n".join(lines))
    assert "Questions must be 500 characters or fewer." not in page_text(resp)
    saved = db("SELECT content FROM messages WHERE sender = 'driver'")[0]["content"]
    assert saved == "\n".join(lines) and len(saved) == 500


def test_e19_one_more_character_after_new_lines_is_still_refused(driver, db):
    lines = ["a" * 49] * 9 + ["a" * 51]  # counter reads 501
    resp = ask(driver, "\r\n".join(lines))
    assert "Questions must be 500 characters or fewer." in page_text(resp)
    assert db.count("messages") == 0


def test_e19_spaces_around_the_question_do_not_count(driver, db):
    ask(driver, "  " + "a" * 500 + "  ")
    assert db("SELECT 1 FROM messages WHERE sender = 'driver' AND content = ?", ("a" * 500,))


def test_e20_unavailable_message_is_a_calm_notice_not_a_typing_error(driver, fake_failure):
    fake_failure("rate_limit")
    page = page_text(ask(driver, "How do I turn off lane keep assist?"))
    assert "The assistant is unavailable right now. Please try again." in page
    assert 'class="error calm"' in page
    typing_error = page_text(ask(driver, "   "))
    assert 'class="error calm"' not in typing_error


def test_e17_the_not_sure_reply_is_marked_so_it_can_look_calm(driver):
    unsure = page_text(ask(driver, "Who won the 2020 World Series?"))
    assert 'class="message assistant unsure"' in unsure


def test_e16_a_sourced_answer_is_not_marked_not_sure(driver):
    answered = page_text(ask(driver, "How do I turn off lane keep assist?"))
    assert 'class="message assistant"' in answered
    assert "unsure" not in answered.split('<ol class="thread">')[1].split("</ol>")[0]


# ---------------------------------------------- conversation history (23-25) ---


def test_e24_a_conversation_id_too_big_for_the_database_is_a_404(driver):
    resp = driver.get(f"/conversations/{HUGE_ID}")
    assert resp.status_code == 404
    assert "Conversation not found." in page_text(resp)
    assert driver.post(f"/conversations/{HUGE_ID}/delete").status_code == 404
    assert driver.post(f"/conversations/{HUGE_ID}", data={"question": "hello"}).status_code == 404


def test_e25_get_on_delete_shows_a_plain_405_page(driver, db):
    ask(driver, "How do I turn off lane keep assist?")
    cid = latest_conversation_id(db)
    resp = driver.get(f"/conversations/{cid}/delete")
    assert resp.status_code == 405
    assert "That page can't be opened this way." in page_text(resp)
    assert db.count("conversations") == 1


# ------------------------------------------------- users and permissions ---


def test_e29_a_post_from_another_site_is_refused(driver, db):
    ask(driver, "How do I turn off lane keep assist?")
    cid = latest_conversation_id(db)
    for origin in ("same-site", "cross-site"):
        resp = driver.post(f"/conversations/{cid}/delete", headers={"Sec-Fetch-Site": origin})
        assert resp.status_code == 403, origin
    assert db.count("conversations") == 1


def test_e29_posts_from_our_own_pages_and_typed_links_still_work(driver, db):
    for origin in ("same-origin", "none"):
        resp = driver.post("/chat", data={"question": "How do I turn off lane keep assist?"}, headers={"Sec-Fetch-Site": origin})
        assert resp.status_code == 302, origin
    assert db.count("conversations") == 2


def test_e29_an_unknown_admin_action_shows_a_plain_400_page(admin):
    resp = admin.post("/admin/manuals", data={"action": "bogus"})
    assert resp.status_code == 400
    assert "That request wasn't understood." in page_text(resp)


def test_e13_a_driver_posting_too_much_is_not_told_about_pdfs(driver, flask_app, monkeypatch):
    monkeypatch.setitem(flask_app.config, "MAX_CONTENT_LENGTH", 2000)
    resp = driver.post("/chat", data={"question": "a" * 5000})
    assert resp.status_code == 413
    assert "PDFs must be 50 MB or smaller." not in page_text(resp)
    assert "That was too much to send at once." in page_text(resp)


# ------------------------------------------------- headers and page shell ---


@pytest.mark.parametrize("path", ["/login", "/signup", "/chat", "/conversations", "/vehicle"])
def test_security_headers_are_on_every_page(driver, path):
    resp = driver.get(path, follow_redirects=True)
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    csp = resp.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp and "frame-ancestors 'none'" in csp
    assert "script-src" not in csp  # chat.js is our own file, covered by default-src 'self'


def test_a_head_request_is_treated_like_a_get(new_client, driver, admin):
    # Link previewers and health checks send HEAD; it must not be read as a form post.
    visitor = new_client()
    assert visitor.head("/login").status_code == 200
    assert visitor.head("/signup").status_code == 200
    assert driver.head("/chat").status_code == 200
    assert admin.head("/admin/manuals").status_code == 200


def test_the_session_cookie_is_http_only_and_same_site(client):
    resp = client.post("/signup", data={"email": DRIVER_EMAIL, "password": "camry2024!"})
    cookie = resp.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie


def test_the_nav_marks_the_page_you_are_on(driver):
    chat = page_text(driver.get("/chat"))
    assert 'aria-current="page">Ask</a>' in chat
    assert 'aria-current="page">My conversations</a>' not in chat
    history = page_text(driver.get("/conversations"))
    assert 'aria-current="page">My conversations</a>' in history


def test_the_chat_page_suggests_questions_only_before_the_first_one(driver):
    first = page_text(driver.get("/chat"))
    assert "Things you can ask" in first
    ask(driver, "How do I turn off lane keep assist?")
    cid = latest_conversation_id_from_page(driver)
    assert "Things you can ask" not in page_text(driver.get(f"/conversations/{cid}"))


def latest_conversation_id_from_page(driver):
    page = page_text(driver.get("/conversations"))
    return int(page.split("/conversations/")[1].split('"')[0])
