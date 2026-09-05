import sqlite3
import os
from datetime import datetime

DATABASE_FILE = "biomatch.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id TEXT UNIQUE NOT NULL,
            registration_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id TEXT NOT NULL,
            similarity_score REAL,
            result TEXT NOT NULL,
            brightness REAL,
            contrast REAL,
            security_status TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id TEXT,
            attack_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            source TEXT NOT NULL,
            action_taken TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

    print("Database initialized successfully.")
    print("Database:", os.path.abspath(DATABASE_FILE))


def log_security_event(
    subject_id,
    attack_type,
    severity,
    source,
    action_taken
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO security_events
        (
            subject_id,
            attack_type,
            severity,
            source,
            action_taken,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        subject_id,
        attack_type,
        severity,
        source,
        action_taken,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()


def get_recent_security_events(limit=20):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM security_events
        ORDER BY event_id DESC
        LIMIT ?
    """, (limit,))

    events = cursor.fetchall()

    connection.close()

    return events


if __name__ == "__main__":
    initialize_database()