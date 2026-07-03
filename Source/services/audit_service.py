"""
===========================================
 Audit Log Service
===========================================
Lightweight activity trail so the Admin can see who did what and
when (logins, user management, and other sensitive actions).
"""

from database.database import get_connection


def log_action(user, action):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO audit_logs (user, action) VALUES (?, ?)",
        (user, action)
    )

    conn.commit()
    conn.close()


def get_recent_logs(limit=100):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?",
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return rows
