from database.database import get_connection


def create_supplier_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        mobile TEXT,
        gst_number TEXT,
        address TEXT,
        email TEXT,
        outstanding REAL DEFAULT 0,
        status TEXT DEFAULT 'Active',
        created_date TEXT
    )
    """)

    conn.commit()
    conn.close()


def get_supplier_names():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT supplier_name
        FROM suppliers
        ORDER BY supplier_name
    """)

    rows = cursor.fetchall()

    conn.close()

    return [row[0] for row in rows]