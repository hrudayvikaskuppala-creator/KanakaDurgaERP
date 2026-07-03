from database.database import execute


def migrate():

    execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        full_name TEXT,
        role TEXT,
        status INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS company(
        id INTEGER PRIMARY KEY,
        company_name TEXT,
        gstin TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        website TEXT
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY,
        theme TEXT DEFAULT 'light',
        currency TEXT DEFAULT 'INR',
        accent_theme TEXT DEFAULT 'blue',
        audio_muted INTEGER DEFAULT 0
    )
    """)

    # Older databases won't have these columns yet - safe, additive
    # migrations so existing installs pick up new Settings options
    # without losing their saved preferences.
    from database.database import fetchall
    columns = [row[1] for row in fetchall("PRAGMA table_info(settings)")]
    if "accent_theme" not in columns:
        execute("ALTER TABLE settings ADD COLUMN accent_theme TEXT DEFAULT 'blue'")
    if "audio_muted" not in columns:
        execute("ALTER TABLE settings ADD COLUMN audio_muted INTEGER DEFAULT 0")

    execute("""
    CREATE TABLE IF NOT EXISTS audit_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        action TEXT,
        log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)