from database.database import get_connection
from models.product import (
    increase_stock,
    decrease_stock,
    get_product_names,
    get_product_details
)


def find_duplicate_product(brand, model, capacity, exclude_id=None):
    """
    Returns True if a product with the same brand + model + capacity
    (case-insensitive) already exists. Battery products are uniquely
    identified by that combination in this app (the same brand/model
    can legitimately come in different capacities).
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT id FROM products
        WHERE LOWER(TRIM(brand)) = ?
          AND LOWER(TRIM(model)) = ?
          AND LOWER(TRIM(COALESCE(capacity, ''))) = ?
    """
    params = [
        (brand or "").strip().lower(),
        (model or "").strip().lower(),
        (capacity or "").strip().lower(),
    ]

    if exclude_id:
        query += " AND id != ?"
        params.append(exclude_id)

    cursor.execute(query, params)
    found = cursor.fetchone() is not None

    conn.close()
    return found


def get_product_by_brand_model_capacity(brand, model, capacity):
    """Like find_duplicate_product, but returns the full row (or None)
    instead of just a bool - used by bulk import to merge into an
    existing product (add stock, refresh price) instead of skipping it."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE LOWER(TRIM(brand)) = ?
          AND LOWER(TRIM(model)) = ?
          AND LOWER(TRIM(COALESCE(capacity, ''))) = ?
    """, (
        (brand or "").strip().lower(),
        (model or "").strip().lower(),
        (capacity or "").strip().lower(),
    ))

    row = cursor.fetchone()
    conn.close()
    return row


def add_product(
    brand,
    model,
    capacity,
    purchase_price,
    selling_price,
    warranty,
    stock,
    min_stock,
    rack_location,
    barcode=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products(
            brand,
            model,
            capacity,
            purchase_price,
            selling_price,
            warranty,
            stock,
            min_stock,
            rack_location,
            barcode,
            created_date
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,datetime('now'))
    """, (
        brand,
        model,
        capacity,
        purchase_price,
        selling_price,
        warranty,
        stock,
        min_stock,
        rack_location,
        (barcode or "").strip() or None
    ))

    new_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return new_id


def find_duplicate_barcode(barcode, exclude_id=None):
    """Returns True if another product already uses this barcode."""
    barcode = (barcode or "").strip()
    if not barcode:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id FROM products WHERE barcode = ?"
    params = [barcode]

    if exclude_id:
        query += " AND id != ?"
        params.append(exclude_id)

    cursor.execute(query, params)
    found = cursor.fetchone() is not None

    conn.close()
    return found


def find_product_by_barcode(barcode):
    """Returns the full product row for a scanned barcode, or None."""
    barcode = (barcode or "").strip()
    if not barcode:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
    row = cursor.fetchone()

    conn.close()
    return row


def set_product_barcode(product_id, barcode):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE products SET barcode = ? WHERE id = ?",
        ((barcode or "").strip() or None, product_id)
    )

    conn.commit()
    conn.close()


def get_product_by_id(product_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM products
        WHERE id=?
    """, (product_id,))

    row = cursor.fetchone()

    conn.close()

    return row


def get_all_products():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            brand,
            model,
            capacity,
            stock,
            selling_price,
            barcode
        FROM products
        ORDER BY brand, model
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def update_product(
    product_id,
    brand,
    model,
    capacity,
    purchase_price,
    selling_price,
    warranty,
    stock,
    min_stock,
    rack_location,
    barcode=None
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products SET
            brand=?,
            model=?,
            capacity=?,
            purchase_price=?,
            selling_price=?,
            warranty=?,
            stock=?,
            min_stock=?,
            rack_location=?,
            barcode=?
        WHERE id=?
    """, (
        brand,
        model,
        capacity,
        purchase_price,
        selling_price,
        warranty,
        stock,
        min_stock,
        rack_location,
        (barcode or "").strip() or None,
        product_id
    ))

    conn.commit()
    conn.close()


def delete_product(product_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id=?",
        (product_id,)
    )

    conn.commit()
    conn.close()


def search_products(keyword):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            brand,
            model,
            capacity,
            stock,
            selling_price,
            barcode
        FROM products
        WHERE
            brand LIKE ?
            OR model LIKE ?
            OR capacity LIKE ?
            OR barcode LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows

def bulk_import_products(rows):
    """
    Applies a list of parsed product dicts (brand/model/capacity/
    purchase_price/selling_price/warranty/stock/rack_location) to the
    database in one go:
      - An existing product with the same brand+model+capacity gets
        MERGED (its stock increases by the imported quantity, and its
        price/warranty/rack fields are refreshed with any non-blank
        imported values) instead of being duplicated.
      - Everything else becomes a new product.

    Returns a summary dict: {"added": n, "merged": n, "skipped": [...]}
    so the calling page can show the user exactly what happened -
    nothing here raises for a single bad row, it just records why that
    row was skipped and keeps going (a bulk import of a few thousand
    rows shouldn't abort because row #612 had a typo).
    """
    added = 0
    merged = 0
    skipped = []

    def _num(value, cast=float, default=0):
        try:
            return cast(value)
        except (TypeError, ValueError):
            return default

    for row in rows:
        brand = (row.get("brand") or "").strip()
        model = (row.get("model") or "").strip()
        capacity = (row.get("capacity") or "").strip()

        if not brand or not model:
            skipped.append(f"{brand or '?'} {model or '?'} - missing Brand or Model")
            continue

        purchase_price = _num(row.get("purchase_price"))
        selling_price = _num(row.get("selling_price"))
        warranty = _num(row.get("warranty"), cast=int)
        stock = _num(row.get("stock"), cast=int, default=0)
        min_stock = _num(row.get("min_stock"), cast=int, default=0)
        rack_location = (row.get("rack_location") or "").strip()
        barcode = (row.get("barcode") or "").strip() or None

        existing = get_product_by_brand_model_capacity(brand, model, capacity)

        try:
            if existing:
                update_product(
                    existing["id"],
                    brand,
                    model,
                    capacity,
                    purchase_price or existing["purchase_price"],
                    selling_price or existing["selling_price"],
                    warranty or existing["warranty"],
                    (existing["stock"] or 0) + stock,
                    min_stock or existing["min_stock"],
                    rack_location or existing["rack_location"],
                    existing["barcode"]
                )
                merged += 1
            else:
                add_product(
                    brand, model, capacity, purchase_price, selling_price,
                    warranty, stock, min_stock, rack_location, barcode
                )
                added += 1
        except Exception as exc:
            skipped.append(f"{brand} {model} - {exc}")

    return {"added": added, "merged": merged, "skipped": skipped}
