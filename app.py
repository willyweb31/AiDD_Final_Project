"""MyCarAI routes. SQL lives in models.py, input rules in validators.py, and AI
calls in ai.py; this file only connects them to pages."""

import os
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import ai
import models
import validators

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
# The single database setting. Test runs get their own file so fake embeddings
# never end up next to real ones.
app.config["DATABASE"] = str(BASE_DIR / ("mycarai-test.db" if ai.TESTING else "mycarai.db"))
app.config["MAX_CONTENT_LENGTH"] = validators.MAX_PDF_BYTES
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("Set FLASK_SECRET_KEY in your .env file.")

UNAVAILABLE = "The assistant is unavailable right now. Please try again."
MANUAL_FAILED = "The manual could not be processed. Try again."
CONVERSATION_NOT_FOUND = "Conversation not found."


# --------------------------------------------------------------- plumbing ---


def get_db():
    if "db" not in g:
        g.db = models.connect(app.config["DATABASE"])
    return g.db


@app.teardown_appcontext
def close_db(_error):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


@app.before_request
def load_user():
    g.user = None
    user_id = session.get("user_id")
    if user_id is not None:
        g.user = models.get_user(get_db(), user_id)
        if g.user is None:
            session.clear()


@app.template_filter("vehicle_name")
def vehicle_name(row):
    return f"{row['year']} {row['make']} {row['model']} {row['trim']}"


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def driver_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        if g.user["role"] != "driver":
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        if g.user["role"] != "admin":
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def home_for(user):
    if user is None:
        return url_for("login")
    if user["role"] == "admin":
        return url_for("admin_manuals")
    return url_for("chat") if user["vehicle_id"] else url_for("vehicle")


def conversation_not_found():
    return render_template("error.html", message=CONVERSATION_NOT_FOUND), 404


def answer(question, vehicle):
    """Raises ai.ProviderError when the assistant can't be reached."""
    chunks = models.chunks_for_vehicle(get_db(), vehicle["id"])
    return ai.answer_question(question, chunks, vehicle_name(vehicle))


# ----------------------------------------------------------------- errors ---


@app.errorhandler(403)
def forbidden(_error):
    return render_template("error.html", message="You don't have access to this page."), 403


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", message="Page not found."), 404


@app.errorhandler(413)
def too_large(_error):
    # Flask refuses an oversized upload before the route runs.
    if g.get("user") is not None and g.user["role"] == "admin":
        return admin_page(upload_error=validators.PDF_TOO_LARGE), 413
    return render_template("error.html", message=validators.PDF_TOO_LARGE), 413


@app.errorhandler(500)
def server_error(_error):
    return render_template("error.html", message="Something went wrong. Please try again."), 500


# --------------------------------------------------------------- accounts ---


@app.route("/")
def index():
    return redirect(home_for(g.user))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if g.user is not None:
        return redirect(home_for(g.user))
    if request.method == "GET":
        return render_template("signup.html")

    # Any "role" field in the form is ignored: every signup is a driver.
    password = request.form.get("password", "")
    email, error = validators.validate_signup(get_db(), request.form.get("email"), password)
    if error is None:
        user_id = models.create_user(get_db(), email, generate_password_hash(password))
        if user_id is None:
            error = "An account with this email already exists."
    if error:
        return render_template("signup.html", error=error, email=request.form.get("email", "")), 400

    session.clear()
    session["user_id"] = user_id
    return redirect(url_for("vehicle"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None:
        return redirect(home_for(g.user))
    if request.method == "GET":
        return render_template("login.html")

    email = validators.clean_email(request.form.get("email"))
    user = models.get_user_by_email(get_db(), email)
    if user is None or not check_password_hash(user["password_hash"], request.form.get("password", "")):
        return render_template("login.html", error="Email or password is incorrect.", email=email), 400

    session.clear()
    session["user_id"] = user["id"]
    return redirect(home_for(user))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You are signed out.")
    return redirect(url_for("login"))


# ---------------------------------------------------------------- vehicle ---


@app.route("/vehicle", methods=["GET", "POST"])
@driver_required
def vehicle():
    conn = get_db()
    error = None
    if request.method == "POST":
        vehicle_id, error = validators.validate_vehicle_choice(conn, request.form.get("vehicle_id"))
        if error is None:
            models.set_user_vehicle(conn, g.user["id"], vehicle_id)
            return redirect(url_for("chat"))

    page = render_template(
        "vehicle.html",
        vehicles=models.vehicles_with_manual(conn),
        selected=g.user["vehicle_id"],
        error=error,
    )
    return (page, 400) if error else page


# ------------------------------------------------------------------- chat ---


def chat_page(vehicle, conversation=None, messages=(), error=None, question="", status=200):
    page = render_template(
        "chat.html",
        vehicle=vehicle,
        conversation=conversation,
        messages=messages,
        error=error,
        question=question,
    )
    return page, status


@app.route("/chat", methods=["GET", "POST"])
@driver_required
def chat():
    conn = get_db()
    vehicle = models.get_vehicle(conn, g.user["vehicle_id"]) if g.user["vehicle_id"] else None
    if vehicle is None:
        flash("Choose your vehicle first.")
        return redirect(url_for("vehicle"))
    if request.method == "GET":
        return chat_page(vehicle)

    raw = request.form.get("question", "")
    question, error = validators.validate_question(raw)
    if error:
        return chat_page(vehicle, error=error, question=raw, status=400)
    try:
        reply, chunk_ids = answer(question, vehicle)
    except ai.ProviderError as exc:
        app.logger.warning("Assistant unavailable: %s", exc)
        return chat_page(vehicle, error=UNAVAILABLE, question=raw, status=503)

    conversation_id = models.create_conversation(
        conn, g.user["id"], vehicle["id"], question[:60], question, reply, chunk_ids
    )
    return redirect(url_for("conversation", conversation_id=conversation_id))


# ---------------------------------------------------------- conversations ---


@app.route("/conversations")
@driver_required
def conversations():
    return render_template(
        "conversations.html", conversations=models.list_conversations(get_db(), g.user["id"])
    )


@app.route("/conversations/<int:conversation_id>", methods=["GET", "POST"])
@login_required
def conversation(conversation_id):
    # Admins get the same 404 as a missing conversation, never "see everything".
    if g.user["role"] != "driver":
        return conversation_not_found()
    conn = get_db()
    convo = models.get_conversation(conn, conversation_id, g.user["id"])
    if convo is None:
        return conversation_not_found()
    # Answers come from the conversation's vehicle, not the driver's current one.
    convo_vehicle = {"id": convo["vehicle_id"], **{k: convo[k] for k in ("make", "model", "year", "trim")}}

    error, raw, status = None, "", 200
    if request.method == "POST":
        raw = request.form.get("question", "")
        question, error = validators.validate_question(raw)
        status = 400
        if error is None:
            try:
                reply, chunk_ids = answer(question, convo_vehicle)
            except ai.ProviderError as exc:
                app.logger.warning("Assistant unavailable: %s", exc)
                error, status = UNAVAILABLE, 503
            else:
                if not models.add_follow_up(conn, conversation_id, g.user["id"], question, reply, chunk_ids):
                    return conversation_not_found()
                return redirect(url_for("conversation", conversation_id=conversation_id))

    messages = models.get_messages(conn, conversation_id, g.user["id"])
    return chat_page(convo_vehicle, convo, messages, error, raw, status)


@app.route("/conversations/<int:conversation_id>/delete", methods=["POST"])
@login_required
def delete_conversation(conversation_id):
    if g.user["role"] != "driver":
        return conversation_not_found()
    if not models.delete_conversation(get_db(), conversation_id, g.user["id"]):
        return conversation_not_found()
    flash("Conversation deleted.")
    return redirect(url_for("conversations"))


# ------------------------------------------------------------------ admin ---


def admin_page(vehicle_error=None, upload_error=None, form=None):
    conn = get_db()
    return render_template(
        "admin_manuals.html",
        manuals=models.list_manuals(conn),
        vehicles_needing_manual=models.vehicles_without_manual(conn),
        vehicle_error=vehicle_error,
        upload_error=upload_error,
        form=form or {},
    )


@app.route("/admin/manuals", methods=["GET", "POST"])
@admin_required
def admin_manuals():
    if request.method == "GET":
        return admin_page()

    action = request.form.get("action")
    if action == "add_vehicle":
        return add_vehicle()
    if action == "upload_manual":
        return upload_manual()
    abort(400)


def add_vehicle():
    conn = get_db()
    form = request.form
    fields, error = validators.validate_new_vehicle(
        conn, form.get("make"), form.get("model"), form.get("year"), form.get("trim")
    )
    if error is None and models.add_vehicle(conn, **fields) is None:
        error = "This vehicle already exists."
    if error:
        return admin_page(vehicle_error=error, form=form), 400
    flash(f"Added {vehicle_name(fields)}. Upload its manual below.")
    return redirect(url_for("admin_manuals"))


def upload_manual():
    conn = get_db()
    vehicle_id, error = validators.validate_upload_vehicle(conn, request.form.get("vehicle_id"))
    if error is None:
        pages, error = validators.validate_pdf(request.files.get("manual"))
    if error:
        return admin_page(upload_error=error), 400

    try:
        chunks = ai.embed_manual(pages)
    except ai.ProviderError as exc:
        app.logger.warning("Manual upload failed: %s", exc)
        return admin_page(upload_error=MANUAL_FAILED), 503
    if not chunks:
        return admin_page(upload_error=MANUAL_FAILED), 400

    if models.save_manual(conn, vehicle_id, g.user["id"], len(pages), chunks) is None:
        return admin_page(upload_error="This vehicle already has a manual."), 400
    flash(f"{vehicle_name(models.get_vehicle(conn, vehicle_id))} Owner's Manual is ready.")
    return redirect(url_for("admin_manuals"))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
