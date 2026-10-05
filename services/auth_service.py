"""
services/auth_service.py
Secure local authentication service using SQLite and PBKDF2-HMAC password hashing.
Handles user registration, authentication, password verification, and session helpers.
"""

import os
import sqlite3
import hashlib
import hmac
import re
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "users.db")


def _get_db():
    """Get SQLite database connection, ensuring parent directory exists."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the users database table and seed initial demo accounts."""
    conn = _get_db()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

    # Seed demo users if table is empty
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        create_user("Naga Varshitha", "varshitha@jobshield.ai", "password123")
        create_user("Candidate Demo", "demo@jobshield.ai", "demo123")
    conn.close()


def _hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    """
    Cryptographically secure PBKDF2-HMAC-SHA256 password hashing.
    Returns (hash_hex, salt_hex).
    """
    if salt is None:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return key.hex(), salt.hex()


def _verify_password(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    """Verify password against salt and expected hash using constant-time comparison."""
    try:
        salt = bytes.fromhex(salt_hex)
        computed_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000).hex()
        return hmac.compare_digest(computed_hash, expected_hash_hex)
    except Exception:
        return False


def create_user(name: str, email: str, password: str) -> tuple[dict | None, str | None]:
    """
    Register a new user with secure password hashing.
    Returns:
        (user_dict, None) on success
        (None, error_message) on failure
    """
    name = (name or "").strip()
    email = (email or "").strip().lower()

    if len(name) < 2:
        return None, "Full name must be at least 2 characters."
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return None, "Please enter a valid email address."
    if len(password) < 6:
        return None, "Password must be at least 6 characters."

    pwd_hash, salt = _hash_password(password)
    created_at = datetime.utcnow().isoformat()

    conn = _get_db()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (email, name, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (email, name, pwd_hash, salt, created_at))
            user_id = cursor.lastrowid

        return {
            "id": user_id,
            "name": name,
            "email": email,
            "created_at": created_at
        }, None
    except sqlite3.IntegrityError:
        return None, "An account with this email already exists. Please log in."
    except Exception as e:
        return None, f"Database error: {str(e)}"
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> tuple[dict | None, str | None]:
    """
    Authenticate user with email and password.
    Returns:
        (user_dict, None) on success
        (None, error_message) on failure
    """
    email = (email or "").strip().lower()
    if not email or not password:
        return None, "Please provide both email and password."

    conn = _get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, password_hash, salt, created_at FROM users WHERE LOWER(email) = ?", (email,))
        row = cursor.fetchone()
        if not row:
            return None, "Invalid email or password."

        if not _verify_password(password, row["salt"], row["password_hash"]):
            return None, "Invalid email or password."

        return {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "created_at": row["created_at"]
        }, None
    except Exception as e:
        return None, f"Authentication error: {str(e)}"
    finally:
        conn.close()


# Ensure DB is initialized when module is imported
init_db()
