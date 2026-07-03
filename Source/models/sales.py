from database.database import get_connection


def create_sales_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT,
        sale_date TEXT,
        customer TEXT,
        product TEXT,
        quantity INTEGER,
        selling_price REAL,
        gst REAL,
        discount REAL DEFAULT 0,
        total REAL,
        payment_mode TEXT,
        warranty_type TEXT DEFAULT 'Comprehensive',
        created_date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Older databases won't have this column yet - safe, additive
    # migration so existing installs get the Warranty Type field
    # without losing any existing sales history.
    cursor.execute("PRAGMA table_info(sales)")
    columns = [row[1] for row in cursor.fetchall()]
    if "warranty_type" not in columns:
        cursor.execute(
            "ALTER TABLE sales ADD COLUMN warranty_type TEXT DEFAULT 'Comprehensive'"
        )

    conn.commit()
    conn.close()


def save_sale(
        invoice,
        date,
        customer,
        product,
        qty,
        price,
        gst,
        discount,
        total,
        payment,
        warranty_type="Comprehensive"):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO sales(
        invoice_no,
        sale_date,
        customer,
        product,
        quantity,
        selling_price,
        gst,
        discount,
        total,
        payment_mode,
        warranty_type
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?)
    """,(
        invoice,
        date,
        customer,
        product,
        qty,
        price,
        gst,
        discount,
        total,
        payment,
        warranty_type
    ))

    conn.commit()
    conn.close()


def get_all_sales():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM sales
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def delete_sale(sale_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM sales WHERE id=?",
        (sale_id,)
    )

    conn.commit()

    conn.close()


def search_sale(keyword):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM sales
    WHERE invoice_no LIKE ?
       OR customer LIKE ?
       OR product LIKE ?
    """,(
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows