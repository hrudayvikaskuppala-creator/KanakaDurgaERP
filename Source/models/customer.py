from database.database import get_connection


def create_customer_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        mobile TEXT,
        whatsapp TEXT,
        gst_number TEXT,
        address TEXT,
        vehicle_number TEXT,
        vehicle_model TEXT,
        email TEXT,
        outstanding REAL DEFAULT 0,
        status TEXT DEFAULT 'Active',
        created_date TEXT
    )
    """)
    cursor.execute("""
    INSERT OR IGNORE INTO customers
    (
        customer_name,
        mobile,
        whatsapp,
        gst_number,
        address
    )
    VALUES
    (
        'Cash Customer (Walk-in)',
        '',
        '',
        '',
        ''
    )
    """)

    conn.commit()
    conn.close()
    


def get_customer_names():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT customer_name
        FROM customers
        ORDER BY customer_name
    """)

    rows = cursor.fetchall()

    conn.close()

    return [row[0] for row in rows]