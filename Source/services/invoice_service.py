from datetime import datetime
from database.database import get_connection


def generate_invoice_number():

    conn = get_connection()
    cursor = conn.cursor()

    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")

    prefix = f"INV-{year}{month}"

    cursor.execute("""
        SELECT invoice_no
        FROM sales
        WHERE invoice_no LIKE ?
        ORDER BY id DESC
        LIMIT 1
    """, (prefix + "%",))

    row = cursor.fetchone()

    if row:
        last_number = int(row[0][-3:])
        next_number = last_number + 1
    else:
        next_number = 1

    conn.close()

    invoice_no = f"{prefix}{next_number:03d}"

    return invoice_no


def get_current_date():

    return datetime.now().strftime("%d-%m-%Y")


def get_current_time():

    return datetime.now().strftime("%I:%M:%S %p")


def get_current_datetime():

    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")