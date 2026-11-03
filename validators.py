"""Every input rule. Routes call these on the server before anything is saved.

Each function returns (clean_value, error). error is None when the input is fine,
otherwise the exact message from the spec to show the user.
"""

import re

import ai
import models

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8
MAX_QUESTION_LENGTH = 500
MAX_PDF_BYTES = 50 * 1024 * 1024

PDF_TOO_LARGE = "PDFs must be 50 MB or smaller."
CHOOSE_FROM_LIST = "Choose a vehicle from the list."


def clean_email(raw):
    return (raw or "").strip().lower()


def validate_signup(conn, email, password):
    email = clean_email(email)
    password = password or ""
    if not email:
        return None, "Email is required."
    if not EMAIL_PATTERN.match(email):
        return None, "Enter a valid email address."
    if len(password) < MIN_PASSWORD_LENGTH:
        return None, "Password must be at least 8 characters."
    if models.get_user_by_email(conn, email) is not None:
        return None, "An account with this email already exists."
    return email, None


def _vehicle_id(raw):
    try:
        return int((raw or "").strip())
    except ValueError:
        return None


def validate_vehicle_choice(conn, raw):
    """A driver may only choose a real vehicle that has a manual."""
    vehicle_id = _vehicle_id(raw)
    if vehicle_id is None or not models.vehicle_has_manual(conn, vehicle_id):
        return None, CHOOSE_FROM_LIST
    return vehicle_id, None


def validate_new_vehicle(conn, make, model, year, trim):
    make, model, year, trim = ((v or "").strip() for v in (make, model, year, trim))
    if not (make and model and trim) or not re.fullmatch(r"\d{4}", year):
        return None, "Enter make, model, a 4-digit year, and trim."
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
    if not data:
        return None, "Choose a PDF to upload."
    if len(data) > MAX_PDF_BYTES:
        return None, PDF_TOO_LARGE
    if not file.filename.lower().endswith(".pdf") or not data.startswith(b"%PDF-"):
        return None, "Upload a PDF file."
    try:
        pages = ai.read_pdf_pages(data)
    except ai.UnreadablePdf:
        return None, "Upload a PDF file."
    if not pages:
        return None, "Upload a PDF file."
    return pages, None


def validate_question(raw):
    question = (raw or "").strip()
    if not question:
        return None, "Type a question first."
    if len(question) > MAX_QUESTION_LENGTH:
        return None, "Questions must be 500 characters or fewer."
    return question, None
