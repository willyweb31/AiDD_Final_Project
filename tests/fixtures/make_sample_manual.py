"""Builds tests/fixtures/sample_manual.pdf: the 3-page fixture manual from the spec.

Uses only the standard library so it runs anywhere. Run it once and commit the PDF:
    python tests/fixtures/make_sample_manual.py
"""

from pathlib import Path

PAGES = [
    "Welcome to your vehicle. Read this guide before driving. Store this booklet inside the glove compartment.",
    "Lane keep assist keeps the car in its lane. To turn off lane keep assist, press the lane assist button.",
    "Check tire pressure monthly. Inflate tires to the pressure shown on the label inside the door jamb.",
]


def build_pdf(pages):
    objects = []  # each entry is the body of object number index + 1

    def add(body):
        objects.append(body)
        return len(objects)

    font_id = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    pages_id = add(b"")  # filled in once the page ids are known
    page_ids = []
    for text in pages:
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT /F1 10 Tf 40 740 Td ({escaped}) Tj ET".encode("latin-1")
        content_id = add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        page_ids.append(
            add(
                b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 612 792] "
                b"/Resources << /Font << /F1 %d 0 R >> >> /Contents %d 0 R >>"
                % (pages_id, font_id, content_id)
            )
        )
    kids = b" ".join(b"%d 0 R" % pid for pid in page_ids)
    objects[pages_id - 1] = b"<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, len(page_ids))
    catalog_id = add(b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id)

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref_at = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        catalog_id,
        xref_at,
    )
    return bytes(out)


if __name__ == "__main__":
    target = Path(__file__).with_name("sample_manual.pdf")
    target.write_bytes(build_pdf(PAGES))
    print(f"wrote {target}")
