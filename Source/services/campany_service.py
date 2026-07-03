"""
===========================================
 Company Profile Service
===========================================
Handles reading / writing the single-row "company" table that stores
the shop's own business details (used on the Settings page and
printed on sales invoices/receipts).
"""

from database.database import get_connection


def get_company():
    """
    Return the company profile row (id=1) or None if it hasn't
    been configured yet.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM company WHERE id = 1")

    row = cursor.fetchone()

    conn.close()

    return row


def save_company(
    company_name,
    gstin,
    phone,
    email,
    address,
    website
):
    """
    Insert or update the single company profile row (id is fixed to 1
    since a desktop ERP instance only manages one business).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM company WHERE id = 1")
    exists = cursor.fetchone()

    if exists:
        cursor.execute("""
            UPDATE company
            SET
                company_name=?,
                gstin=?,
                phone=?,
                email=?,
                address=?,
                website=?
            WHERE id=1
        """, (
            company_name,
            gstin,
            phone,
            email,
            address,
            website
        ))
    else:
        cursor.execute("""
            INSERT INTO company(
                id,
                company_name,
                gstin,
                phone,
                email,
                address,
                website
            )
            VALUES (1, ?, ?, ?, ?, ?, ?)
        """, (
            company_name,
            gstin,
            phone,
            email,
            address,
            website
        ))

    conn.commit()
    conn.close()


def get_audio_muted():
    """
    Returns True/False. Read independently of the rest of Settings so
    the audio service can check it fast at startup without touching
    unrelated preferences.
    """
    try:
        return bool(get_settings()["audio_muted"])
    except Exception:
        return False


def set_audio_muted(muted):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM settings WHERE id = 1")
    exists = cursor.fetchone()

    if exists:
        cursor.execute("UPDATE settings SET audio_muted=? WHERE id=1", (1 if muted else 0,))
    else:
        cursor.execute(
            "INSERT INTO settings (id, theme, currency, accent_theme, audio_muted) "
            "VALUES (1, 'light', 'INR', 'blue', ?)",
            (1 if muted else 0,)
        )

    conn.commit()
    conn.close()


def get_settings():
    """
    Return the single settings row (theme / currency / accent_theme),
    creating a default one if it doesn't exist yet.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM settings WHERE id = 1")
    row = cursor.fetchone()

    if not row:
        cursor.execute("""
            INSERT INTO settings (id, theme, currency, accent_theme)
            VALUES (1, 'light', 'INR', 'blue')
        """)
        conn.commit()

        cursor.execute("SELECT * FROM settings WHERE id = 1")
        row = cursor.fetchone()

    conn.close()

    return row


def save_settings(theme, currency, accent_theme="blue"):
    """
    Insert or update the single settings row.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM settings WHERE id = 1")
    exists = cursor.fetchone()

    if exists:
        cursor.execute("""
            UPDATE settings
            SET theme=?, currency=?, accent_theme=?
            WHERE id=1
        """, (theme, currency, accent_theme))
    else:
        cursor.execute("""
            INSERT INTO settings (id, theme, currency, accent_theme)
            VALUES (1, ?, ?, ?)
        """, (theme, currency, accent_theme))

    conn.commit()
    conn.close()
