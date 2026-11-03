"""Creates the tables, the admin account, and the demo vehicles: python seed.py

Safe to run more than once. With TESTING=1 the Camry manual is the 3-page
fixture PDF and the fake provider embeds it. Otherwise the real manual must be at
REAL_CAMRY_MANUAL, and embedding it uses your GEMINI_API_KEY.
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from werkzeug.security import generate_password_hash

import ai
import models

ROOT = Path(__file__).resolve().parent
ADMIN_EMAIL = "admin@mycarai.test"
ADMIN_PASSWORD = "admin12345"
CAMRY = ("Toyota", "Camry", 2024, "XSE")
RAV4 = ("Toyota", "RAV4", 2024, "XLE")  # deliberately has no manual
SAMPLE_MANUAL = ROOT / "tests" / "fixtures" / "sample_manual.pdf"
REAL_CAMRY_MANUAL = ROOT / "knowledge" / "manuals" / "2024_Toyota_Camry_XSE.pdf"


def _vehicle_id(conn, vehicle):
    existing = models.find_vehicle(conn, *vehicle)
    return existing["id"] if existing else models.add_vehicle(conn, *vehicle)


def seed(db_path):
    conn = models.connect(db_path)
    try:
        models.init_db(conn)
        if models.get_user_by_email(conn, ADMIN_EMAIL) is None:
            models.create_user(conn, ADMIN_EMAIL, generate_password_hash(ADMIN_PASSWORD), role="admin")
        admin_id = models.get_user_by_email(conn, ADMIN_EMAIL)["id"]

        camry_id = _vehicle_id(conn, CAMRY)
        _vehicle_id(conn, RAV4)

        if models.vehicle_has_manual(conn, camry_id):
            return
        manual = SAMPLE_MANUAL if ai.TESTING else REAL_CAMRY_MANUAL
        if not manual.exists():
            print(f"No Camry manual at {manual}. Add it there and run seed.py again,")
            print("or sign in as the admin and upload it on /admin/manuals.")
            return
        pages = ai.read_pdf_pages(manual.read_bytes())
        try:
            chunks = ai.embed_manual(pages)
        except ai.ProviderError as exc:
            print(f"Could not process the Camry manual ({exc}). Try seed.py again later.")
            return
        models.save_manual(conn, camry_id, admin_id, len(pages), chunks)
        print(f"Loaded the Camry manual: {len(pages)} pages, {len(chunks)} with text.")
    finally:
        conn.close()


if __name__ == "__main__":
    from app import app

    seed(app.config["DATABASE"])
    print(f"Seeded {app.config['DATABASE']}")
