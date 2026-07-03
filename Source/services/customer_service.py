from database.database import get_connection


def find_duplicate_customer(mobile, exclude_id=None):
    """
    Returns True if a customer with this mobile number already
    exists. Mobile number is the natural unique key for a customer
    here (names commonly repeat; phone numbers shouldn't).
    """
    mobile = (mobile or "").strip()
    if not mobile:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id FROM customers WHERE TRIM(mobile) = ?"
    params = [mobile]

    if exclude_id:
        query += " AND id != ?"
        params.append(exclude_id)

    cursor.execute(query, params)
    found = cursor.fetchone() is not None

    conn.close()
    return found


def add_customer(
    customer_name,
    mobile,
    whatsapp,
    gst_number,
    address,
    vehicle_number,
    vehicle_model,
    email
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO customers(
            customer_name,
            mobile,
            whatsapp,
            gst_number,
            address,
            vehicle_number,
            vehicle_model,
            email,
            created_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        customer_name,
        mobile,
        whatsapp,
        gst_number,
        address,
        vehicle_number,
        vehicle_model,
        email
    ))

    conn.commit()
    conn.close()


def get_customer_by_id(customer_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM customers
        WHERE id=?
    """, (customer_id,))

    row = cursor.fetchone()

    conn.close()

    return row


def get_all_customers():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            customer_name,
            mobile,
            vehicle_number,
            outstanding,
            status
        FROM customers
        ORDER BY customer_name
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def update_customer(
    customer_id,
    customer_name,
    mobile,
    whatsapp,
    gst_number,
    address,
    vehicle_number,
    vehicle_model,
    email
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE customers
        SET
            customer_name=?,
            mobile=?,
            whatsapp=?,
            gst_number=?,
            address=?,
            vehicle_number=?,
            vehicle_model=?,
            email=?
        WHERE id=?
    """, (
        customer_name,
        mobile,
        whatsapp,
        gst_number,
        address,
        vehicle_number,
        vehicle_model,
        email,
        customer_id
    ))

    conn.commit()
    conn.close()


def delete_customer(customer_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT customer_name
        FROM customers
        WHERE id=?
        """,
        (customer_id,)
    )

    customer = cursor.fetchone()

    if customer and customer["customer_name"] == "Cash Customer (Walk-in)":
        conn.close()
        raise ValueError(
            "Cash Customer (Walk-in) cannot be deleted."
        )

    cursor.execute(
        "DELETE FROM customers WHERE id=?",
        (customer_id,)
    )

    conn.commit()
    conn.close()

def search_customer(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            customer_name,
            mobile,
            vehicle_number,
            outstanding,
            status
        FROM customers
        WHERE
            customer_name LIKE ?
            OR mobile LIKE ?
            OR vehicle_number LIKE ?
        ORDER BY customer_name
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows