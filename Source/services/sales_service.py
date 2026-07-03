from models.sales import (
    save_sale,
    get_all_sales,
    delete_sale,
    search_sale
)


def add_sale(
    invoice,
    date,
    customer,
    product,
    quantity,
    price,
    gst,
    discount,
    total,
    payment_mode,
    warranty_type="Comprehensive"
):

    save_sale(
        invoice,
        date,
        customer,
        product,
        quantity,
        price,
        gst,
        discount,
        total,
        payment_mode,
        warranty_type
    )


def load_sales():
    return get_all_sales()


def remove_sale(sale_id):
    delete_sale(sale_id)


def find_sale(keyword):
    return search_sale(keyword)


def invoice_number_exists(invoice_no):
    """
    True if this invoice number has already been saved as a sale.
    Sales invoice numbers are usually auto-generated, but this guards
    against accidental duplicate entry if one is typed in manually.
    """
    from database.database import get_connection

    invoice_no = (invoice_no or "").strip()
    if not invoice_no:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM sales WHERE LOWER(TRIM(invoice_no)) = ? LIMIT 1",
        (invoice_no.lower(),)
    )
    found = cursor.fetchone() is not None
    conn.close()

    return found