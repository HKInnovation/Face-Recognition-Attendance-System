import sqlite3
import os

DB_NAME = "attendance.db"

# Remove old DB if exists (clean start)
if os.path.exists(DB_NAME):
    print("⚠️ Existing database found.")
    print("➡️ Delete it if you want a fresh start.")
else:
    print("🆕 Creating new database...")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    out_time TEXT
)
""")

conn.commit()
conn.close()

print("✅ attendance table created successfully")
