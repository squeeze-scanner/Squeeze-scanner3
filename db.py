import sqlite3
import time

conn = sqlite3.connect("squeeze.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS signals (
    ticker TEXT,
    score REAL,
    signal TEXT,
    price REAL,
    timestamp INTEGER
)
""")

conn.commit()


def save_signal(data):
    cursor.execute("""
        INSERT INTO signals VALUES (?, ?, ?, ?, ?)
    """, (
        data["ticker"],
        data["score"],
        data["signal"],
        data["price"],
        int(time.time())
    ))
    conn.commit()
