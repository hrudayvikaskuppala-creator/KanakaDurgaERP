import bcrypt

from database.database import execute, fetchone, fetchall


def create_admin():

    admin = fetchone(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    )

    if admin:
        return

    password = bcrypt.hashpw(
        "admin123".encode(),
        bcrypt.gensalt()
    ).decode()

    execute(
        """
        INSERT INTO users
        (
            username,
            password,
            full_name,
            role
        )
        VALUES
        (?,?,?,?)
        """,
        (
            "admin",
            password,
            "Administrator",
            "Admin"
        )
    )


def login(username, password):

    user = fetchone(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    if not user:
        return None

    if bcrypt.checkpw(
        password.encode(),
        user["password"].encode()
    ):
        return user

    return None


def change_password(username, old_password, new_password):
    """
    Verify the current password and, if correct, update it to the
    new one. Returns True on success, False if the old password
    doesn't match / user doesn't exist.
    """
    user = login(username, old_password)

    if not user:
        return False

    hashed = bcrypt.hashpw(
        new_password.encode(),
        bcrypt.gensalt()
    ).decode()

    execute(
        "UPDATE users SET password=? WHERE username=?",
        (hashed, username)
    )

    return True


def get_all_users():
    return fetchall(
        "SELECT id, username, full_name, role, status, created_at FROM users ORDER BY id"
    )


def get_user_by_id(user_id):
    return fetchone(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    )


def username_exists(username, exclude_id=None):
    if exclude_id:
        row = fetchone(
            "SELECT id FROM users WHERE username=? AND id!=?",
            (username, exclude_id)
        )
    else:
        row = fetchone(
            "SELECT id FROM users WHERE username=?",
            (username,)
        )

    return row is not None


def create_user(username, password, full_name, role):
    """
    Admin-only: create a brand new user account.
    """
    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    execute(
        """
        INSERT INTO users (username, password, full_name, role, status)
        VALUES (?, ?, ?, ?, 1)
        """,
        (username, hashed, full_name, role)
    )


def update_user(user_id, full_name, role, status):
    """
    Admin-only: update a user's profile / role / active status.
    Does not touch the password - use reset_password for that.
    """
    execute(
        "UPDATE users SET full_name=?, role=?, status=? WHERE id=?",
        (full_name, role, status, user_id)
    )


def reset_password(user_id, new_password):
    """
    Admin-only: force-set a user's password without needing to know
    the old one (e.g. when a user forgets their password).
    """
    hashed = bcrypt.hashpw(
        new_password.encode(),
        bcrypt.gensalt()
    ).decode()

    execute(
        "UPDATE users SET password=? WHERE id=?",
        (hashed, user_id)
    )


def count_active_admins(exclude_id=None):
    """
    Used to guard against locking everyone out by deleting/demoting
    the last remaining active Admin account.
    """
    if exclude_id:
        row = fetchone(
            """
            SELECT COUNT(*) AS c FROM users
            WHERE role='Admin' AND status=1 AND id!=?
            """,
            (exclude_id,)
        )
    else:
        row = fetchone(
            "SELECT COUNT(*) AS c FROM users WHERE role='Admin' AND status=1"
        )

    return row["c"] if row else 0


def delete_user(user_id):
    execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )