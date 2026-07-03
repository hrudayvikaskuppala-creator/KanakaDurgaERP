import sqlite3
import os

DATABASE_NAME = "battery_erp.db"


def get_connection():
    db_path = os.path.join(os.getcwd(), DATABASE_NAME)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Enable Foreign Keys
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def execute(query, params=()):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(query, params)

    conn.commit()

    conn.close()


def fetchall(query, params=()):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(query, params)

    rows = cursor.fetchall()

    conn.close()

    return rows


def fetchone(query, params=()):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(query, params)

    row = cursor.fetchone()

    conn.close()

    return row