from database.database import get_connection
from models.supplier import get_supplier_names


def find_duplicate_supplier(supplier_name, mobile, gst_number, exclude_id=None):
    """
    Returns a short reason string ("name", "mobile" or "GST number")
    if a supplier with a matching name, mobile, or GST number already
    exists (case-insensitive, ignoring blank values), otherwise None.
    Used to block duplicate supplier entries before they're saved.
    """
    conn = get_connection()
    cursor = conn.cursor()

    name = (supplier_name or "").strip().lower()
    mobile = (mobile or "").strip()
    gst_number = (gst_number or "").strip().upper()

    if name:
        query = "SELECT id FROM suppliers WHERE LOWER(TRIM(supplier_name)) = ?"
        params = [name]
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        cursor.execute(query, params)
        if cursor.fetchone():
            conn.close()
            return "name"

    if mobile:
        query = "SELECT id FROM suppliers WHERE TRIM(mobile) = ?"
        params = [mobile]
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        cursor.execute(query, params)
        if cursor.fetchone():
            conn.close()
            return "mobile"

    if gst_number:
        query = "SELECT id FROM suppliers WHERE UPPER(TRIM(gst_number)) = ?"
        params = [gst_number]
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        cursor.execute(query, params)
        if cursor.fetchone():
            conn.close()
            return "GST number"

    conn.close()
    return None


def add_supplier(
    supplier_name,
    mobile,
    gst_number,
    address,
    email
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO suppliers(
            supplier_name,
            mobile,
            gst_number,
            address,
            email,
            created_date
        )
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (
        supplier_name,
        mobile,
        gst_number,
        address,
        email
    ))

    conn.commit()
    conn.close()


def get_all_suppliers():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            supplier_name,
            mobile,
            outstanding,
            status
        FROM suppliers
        ORDER BY supplier_name
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_supplier_by_id(supplier_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM suppliers WHERE id=?",
        (supplier_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def update_supplier(
    supplier_id,
    supplier_name,
    mobile,
    gst_number,
    address,
    email
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE suppliers
        SET supplier_name=?,
            mobile=?,
            gst_number=?,
            address=?,
            email=?
        WHERE id=?
    """, (
        supplier_name,
        mobile,
        gst_number,
        address,
        email,
        supplier_id
    ))

    conn.commit()
    conn.close()


def delete_supplier(supplier_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM suppliers WHERE id=?",
        (supplier_id,)
    )

    conn.commit()
    conn.close()


def search_suppliers(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            supplier_name,
            mobile,
            outstanding,
            status
        FROM suppliers
        WHERE supplier_name LIKE ?
           OR mobile LIKE ?
           OR gst_number LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


def adjust_outstanding(supplier_name, amount):
    """
    Adds `amount` (can be negative to reduce it) to a supplier's
    outstanding balance. Used by the Purchase page when an invoice is
    saved with an unpaid/partial balance, so supplier balances stay
    accurate without a separate manual step.
    """
    if not supplier_name or not amount:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE suppliers SET outstanding = COALESCE(outstanding, 0) + ? "
        "WHERE supplier_name = ?",
        (amount, supplier_name)
    )

    conn.commit()
    conn.close()