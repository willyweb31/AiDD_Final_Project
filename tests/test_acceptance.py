"""Acceptance criteria 1-31 from .claude/spec.md, run with Flask's test client.

Each test is named after the criterion it checks. Criteria 32-33 (chat.js in a
real browser) are checked by hand and are not here.
"""

from datetime import date

import pytest

from conftest import (
    ADMIN_EMAIL,
    ADMIN_URL,
    DRIVER_EMAIL,
    DRIVER_PASSWORD,
    QUESTION_FIELD,
    add_vehicle,
    ask,
    choose_vehicle,
    latest_conversation_id,
    login,
    logout,
    make_driver,
    page_text,
    redirect_path,
    signup,
    upload_manual,
)

LANE_QUESTION = "How do I turn off lane keep assist?"
LANE_ANSWER = "Based on your manual: Lane keep assist keeps the car in its lane."
CAMRY_SOURCE = "Source: 2024 Toyota Camry XSE Owner's Manual, PDF page 2"
OFF_TOPIC = "Who won the 2020 World Series?"
UNAVAILABLE = "The assistant is unavailable right now. Please try again."
TODAY = date.today().isoformat()


def add_camry_se(admin, ids):
    """Criterion 10's setup: admin adds 2025 Toyota Camry SE with the sample manual."""
    add_vehicle(admin, "Toyota", "Camry", "2025", "SE")
    se_id = ids.lookup(2025, "Toyota", "Camry", "SE")
    assert se_id is not None, "2025 Toyota Camry SE was not added"
    return se_id, upload_manual(admin, se_id)


# ---------------------------------------------------------------- Accounts ---


def test_01_signup_creates_driver_with_hashed_password(client, db):
    before = db.count("users")
    resp = signup(client)
    assert resp.request.path == "/vehicle"
    assert f"Signed in as {DRIVER_EMAIL}" in page_text(resp)
    assert db.count("users") == before + 1
    row = db("SELECT role, password_hash FROM users WHERE email = ?", (DRIVER_EMAIL,))[0]
    assert row["role"] == "driver"
    assert row["password_hash"] != DRIVER_PASSWORD


@pytest.mark.parametrize(
    "email, message",
    [("", "Email is required."), ("not-an-email", "Enter a valid email address.")],
)
def test_02_signup_rejects_bad_email(client, db, email, message):
    before = db.count("users")
    resp = signup(client, email=email)
    assert message in page_text(resp)
    assert db.count("users") == before


def test_03_signup_rejects_short_password(client, db):
    before = db.count("users")
    resp = signup(client, password="abc1234")
    assert "Password must be at least 8 characters." in page_text(resp)
    assert db.count("users") == before


def test_04_signup_rejects_duplicate_email_case_insensitive(client, new_client, db):
    signup(client)
    before = db.count("users")
    resp = signup(new_client(), email="DRIVER1@test.com")
    assert "An account with this email already exists." in page_text(resp)
    assert db.count("users") == before


def test_05_login_lands_on_vehicle_then_chat_and_logout(client, new_client, ids):
    signup(client)
    logout(client)

    resp = login(client)
    assert resp.request.path == "/vehicle"
    assert f"Signed in as {DRIVER_EMAIL}" in page_text(resp)

    choose_vehicle(client, ids.camry)
    logout(client)
    resp = login(client)
    assert resp.request.path == "/chat"
    assert f"Signed in as {DRIVER_EMAIL}" in page_text(resp)

    resp = logout(client)
    assert resp.request.path == "/login"
    assert "You are signed out." in page_text(resp)
    assert redirect_path(client.get("/chat")) == "/login"


def test_06_login_failure_message_is_the_same(client):
    signup(client)
    logout(client)
    wrong_password = login(client, DRIVER_EMAIL, "wrong-password")
    no_account = login(client, "nobody@test.com", DRIVER_PASSWORD)
    for resp in (wrong_password, no_account):
        assert resp.request.path == "/login"
        assert "Email or password is incorrect." in page_text(resp)


# --------------------------------------------------------- Vehicle profile ---


def test_07_vehicle_list_only_has_vehicles_with_manuals(client, ids):
    signup(client)
    text = page_text(client.get("/vehicle"))
    assert "2024 Toyota Camry XSE" in text
    assert "2024 Toyota RAV4 XLE" not in text

    resp = choose_vehicle(client, ids.camry)
    assert resp.request.path == "/chat"
    assert "Ask about your 2024 Toyota Camry XSE" in page_text(resp)


@pytest.mark.parametrize("bad_value", ["9999", "abc", "RAV4"])
def test_08_vehicle_post_is_validated_on_server(client, db, ids, bad_value):
    signup(client)
    value = ids.rav4 if bad_value == "RAV4" else bad_value
    resp = choose_vehicle(client, value)
    assert "Choose a vehicle from the list." in page_text(resp)
    row = db("SELECT vehicle_id FROM users WHERE email = ?", (DRIVER_EMAIL,))[0]
    assert row["vehicle_id"] is None


def test_09_chat_requires_a_vehicle(client):
    signup(client)
    resp = client.get("/chat", follow_redirects=True)
    assert resp.request.path == "/vehicle"
    assert "Choose your vehicle first." in page_text(resp)


# ---------------------------------------------------------- Manual library ---


def test_10_admin_adds_vehicle_and_uploads_manual(admin, db, ids):
    se_id, _ = add_camry_se(admin, ids)
    text = page_text(admin.get(ADMIN_URL))
    assert "2025 Toyota Camry SE Owner's Manual" in text
    assert ADMIN_EMAIL in text
    assert TODAY in text
    assert "Ready" in text

    manual = db("SELECT id, page_count FROM manuals WHERE vehicle_id = ?", (se_id,))
    assert len(manual) == 1
    assert manual[0]["page_count"] == 3
    pages = db(
        "SELECT DISTINCT page_number FROM chunks WHERE manual_id = ? ORDER BY page_number",
        (manual[0]["id"],),
    )
    assert [p["page_number"] for p in pages] == [1, 2, 3]


@pytest.mark.parametrize(
    "fields, message",
    [
        (("", "Camry", "2025", "SE"), "Enter make, model, a 4-digit year, and trim."),
        (("Toyota", "Camry", "20x5", "SE"), "Enter make, model, a 4-digit year, and trim."),
        (("Toyota", "Camry", "2024", "XSE"), "This vehicle already exists."),
    ],
)
def test_11_add_vehicle_is_validated(admin, db, fields, message):
    before = db.count("vehicles")
    resp = add_vehicle(admin, *fields)
    assert message in page_text(resp)
    assert db.count("vehicles") == before


@pytest.mark.parametrize(
    "filename, content",
    [("manual.docx", b"PK\x03\x04 not really a docx"), ("manual.pdf", b"just some text")],
)
def test_12_upload_rejects_non_pdf(admin, db, ids, filename, content):
    add_vehicle(admin, "Toyota", "Camry", "2025", "SE")
    se_id = ids.lookup(2025, "Toyota", "Camry", "SE")
    manuals, chunks = db.count("manuals"), db.count("chunks")
    resp = upload_manual(admin, se_id, filename, content)
    assert "Upload a PDF file." in page_text(resp)
    assert (db.count("manuals"), db.count("chunks")) == (manuals, chunks)


def test_13_upload_requires_a_file(admin, db, ids):
    add_vehicle(admin, "Toyota", "Camry", "2025", "SE")
    se_id = ids.lookup(2025, "Toyota", "Camry", "SE")
    before = db.count("manuals")
    resp = upload_manual(admin, se_id, filename=None)
    assert "Choose a PDF to upload." in page_text(resp)
    assert db.count("manuals") == before


def test_13_upload_rejects_pdf_over_50_mb(admin, db, ids):
    add_vehicle(admin, "Toyota", "Camry", "2025", "SE")
    se_id = ids.lookup(2025, "Toyota", "Camry", "SE")
    before = db.count("manuals")
    big = b"%PDF-1.4\n" + b"0" * (50 * 1024 * 1024 + 1)
    resp = upload_manual(admin, se_id, "big.pdf", big)
    assert "PDFs must be 50 MB or smaller." in page_text(resp)
    assert db.count("manuals") == before


def test_14_one_manual_per_vehicle(admin, db, ids):
    manuals, chunks = db.count("manuals"), db.count("chunks")
    resp = upload_manual(admin, ids.camry)
    assert "This vehicle already has a manual." in page_text(resp)
    assert (db.count("manuals"), db.count("chunks")) == (manuals, chunks)


def test_15_failed_embedding_rolls_back_upload(admin, db, ids, fake_failure):
    add_vehicle(admin, "Toyota", "Camry", "2025", "SE")
    se_id = ids.lookup(2025, "Toyota", "Camry", "SE")
    manuals, chunks = db.count("manuals"), db.count("chunks")
    fake_failure("rate_limit")
    resp = upload_manual(admin, se_id)
    assert "The manual could not be processed. Try again." in page_text(resp)
    assert (db.count("manuals"), db.count("chunks")) == (manuals, chunks)


# ------------------------------------------------------------ Ask MyCarAI ---


def test_16_answer_is_grounded_with_source(driver):
    text = page_text(ask(driver, LANE_QUESTION))
    assert LANE_QUESTION in text
    assert LANE_ANSWER in text
    assert CAMRY_SOURCE in text


def test_17_off_topic_question_gets_not_sure(driver, db):
    text = page_text(ask(driver, OFF_TOPIC))
    assert "I'm not sure" in text
    assert "Source:" not in text
    rows = db("SELECT sender, content FROM messages ORDER BY id")
    assert rows[-2]["sender"] == "driver" and rows[-2]["content"] == OFF_TOPIC
    assert rows[-1]["sender"] == "assistant" and rows[-1]["content"].startswith("I'm not sure")


@pytest.mark.parametrize("question", ["", "     "])
def test_18_empty_question_is_rejected(driver, db, question):
    before = (db.count("messages"), db.count("conversations"))
    resp = ask(driver, question)
    assert "Type a question first." in page_text(resp)
    assert (db.count("messages"), db.count("conversations")) == before


def test_19_question_length_is_checked_on_server(driver, db):
    before = db.count("messages")
    resp = ask(driver, "a" * 501)
    assert "Questions must be 500 characters or fewer." in page_text(resp)
    assert db.count("messages") == before

    resp = ask(driver, "a" * 500)
    assert db("SELECT 1 FROM messages WHERE sender = 'driver' AND content = ?", ("a" * 500,))
    assert "I'm not sure" in page_text(resp)


@pytest.mark.parametrize("mode", ["missing_key", "rate_limit"])
def test_20_provider_failure_is_handled(driver, db, fake_failure, monkeypatch, mode):
    if mode == "missing_key":
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    fake_failure(mode)
    before = (db.count("messages"), db.count("conversations"))
    resp = ask(driver, LANE_QUESTION)
    text = page_text(resp)
    assert UNAVAILABLE in text
    assert "Traceback" not in text
    assert (db.count("messages"), db.count("conversations")) == before


def test_21_question_html_is_escaped(driver):
    raw = ask(driver, "<script>alert(1)</script>").get_data(as_text=True)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in raw
    assert "<script>alert(1)</script>" not in raw


def test_22_follow_up_uses_the_conversations_vehicle(driver, admin, db, ids):
    ask(driver, LANE_QUESTION)
    conv_id = latest_conversation_id(db)
    se_id, _ = add_camry_se(admin, ids)
    choose_vehicle(driver, se_id)

    convs = db.count("conversations")
    msgs = db("SELECT COUNT(*) AS n FROM messages WHERE conversation_id = ?", (conv_id,))[0]["n"]
    text = page_text(ask(driver, "Where is the lane assist button?", conv_id))

    after = db("SELECT COUNT(*) AS n FROM messages WHERE conversation_id = ?", (conv_id,))[0]["n"]
    assert after == msgs + 2
    assert db.count("conversations") == convs
    assert "Source: 2024 Toyota Camry XSE Owner's Manual" in text
    assert "2025 Toyota Camry SE Owner's Manual" not in text


# ---------------------------------------------------- Conversation history ---


def test_23_history_lists_newest_first_with_full_thread(driver, db):
    ask(driver, OFF_TOPIC)  # an older conversation
    first = "How do I turn off lane keep assist on my Camry when I drive on the highway?"
    follow_up = "Where is the lane assist button?"
    assert len(first) == 75
    ask(driver, first)
    conv_id = latest_conversation_id(db)
    ask(driver, follow_up, conv_id)

    listing = page_text(driver.get("/conversations"))
    title = first[:60]
    assert title in listing
    assert listing.index(title) < listing.index(OFF_TOPIC[:60])
    assert "2024 Toyota Camry XSE" in listing
    assert TODAY in listing
    assert db("SELECT title FROM conversations WHERE id = ?", (conv_id,))[0]["title"] == title

    thread = page_text(driver.get(f"/conversations/{conv_id}"))
    assert thread.index(first) < thread.index(follow_up)
    assert thread.count("Source: 2024 Toyota Camry XSE Owner's Manual, PDF page") == 2


def test_24_missing_conversation_is_404(driver):
    resp = driver.get("/conversations/9999")
    assert resp.status_code == 404
    assert "Conversation not found." in page_text(resp)


def test_25_delete_removes_conversation_messages_and_citations(driver, db):
    ask(driver, LANE_QUESTION)
    conv_id = latest_conversation_id(db)

    assert driver.get(f"/conversations/{conv_id}/delete").status_code == 405
    assert db("SELECT 1 FROM conversations WHERE id = ?", (conv_id,))

    message_ids = [r["id"] for r in db("SELECT id FROM messages WHERE conversation_id = ?", (conv_id,))]
    driver.post(f"/conversations/{conv_id}/delete", follow_redirects=True)

    assert LANE_QUESTION not in page_text(driver.get("/conversations"))
    assert not db("SELECT 1 FROM conversations WHERE id = ?", (conv_id,))
    assert not db("SELECT 1 FROM messages WHERE conversation_id = ?", (conv_id,))
    marks = ",".join("?" * len(message_ids))
    assert not db(f"SELECT 1 FROM citations WHERE message_id IN ({marks})", message_ids)


# ---------------------------------------------------- Users and permissions ---


@pytest.mark.parametrize("path", ["/chat", "/conversations", "/vehicle", ADMIN_URL])
def test_26_visitors_are_sent_to_login(client, path):
    assert redirect_path(client.get(path)) == "/login"


def test_27_driver_cannot_read_another_drivers_conversation(driver, new_client, db, ids):
    secret = "Where is the spare key hidden in my Camry?"
    driver_b = make_driver(new_client, "driverb@test.com", ids.camry)
    ask(driver_b, secret)
    conv_b = latest_conversation_id(db, "driverb@test.com")

    resp = driver.get(f"/conversations/{conv_b}")
    assert resp.status_code == 404
    assert "Conversation not found." in page_text(resp)
    assert secret not in page_text(resp)


def test_28_driver_cannot_change_another_drivers_conversation(driver, new_client, db, ids):
    driver_b = make_driver(new_client, "driverb@test.com", ids.camry)
    ask(driver_b, LANE_QUESTION)
    conv_b = latest_conversation_id(db, "driverb@test.com")
    before = (db.count("conversations"), db.count("messages"))

    assert driver.post(f"/conversations/{conv_b}/delete").status_code == 404
    assert driver.post(f"/conversations/{conv_b}", data={QUESTION_FIELD: "hi"}).status_code == 404
    assert (db.count("conversations"), db.count("messages")) == before


def test_29_drivers_cannot_use_admin_pages(driver, db, ids):
    before = (db.count("vehicles"), db.count("manuals"), db.count("chunks"))
    assert driver.get(ADMIN_URL).status_code == 403
    assert add_vehicle(driver, "Toyota", "Camry", "2025", "SE").status_code == 403
    assert upload_manual(driver, ids.rav4).status_code == 403
    assert (db.count("vehicles"), db.count("manuals"), db.count("chunks")) == before


def test_30_admin_cannot_use_driver_pages(driver, admin, db):
    ask(driver, LANE_QUESTION)
    conv_id = latest_conversation_id(db)
    before = (db.count("conversations"), db.count("messages"))

    assert admin.get(f"/conversations/{conv_id}").status_code == 404
    assert admin.post(f"/conversations/{conv_id}/delete").status_code == 404
    assert (db.count("conversations"), db.count("messages")) == before
    for path in ("/chat", "/vehicle", "/conversations"):
        assert admin.get(path).status_code == 403, path


def test_31_signup_ignores_role_field(client, db):
    signup(client, "sneaky@test.com", DRIVER_PASSWORD, role="admin")
    assert db("SELECT role FROM users WHERE email = ?", ("sneaky@test.com",))[0]["role"] == "driver"
