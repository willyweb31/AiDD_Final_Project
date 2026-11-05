"""Every input rule. Routes call these on the server before anything is saved.

Each function returns (clean_value, error). error is None when the input is fine,
otherwise the exact message from the spec to show the user.
"""

import re

import ai
import models

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_EMAIL_LENGTH = 254
MIN_PASSWORD_LENGTH = 8
MAX_QUESTION_LENGTH = 500
MAX_VEHICLE_FIELD_LENGTH = 50
MAX_PDF_BYTES = 50 * 1024 * 1024
# SQLite stores integers in 8 bytes; a bigger id cannot match any row.
MAX_DB_ID = 2**63 - 1

PDF_TOO_LARGE = "PDFs must be 50 MB or smaller."
CHOOSE_FROM_LIST = "Choose a vehicle from the list."
ADD_VEHICLE_FIELDS = "Enter make, model, a 4-digit year, and trim."
NOT_A_PDF = "Upload a PDF file."
NO_READABLE_TEXT = "This PDF has no text we can read. Upload a PDF with selectable text."


def clean_email(raw):
    return (raw or "").strip().lower()


def validate_signup(conn, email, password):
    email = clean_email(email)
    password = password or ""
    if not email:
        return None, "Email is required."
    if len(email) > MAX_EMAIL_LENGTH or not EMAIL_PATTERN.match(email):
        return None, "Enter a valid email address."
    if len(password) < MIN_PASSWORD_LENGTH:
        return None, "Password must be at least 8 characters."
    if models.get_user_by_email(conn, email) is not None:
        return None, "An account with this email already exists."
    return email, None


def _vehicle_id(raw):
    """Plain ASCII digits only, so "1_0", "-1", and non-Latin digits are refused,
    and short enough that SQLite can compare it."""
    raw = (raw or "").strip()
    if not re.fullmatch(r"[0-9]{1,18}", raw):
        return None
    return int(raw)


def valid_conversation_id(conversation_id):
    """A conversation id from the URL that SQLite can look up. Anything else is
    answered with the same 404 as a conversation that does not exist."""
    return 0 < conversation_id <= MAX_DB_ID


def validate_vehicle_choice(conn, raw):
    """A driver may only choose a real vehicle that has a manual."""
    vehicle_id = _vehicle_id(raw)
    if vehicle_id is None or not models.vehicle_has_manual(conn, vehicle_id):
        return None, CHOOSE_FROM_LIST
    return vehicle_id, None


def validate_new_vehicle(conn, make, model, year, trim):
    # Collapse runs of spaces so "Land  Cruiser" and "Land Cruiser" are one vehicle.
    make, model, trim = (" ".join((v or "").split()) for v in (make, model, trim))
    year = (year or "").strip()
    if not (make and model and trim) or not re.fullmatch(r"[1-9][0-9]{3}", year):
        return None, ADD_VEHICLE_FIELDS
    if max(len(make), len(model), len(trim)) > MAX_VEHICLE_FIELD_LENGTH:
        return None, ADD_VEHICLE_FIELDS
    if models.find_vehicle(conn, make, model, int(year), trim) is not None:
        return None, "This vehicle already exists."
    return {"make": make, "model": model, "year": int(year), "trim": trim}, None


def validate_upload_vehicle(conn, raw):
    """A manual may only be uploaded for a real vehicle that has none yet."""
    vehicle_id = _vehicle_id(raw)
    if vehicle_id is None or models.get_vehicle(conn, vehicle_id) is None:
        return None, CHOOSE_FROM_LIST
    if models.vehicle_has_manual(conn, vehicle_id):
        return None, "This vehicle already has a manual."
    return vehicle_id, None


def validate_pdf(file):
    """Returns the text of each page of an uploaded PDF."""
    if file is None or not file.filename:
        return None, "Choose a PDF to upload."
    data = file.read()
    if len(data) > MAX_PDF_BYTES:
        return None, PDF_TOO_LARGE
    # A file was chosen, so an empty one is a bad file, not a missing one.
    if not data or not file.filename.lower().endswith(".pdf") or not data.startswith(b"%PDF-"):
        return None, NOT_A_PDF
    try:
        pages = ai.read_pdf_pages(data)
    except ai.UnreadablePdf:
        return None, NOT_A_PDF
    if not pages:
        return None, NOT_A_PDF
    if not any(pages):
        # Scanned pages: nothing to answer from, and trying again will not help.
        return None, NO_READABLE_TEXT
    return pages, None


def validate_question(raw):
    # Browsers send each new line as \r\n; count it once, as the live counter does.
    question = (raw or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not question:
        return None, "Type a question first."
    if len(question) > MAX_QUESTION_LENGTH:
        return None, "Questions must be 500 characters or fewer."
    return question, None
