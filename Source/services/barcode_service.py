"""
Barcode / QR code service.

Responsibilities:
  - Generate a valid, unique EAN-13 barcode value for a product that
    doesn't have one yet.
  - Validate manually-typed barcodes (EAN-13 / EAN-8 / UPC-A / UPC-E /
    Code128 / Code39 all pass through as free text - only EAN/UPC have a
    checksum we can actually verify).
  - Look up a product from a scanned code (used by both the Sales page
    scanner and the Product page "Scan" button).
  - Render a barcode image and/or QR code image, and lay both out on a
    small printable label (PDF) alongside the product name and price.

Image generation uses the optional `python-barcode` and `qrcode`
libraries. Both are pure add-ons: if they aren't installed, label/image
generation degrades to a clear text-only placeholder instead of raising,
because the barcode *value* stored on the product (used for scanning and
lookup) never depends on being able to render a picture of it.
"""

import io
import os

from services.product_service import find_product_by_barcode, find_duplicate_barcode


# ---------------------------------------------------------------------------
# Value generation / validation
# ---------------------------------------------------------------------------

# Store-specific EAN-13 prefix. "20"-"29" is the GS1 "restricted
# circulation" range reserved for in-store use (weighed/priced items,
# internal SKUs, etc.) and will never collide with a real manufacturer's
# published barcode.
_INTERNAL_PREFIX = "20"


def _ean13_check_digit(digits12):
    """Standard EAN-13 checksum for the first 12 digits."""
    total = 0
    for i, ch in enumerate(digits12):
        n = int(ch)
        total += n * (3 if i % 2 == 1 else 1)
    return str((10 - (total % 10)) % 10)


def generate_barcode_value(product_id):
    """
    Deterministically builds a valid, unique EAN-13 from a product's
    database id, e.g. product #42 -> "2000000000042" + check digit.
    Guaranteed unique as long as product ids are unique (they are, being
    the primary key), so no collision check is needed.
    """
    body = f"{_INTERNAL_PREFIX}{int(product_id):010d}"[:12]
    return body + _ean13_check_digit(body)


def generate_unique_random_barcode():
    """
    For the "Auto-Generate" button on the Product form, used *before* a
    product has been saved (and therefore has no id yet to derive a
    value from, unlike generate_barcode_value). Picks a random 10-digit
    body in the internal-use range and checks it against the database,
    retrying on the astronomically unlikely chance of a collision.
    """
    import random

    for _ in range(20):
        body = f"{_INTERNAL_PREFIX}{random.randint(0, 9_999_999_999):010d}"[:12]
        code = body + _ean13_check_digit(body)
        if not barcode_in_use(code):
            return code
    # Practically unreachable, but never leave the caller with nothing.
    raise RuntimeError("Could not generate a unique barcode, please try again.")


def is_valid_ean_upc(code):
    """True if `code` is an 8, 12 or 13 digit string with a correct
    check digit (EAN-8 / UPC-A / EAN-13). Non-numeric or other-length
    codes (Code128, Code39, QR payloads, free-text SKUs) simply aren't
    EAN/UPC, so this returns False for them rather than raising - the
    caller should treat those as "valid but unverifiable"."""
    code = (code or "").strip()
    if not code.isdigit() or len(code) not in (8, 12, 13):
        return False
    body, check = code[:-1], code[-1]
    if len(body) == 12:
        return _ean13_check_digit(body) == check
    if len(body) == 7:
        # EAN-8 uses the same weighting scheme, just shorter.
        total = sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(body))
        return str((10 - (total % 10)) % 10) == check
    # UPC-A is numerically an EAN-13 with a leading 0.
    if len(body) == 11:
        return _ean13_check_digit("0" + body) == check
    return False


def lookup_product_by_code(code):
    """Look up a product for a scanned/typed code. Returns the sqlite3.Row
    or None. Trims whitespace defensively (scanners sometimes emit a
    trailing newline that lands in the Entry as-is)."""
    code = (code or "").strip()
    if not code:
        return None
    return find_product_by_barcode(code)


def barcode_in_use(code, exclude_id=None):
    return find_duplicate_barcode(code, exclude_id=exclude_id)


# ---------------------------------------------------------------------------
# Image generation (optional dependencies)
# ---------------------------------------------------------------------------

def generate_barcode_image(code, symbology="code128"):
    """
    Returns PNG bytes for `code`, or None if the python-barcode library
    isn't installed. `symbology` is "code128" (default, handles any
    text/number) or "ean13" (only valid for a 12/13-digit EAN payload).
    """
    try:
        import barcode as _barcode_lib
        from barcode.writer import ImageWriter
    except ImportError:
        return None

    try:
        writer_class = _barcode_lib.get_barcode_class(
            "ean13" if symbology == "ean13" else "code128"
        )
        # python-barcode wants the 12-digit EAN body (it computes/appends
        # the check digit itself).
        payload = code[:-1] if symbology == "ean13" and len(code) == 13 else code
        instance = writer_class(payload, writer=ImageWriter())

        buffer = io.BytesIO()
        instance.write(buffer, options={"write_text": True, "quiet_zone": 2})
        return buffer.getvalue()
    except Exception:
        # Malformed payload for the chosen symbology, missing font, etc.
        # Image generation is a nice-to-have, never let it crash the caller.
        return None


def generate_qr_image(data):
    """Returns PNG bytes for a QR code encoding `data`, or None if the
    `qrcode` library isn't installed."""
    try:
        import qrcode
    except ImportError:
        return None

    try:
        img = qrcode.make(data)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    except Exception:
        return None


def generate_label_pdf(output_path, product_name, code, price=None, company_name=None):
    """
    Builds a small printable shelf/product label (75mm x 45mm, a common
    thermal/adhesive label size) containing the product name, price,
    a barcode image (falls back to plain text if python-barcode isn't
    installed) and a QR code carrying the barcode value for phone-camera
    lookups. Uses reportlab, which is already a project dependency.
    """
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas as pdf_canvas

    width, height = 75 * mm, 45 * mm
    c = pdf_canvas.Canvas(output_path, pagesize=(width, height))

    y = height - 8 * mm
    if company_name:
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(width / 2, y, company_name)
        y -= 5 * mm

    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(width / 2, y, (product_name or "")[:40])
    y -= 6 * mm

    if price is not None:
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, y, f"MRP: Rs. {float(price):,.2f}")
        y -= 5 * mm

    barcode_png = generate_barcode_image(code, symbology="code128")
    qr_png = generate_qr_image(code)

    if barcode_png:
        img = ImageReader(io.BytesIO(barcode_png))
        img_w = 55 * mm
        img_h = 14 * mm
        c.drawImage(
            img, (width - img_w) / 2, y - img_h,
            width=img_w, height=img_h, preserveAspectRatio=True, mask="auto"
        )
        y -= (img_h + 3 * mm)
    else:
        # No barcode library available - still make the label usable by
        # printing the raw code large enough to key in manually.
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, y - 5 * mm, code)
        y -= 8 * mm

    if qr_png:
        img = ImageReader(io.BytesIO(qr_png))
        qr_size = 14 * mm
        c.drawImage(
            img, (width - qr_size) / 2, max(y - qr_size, 2 * mm),
            width=qr_size, height=qr_size, preserveAspectRatio=True, mask="auto"
        )

    c.setFont("Helvetica", 6)
    c.drawCentredString(width / 2, 2 * mm, code)

    c.save()
    return output_path
