import sqlite3
from datetime import datetime, timedelta

DATABASE_FILE = "biomatch.db"

MAX_FAILED_ATTEMPTS = 3
LOCKOUT_MINUTES = 2


def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def ensure_security_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authentication_security (
            subject_id TEXT PRIMARY KEY,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until TEXT,
            last_failed_at TEXT
        )
    """)

    connection.commit()
    connection.close()


def is_locked(subject_id):

    ensure_security_table()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT failed_attempts, locked_until
        FROM authentication_security
        WHERE subject_id = ?
    """, (subject_id,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return False, 0

    locked_until = row["locked_until"]

    if not locked_until:
        return False, row["failed_attempts"]

    lock_time = datetime.strptime(
        locked_until,
        "%Y-%m-%d %H:%M:%S"
    )

    if datetime.now() < lock_time:
        return True, row["failed_attempts"]

    reset_security_state(subject_id)

    return False, 0


def register_failed_attempt(subject_id):

    ensure_security_table()

    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now()

    cursor.execute("""
        SELECT failed_attempts
        FROM authentication_security
        WHERE subject_id = ?
    """, (subject_id,))

    row = cursor.fetchone()

    if row is None:

        failed_attempts = 1

        cursor.execute("""
            INSERT INTO authentication_security
            (
                subject_id,
                failed_attempts,
                locked_until,
                last_failed_at
            )
            VALUES (?, ?, NULL, ?)
        """, (
            subject_id,
            failed_attempts,
            now.strftime("%Y-%m-%d %H:%M:%S")
        ))

    else:

        failed_attempts = row["failed_attempts"] + 1

        cursor.execute("""
            UPDATE authentication_security
            SET failed_attempts = ?,
                last_failed_at = ?
            WHERE subject_id = ?
        """, (
            failed_attempts,
            now.strftime("%Y-%m-%d %H:%M:%S"),
            subject_id
        ))

    locked = False

    if failed_attempts >= MAX_FAILED_ATTEMPTS:

        locked_until = now + timedelta(
            minutes=LOCKOUT_MINUTES
        )

        cursor.execute("""
            UPDATE authentication_security
            SET locked_until = ?
            WHERE subject_id = ?
        """, (
            locked_until.strftime("%Y-%m-%d %H:%M:%S"),
            subject_id
        ))

        locked = True

    connection.commit()
    connection.close()

    return failed_attempts, locked


def reset_security_state(subject_id):

    ensure_security_table()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE authentication_security
        SET failed_attempts = 0,
            locked_until = NULL,
            last_failed_at = NULL
        WHERE subject_id = ?
    """, (subject_id,))

    connection.commit()
    connection.close()


def get_security_state(subject_id):

    ensure_security_table()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM authentication_security
        WHERE subject_id = ?
    """, (subject_id,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return {
            "failed_attempts": 0,
            "locked_until": None
        }

    return dict(row)


if __name__ == "__main__":

    ensure_security_table()

    print("======================================")
    print("SECURITY GUARD")
    print("======================================")
    print("Maximum failed attempts:", MAX_FAILED_ATTEMPTS)
    print("Lockout duration:", LOCKOUT_MINUTES, "minutes")
    print("Security table: READY")
    print("======================================")