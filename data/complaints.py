import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path("complaints.db")


def create_table():

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT UNIQUE,
            customer_name TEXT,
            complaint TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def register_complaint(name, complaint):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO complaints
        (customer_name, complaint, status, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        complaint,
        "Pending",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    row_id = cursor.lastrowid
    complaint_id = f"CMP-{1000 + row_id}"

    cursor.execute("""
        UPDATE complaints
        SET complaint_id = ?
        WHERE id = ?
    """, (complaint_id, row_id))

    conn.commit()
    conn.close()

    return complaint_id


def get_complaint_status(complaint_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT complaint_id, customer_name,
               complaint, status, created_at
        FROM complaints
        WHERE complaint_id = ?
    """, (complaint_id,))

    result = cursor.fetchone()

    conn.close()

    return result


# --------------------------------
# Get all complaints
# --------------------------------

def get_all_complaints():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id,
               complaint_id,
               customer_name,
               complaint,
               status,
               created_at
        FROM complaints
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# --------------------------------
# Update complaint status
# --------------------------------

def update_complaint_status(
    complaint_id,
    status
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE complaints
        SET status = ?
        WHERE complaint_id = ?
    """, (
        status,
        complaint_id
    ))

    conn.commit()

    updated = cursor.rowcount

    conn.close()

    return updated > 0


create_table()