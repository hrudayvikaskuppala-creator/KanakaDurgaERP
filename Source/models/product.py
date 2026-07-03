from database.database import get_connection


def create_product_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        capacity TEXT,
        purchase_price REAL,
        selling_price REAL,
        warranty INTEGER,
        stock INTEGER DEFAULT 0,
        min_stock INTEGER DEFAULT 0,
        rack_location TEXT,
        status TEXT DEFAULT 'Active',
        barcode TEXT,
        created_date TEXT
    )
    """)

    conn.commit()

    # Migration: add the barcode column to databases created before this
    # feature existed. SQLite has no "ADD COLUMN IF NOT EXISTS", so probe
    # the schema first and only alter it if the column is missing.
    cursor.execute("PRAGMA table_info(products)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if "barcode" not in existing_columns:
        cursor.execute("ALTER TABLE products ADD COLUMN barcode TEXT")
        conn.commit()

    # Unique index (ignoring NULL/blank) so two products can never share
    # the same scanned barcode, without forcing every legacy row to have one.
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_products_barcode
        ON products(barcode)
        WHERE barcode IS NOT NULL AND barcode != ''
    """)
    conn.commit()

    conn.close()


def get_product_by_barcode(code):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE barcode = ?",
        (code,)
    )

    row = cursor.fetchone()
    conn.close()
    return row


def increase_stock(product_name, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET stock = stock + ?
        WHERE brand || ' ' || model = ?
    """, (quantity, product_name))

    conn.commit()
    conn.close()


def decrease_stock(product_name, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET stock = stock - ?
        WHERE brand || ' ' || model = ?
    """, (quantity, product_name))

    conn.commit()
    conn.close()


def get_product_names():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT brand || ' ' || model AS product_name
        FROM products
        ORDER BY brand, model
    """)

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]


def get_product_details(product_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM products
        WHERE brand || ' ' || model = ?
    """, (product_name,))

    row = cursor.fetchone()

    conn.close()

    return row