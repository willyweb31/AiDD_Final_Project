"""Every SQL statement in MyCarAI. Always ? placeholders, never string building.

Every query on a conversation or its messages filters by the conversation id AND
the signed-in user's id, so someone else's conversation looks the same as a
missing one.
"""

import json
import sqlite3
from datetime import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY,
    make TEXT NOT NULL COLLATE NOCASE,
    model TEXT NOT NULL COLLATE NOCASE,
    year INTEGER NOT NULL,
    trim TEXT NOT NULL COLLATE NOCASE,
    UNIQUE (make, model, year, trim)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'driver' CHECK (role IN ('driver', 'admin')),
    vehicle_id INTEGER REFERENCES vehicles (id)
);

CREATE TABLE IF NOT EXISTS manuals (
    id INTEGER PRIMARY KEY,
    vehicle_id INTEGER NOT NULL UNIQUE REFERENCES vehicles (id),
    page_count INTEGER NOT NULL,
    uploaded_by INTEGER NOT NULL REFERENCES users (id),
    uploaded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY,
    manual_id INTEGER NOT NULL REFERENCES manuals (id),
    page_number INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (id),
    vehicle_id INTEGER NOT NULL REFERENCES vehicles (id),
    title TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations (id),
    sender TEXT NOT NULL CHECK (sender IN ('driver', 'assistant')),
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS citations (
    message_id INTEGER NOT NULL REFERENCES messages (id),
    chunk_id INTEGER NOT NULL REFERENCES chunks (id),
    PRIMARY KEY (message_id, chunk_id)
);
"""


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn):
    conn.executescript(SCHEMA)


def _now():
    return datetime.now().isoformat(sep=" ", timespec="seconds")


# ------------------------------------------------------------------- users ---


def create_user(conn, email, password_hash, role="driver"):
    """Returns the new user's id, or None if the email is already taken."""
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                (email, password_hash, role),
            )
    except sqlite3.IntegrityError:
        return None
    return cur.lastrowid


def get_user(conn, user_id):
    return conn.execute(
        "SELECT id, email, role, vehicle_id FROM users WHERE id = ?", (user_id,)
    ).fetchone()


def get_user_by_email(conn, email):
    return conn.execute(
        "SELECT id, email, password_hash, role, vehicle_id FROM users WHERE email = ?",
        (email,),
    ).fetchone()


def set_user_vehicle(conn, user_id, vehicle_id):
    with conn:
        conn.execute("UPDATE users SET vehicle_id = ? WHERE id = ?", (vehicle_id, user_id))


# ---------------------------------------------------------------- vehicles ---


def get_vehicle(conn, vehicle_id):
    return conn.execute(
        "SELECT id, make, model, year, trim FROM vehicles WHERE id = ?", (vehicle_id,)
    ).fetchone()


def find_vehicle(conn, make, model, year, trim):
    return conn.execute(
        "SELECT id, make, model, year, trim FROM vehicles"
        " WHERE make = ? AND model = ? AND year = ? AND trim = ?",
        (make, model, year, trim),
    ).fetchone()


def add_vehicle(conn, make, model, year, trim):
    """Returns the new vehicle's id, or None if it already exists."""
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO vehicles (make, model, year, trim) VALUES (?, ?, ?, ?)",
                (make, model, year, trim),
            )
    except sqlite3.IntegrityError:
        return None
    return cur.lastrowid


def vehicles_with_manual(conn):
    return conn.execute(
        "SELECT v.id, v.make, v.model, v.year, v.trim FROM vehicles v"
        " JOIN manuals m ON m.vehicle_id = v.id"
        " ORDER BY v.year DESC, v.make, v.model, v.trim"
    ).fetchall()


def vehicles_without_manual(conn):
    return conn.execute(
        "SELECT v.id, v.make, v.model, v.year, v.trim FROM vehicles v"
        " LEFT JOIN manuals m ON m.vehicle_id = v.id WHERE m.id IS NULL"
        " ORDER BY v.year DESC, v.make, v.model, v.trim"
    ).fetchall()


def vehicle_has_manual(conn, vehicle_id):
    row = conn.execute("SELECT 1 FROM manuals WHERE vehicle_id = ?", (vehicle_id,)).fetchone()
    return row is not None


# ----------------------------------------------------------------- manuals ---


def save_manual(conn, vehicle_id, uploaded_by, page_count, chunks):
    """Saves a manual and its chunks in one transaction.

    chunks is a list of (page_number, text, embedding). Returns the manual id, or
    None if the vehicle already has a manual; either way nothing is half-saved.
    """
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO manuals (vehicle_id, page_count, uploaded_by, uploaded_at)"
                " VALUES (?, ?, ?, ?)",
                (vehicle_id, page_count, uploaded_by, _now()),
            )
            manual_id = cur.lastrowid
            conn.executemany(
                "INSERT INTO chunks (manual_id, page_number, text, embedding) VALUES (?, ?, ?, ?)",
                [(manual_id, page, text, json.dumps(emb)) for page, text, emb in chunks],
            )
    except sqlite3.IntegrityError:
        return None
    return manual_id


def list_manuals(conn):
    return conn.execute(
        "SELECT m.id, m.page_count, m.uploaded_at, u.email AS uploader,"
        " v.make, v.model, v.year, v.trim"
        " FROM manuals m"
        " JOIN vehicles v ON v.id = m.vehicle_id"
        " JOIN users u ON u.id = m.uploaded_by"
        " ORDER BY m.uploaded_at DESC, m.id DESC"
    ).fetchall()


def chunks_for_vehicle(conn, vehicle_id):
    rows = conn.execute(
        "SELECT ch.id, ch.page_number, ch.text, ch.embedding FROM chunks ch"
        " JOIN manuals m ON m.id = ch.manual_id WHERE m.vehicle_id = ?",
        (vehicle_id,),
    ).fetchall()
    return [
        {"id": r["id"], "page_number": r["page_number"], "text": r["text"],
         "embedding": json.loads(r["embedding"])}
        for r in rows
    ]


# ----------------------------------------------------------- conversations ---


def _insert_exchange(conn, conversation_id, question, answer, chunk_ids):
    conn.execute(
        "INSERT INTO messages (conversation_id, sender, content) VALUES (?, 'driver', ?)",
        (conversation_id, question),
    )
    cur = conn.execute(
        "INSERT INTO messages (conversation_id, sender, content) VALUES (?, 'assistant', ?)",
        (conversation_id, answer),
    )
    # chunk_ids arrive most similar first. Citations are read back in rowid
    # order, so the first one is the chunk named in the Source line.
    conn.executemany(
        "INSERT INTO citations (message_id, chunk_id) VALUES (?, ?)",
        [(cur.lastrowid, chunk_id) for chunk_id in chunk_ids],
    )


def create_conversation(conn, user_id, vehicle_id, title, question, answer, chunk_ids):
    """Saves a new conversation with its first question and answer. Returns its id."""
    with conn:
        cur = conn.execute(
            "INSERT INTO conversations (user_id, vehicle_id, title, created_at) VALUES (?, ?, ?, ?)",
            (user_id, vehicle_id, title, _now()),
        )
        _insert_exchange(conn, cur.lastrowid, question, answer, chunk_ids)
    return cur.lastrowid


def add_follow_up(conn, conversation_id, user_id, question, answer, chunk_ids):
    """Adds a question and answer to the user's own conversation. False if not theirs."""
    with conn:
        owned = conn.execute(
            "SELECT 1 FROM conversations WHERE id = ? AND user_id = ?", (conversation_id, user_id)
        ).fetchone()
        if owned is None:
            return False
        _insert_exchange(conn, conversation_id, question, answer, chunk_ids)
    return True


def get_conversation(conn, conversation_id, user_id):
    return conn.execute(
        "SELECT c.id, c.title, c.created_at, c.vehicle_id, v.make, v.model, v.year, v.trim"
        " FROM conversations c JOIN vehicles v ON v.id = c.vehicle_id"
        " WHERE c.id = ? AND c.user_id = ?",
        (conversation_id, user_id),
    ).fetchone()


def list_conversations(conn, user_id):
    return conn.execute(
        "SELECT c.id, c.title, c.created_at, v.make, v.model, v.year, v.trim"
        " FROM conversations c JOIN vehicles v ON v.id = c.vehicle_id"
        " WHERE c.user_id = ? ORDER BY c.created_at DESC, c.id DESC",
        (user_id,),
    ).fetchall()


def get_messages(conn, conversation_id, user_id):
    """Messages in the order asked. source_page is the PDF page of the most similar
    cited chunk, or None when the answer did not come from the manual."""
    return conn.execute(
        "SELECT m.id, m.sender, m.content,"
        " (SELECT ch.page_number FROM citations ci JOIN chunks ch ON ch.id = ci.chunk_id"
        "  WHERE ci.message_id = m.id ORDER BY ci.rowid LIMIT 1) AS source_page"
        " FROM messages m JOIN conversations c ON c.id = m.conversation_id"
        " WHERE c.id = ? AND c.user_id = ? ORDER BY m.id",
        (conversation_id, user_id),
    ).fetchall()


def delete_conversation(conn, conversation_id, user_id):
    """Deletes the user's own conversation, its messages and citations. False if not theirs."""
    with conn:
        conn.execute(
            "DELETE FROM citations WHERE message_id IN ("
            " SELECT m.id FROM messages m JOIN conversations c ON c.id = m.conversation_id"
            " WHERE c.id = ? AND c.user_id = ?)",
            (conversation_id, user_id),
        )
        conn.execute(
            "DELETE FROM messages WHERE conversation_id IN ("
            " SELECT id FROM conversations WHERE id = ? AND user_id = ?)",
            (conversation_id, user_id),
        )
        cur = conn.execute(
            "DELETE FROM conversations WHERE id = ? AND user_id = ?", (conversation_id, user_id)
        )
    return cur.rowcount > 0
