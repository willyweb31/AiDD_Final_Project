"""Shared fixtures for the MyCarAI acceptance tests (.claude/spec.md, criteria 1-31).

The spec fixes the behaviour but not every route or form-field name. Every such
assumption lives in the CONTRACT block below; if the build picks a different name,
change it here once rather than in each test.
"""

import html
import os
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlparse

import pytest

# Must be set before ai.py is imported so it picks the fake provider.
os.environ["TESTING"] = "1"
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key")

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------- CONTRACT ---
# app.py exposes a Flask object named `app`, and reads its SQLite path from
# app.config["DATABASE"] (the "single setting" in the Constraints section).
DB_CONFIG_KEY = "DATABASE"
# seed.py exposes seed(db_path) that creates the schema and the seed rows.
SEED_FUNCTION = "seed"
# ai.py exposes FAKE_FAILURE: None, "rate_limit", or "missing_key" (criteria 15, 20).
FAKE_FAILURE_ATTR = "FAKE_FAILURE"

SIGNUP_FIELDS = ("email", "password")
LOGIN_FIELDS = ("email", "password")
VEHICLE_FIELD = "vehicle_id"
QUESTION_FIELD = "question"

# Both admin forms post to /admin/manuals ("sends a POST to add a vehicle or
# upload a manual there", criterion 29), told apart by an `action` field.
ADMIN_URL = "/admin/manuals"
ADD_VEHICLE_ACTION = {"action": "add_vehicle"}
UPLOAD_ACTION = {"action": "upload_manual"}
UPLOAD_FILE_FIELD = "manual"
# ------------------------------------------------------------- END CONTRACT ---

ADMIN_EMAIL = "admin@mycarai.test"
ADMIN_PASSWORD = "admin12345"
DRIVER_EMAIL = "driver1@test.com"
DRIVER_PASSWORD = "camry2024!"
SAMPLE_PDF = FIXTURES / "sample_manual.pdf"


@pytest.fixture
def flask_app(tmp_path):
    import ai
    import app as app_module
    import seed as seed_module

    db_path = str(tmp_path / "test.db")
    flask_app = app_module.app
    flask_app.config.update(TESTING=True, **{DB_CONFIG_KEY: db_path})
    setattr(ai, FAKE_FAILURE_ATTR, None)
    getattr(seed_module, SEED_FUNCTION)(db_path)
    yield flask_app
    setattr(ai, FAKE_FAILURE_ATTR, None)


@pytest.fixture
def db(flask_app):
    """Run read-only SQL against the test database: db("SELECT ...", params)."""

    def query(sql, params=()):
        conn = sqlite3.connect(flask_app.config[DB_CONFIG_KEY])
        conn.row_factory = sqlite3.Row
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()

    query.count = lambda table: query(f"SELECT COUNT(*) AS n FROM {table}")[0]["n"]
    return query


@pytest.fixture
def fake_failure():
    """Make the fake AI provider fail: fake_failure("rate_limit")."""
    import ai

    def set_failure(mode):
        setattr(ai, FAKE_FAILURE_ATTR, mode)

    return set_failure


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture
def new_client(flask_app):
    """Factory for extra clients with their own cookie jar (driver B, admin...)."""
    return flask_app.test_client


@pytest.fixture
def ids(db):
    def vehicle_id(year, make, model, trim):
        rows = db(
            "SELECT id FROM vehicles WHERE year = ? AND make = ? AND model = ? AND trim = ?",
            (year, make, model, trim),
        )
        return rows[0]["id"] if rows else None

    class Ids:
        camry = vehicle_id(2024, "Toyota", "Camry", "XSE")
        rav4 = vehicle_id(2024, "Toyota", "RAV4", "XLE")
        lookup = staticmethod(vehicle_id)

    return Ids


# ------------------------------------------------------------------ helpers ---


def page_text(response):
    """Response HTML with entities decoded, so "Owner&#39;s" matches "Owner's"."""
    return html.unescape(response.get_data(as_text=True))


def redirect_path(response):
    assert response.status_code in (301, 302, 303, 307, 308), response.status_code
    return urlparse(response.headers["Location"]).path


def signup(client, email=DRIVER_EMAIL, password=DRIVER_PASSWORD, **extra):
    data = {SIGNUP_FIELDS[0]: email, SIGNUP_FIELDS[1]: password, **extra}
    return client.post("/signup", data=data, follow_redirects=True)


def login(client, email=DRIVER_EMAIL, password=DRIVER_PASSWORD):
    data = {LOGIN_FIELDS[0]: email, LOGIN_FIELDS[1]: password}
    return client.post("/login", data=data, follow_redirects=True)


def logout(client):
    return client.post("/logout", follow_redirects=True)


def choose_vehicle(client, vehicle_id):
    return client.post("/vehicle", data={VEHICLE_FIELD: vehicle_id}, follow_redirects=True)


def ask(client, question, conversation_id=None):
    url = "/chat" if conversation_id is None else f"/conversations/{conversation_id}"
    return client.post(url, data={QUESTION_FIELD: question}, follow_redirects=True)


def add_vehicle(client, make, model, year, trim):
    data = {**ADD_VEHICLE_ACTION, "make": make, "model": model, "year": year, "trim": trim}
    return client.post(ADMIN_URL, data=data, follow_redirects=True)


def upload_manual(client, vehicle_id, filename="sample_manual.pdf", content=None):
    data = {**UPLOAD_ACTION, VEHICLE_FIELD: vehicle_id}
    if filename is not None:
        import io

        body = SAMPLE_PDF.read_bytes() if content is None else content
        data[UPLOAD_FILE_FIELD] = (io.BytesIO(body), filename)
    return client.post(
        ADMIN_URL, data=data, content_type="multipart/form-data", follow_redirects=True
    )


@pytest.fixture
def driver(client, ids):
    """driver1@test.com, signed in, with the 2024 Camry selected."""
    signup(client)
    choose_vehicle(client, ids.camry)
    return client


@pytest.fixture
def admin(new_client):
    c = new_client()
    login(c, ADMIN_EMAIL, ADMIN_PASSWORD)
    return c


def make_driver(new_client, email, vehicle_id):
    c = new_client()
    signup(c, email, DRIVER_PASSWORD)
    choose_vehicle(c, vehicle_id)
    return c


def latest_conversation_id(db, email=DRIVER_EMAIL):
    rows = db(
        "SELECT c.id FROM conversations c JOIN users u ON u.id = c.user_id "
        "WHERE u.email = ? ORDER BY c.id DESC LIMIT 1",
        (email,),
    )
    return rows[0]["id"] if rows else None
