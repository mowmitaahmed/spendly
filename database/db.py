import os
import sqlite3
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

# Database file path — lives in project root; .gitignore already lists `expense_tracker.db`.
DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expense_tracker.db",
)


def get_db():
    """Open a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create users and expenses tables. Safe to call multiple times."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()


def seed_db():
    """Insert one demo user and 8 sample expenses. No-op if already seeded."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] > 0:
            return

        password_hash = generate_password_hash("demo123")
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )

        today = date.today()
        # (category, amount, description, days_ago) — covers all 7 fixed categories,
        # with Food repeated so we have 8 expenses.
        expenses = [
            ("Food", 1250.00, "Groceries at supermarket", 2),
            ("Transport", 850.00, "Monthly metro pass", 5),
            ("Bills", 320.00, "Electricity bill", 1),
            ("Health", 450.00, "Dental checkup", 12),
            ("Entertainment", 680.00, "Concert tickets", 8),
            ("Shopping", 2100.00, "New running shoes", 3),
            ("Other", 150.00, "Gym membership", 6),
            ("Food", 85.00, "Lunch at restaurant", 15),
        ]
        for category, amount, description, days_ago in expenses:
            expense_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            cur.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) "
                "VALUES (?, ?, ?, ?, ?)",
                (1, amount, category, expense_date, description),
            )

        conn.commit()
