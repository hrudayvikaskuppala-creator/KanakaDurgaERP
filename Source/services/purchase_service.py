from database.database import get_connection
from models.purchase import (
    save_purchase,
    get_all_purchases,
    delete_purchase,
    search_purchase
)


def add_purchase(
    invoice,
    date,
    supplier,
    product,
    quantity,
    price,
    gst,
    total,
    discount=0
):
    save_purchase(
        invoice,
        date,
        supplier,
        product,
        quantity,
        price,
        gst,
        total,
        discount
    )


def load_purchases():
    return get_all_purchases()


def remove_purchase(purchase_id):
    delete_purchase(purchase_id)


def find_purchase(keyword):
    return search_purchase(keyword)


def get_products_for_supplier(supplier_name):
    """
    Distinct products previously purchased from this supplier, so the
    Purchase page can narrow the product list down once a supplier is
    picked (falls back to all products if there's no history yet).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT product_name
        FROM purchases
        WHERE supplier_name = ?
        ORDER BY product_name
    """, (supplier_name,))

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]


def get_last_purchase(supplier_name, product_name):
    """
    Returns the most recent price/GST paid for this supplier+product
    combo, so the form can auto-fill it (nice for repeat restocking).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT purchase_price, gst
        FROM purchases
        WHERE supplier_name = ? AND product_name = ?
        ORDER BY id DESC
        LIMIT 1
    """, (supplier_name, product_name))

    row = cursor.fetchone()
    conn.close()

    return row


def invoice_number_exists(invoice_no, supplier_name):
    """
    True if this invoice number has already been saved for this
    supplier. Used to stop the same invoice being entered twice by
    accident (a very common real-world data-entry mistake).
    """
    invoice_no = (invoice_no or "").strip()
    supplier_name = (supplier_name or "").strip()

    if not invoice_no or not supplier_name:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM purchases
        WHERE LOWER(TRIM(invoice_no)) = ?
          AND LOWER(TRIM(supplier_name)) = ?
        LIMIT 1
    """, (invoice_no.lower(), supplier_name.lower()))

    found = cursor.fetchone() is not None
    conn.close()

    return found