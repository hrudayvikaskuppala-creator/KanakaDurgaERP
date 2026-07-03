from database.database import get_connection


def create_pos_transactions_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pos_transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT,
        amount REAL,
        payment_mode TEXT,
        provider TEXT,
        transaction_id TEXT,
        approval_code TEXT,
        reference_no TEXT,
        status TEXT,
        message TEXT,
        created_date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_pos_transaction(
    invoice_no, amount, payment_mode, provider,
    transaction_id, approval_code, reference_no, status, message
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pos_transactions(
            invoice_no, amount, payment_mode, provider,
            transaction_id, approval_code, reference_no, status, message
        )
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        invoice_no, amount, payment_mode, provider,
        transaction_id, approval_code, reference_no, status, message
    ))

    conn.commit()
    conn.close()


def get_all_pos_transactions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pos_transactions ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_pos_transactions_for_invoice(invoice_no):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM pos_transactions WHERE invoice_no = ? ORDER BY id DESC",
        (invoice_no,)
    )
    rows = cursor.fetchall()

    conn.close()
    return rows
