from database.database import get_connection


def create_purchase_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT,
        purchase_date TEXT,
        supplier_name TEXT,
        product_name TEXT,
        quantity INTEGER,
        purchase_price REAL,
        gst REAL,
        total REAL
    )
    """)

    # Migrate legacy databases that still use the old
    # "supplier" / "product" column names.
    cursor.execute("PRAGMA table_info(purchases)")
    columns = [row[1] for row in cursor.fetchall()]

    if "supplier" in columns and "supplier_name" not in columns:
        cursor.execute(
            "ALTER TABLE purchases RENAME COLUMN supplier TO supplier_name"
        )

    if "product" in columns and "product_name" not in columns:
        cursor.execute(
            "ALTER TABLE purchases RENAME COLUMN product TO product_name"
        )

    # Add per-line discount % support (older databases won't have this
    # column yet - safe, additive migration, existing rows default to 0).
    cursor.execute("PRAGMA table_info(purchases)")
    columns = [row[1] for row in cursor.fetchall()]

    if "discount" not in columns:
        cursor.execute(
            "ALTER TABLE purchases ADD COLUMN discount REAL DEFAULT 0"
        )

    conn.commit()
    conn.close()


def save_purchase(
        invoice,
        date,
        supplier,
        product,
        qty,
        price,
        gst,
        total,
        discount=0):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO purchases(
        invoice_no,
        purchase_date,
        supplier_name,
        product_name,
        quantity,
        purchase_price,
        gst,
        total,
        discount
    )
    VALUES(?,?,?,?,?,?,?,?,?)
    """, (
        invoice,
        date,
        supplier,
        product,
        qty,
        price,
        gst,
        total,
        discount
    ))

    conn.commit()
    conn.close()


def get_all_purchases():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM purchases
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def delete_purchase(purchase_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM purchases WHERE id=?",
        (purchase_id,)
    )

    conn.commit()
    conn.close()


def search_purchase(keyword):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM purchases
    WHERE invoice_no LIKE ?
       OR supplier_name LIKE ?
       OR product_name LIKE ?
    ORDER BY id DESC
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows