import sqlite3

conn = sqlite3.connect("flights.db")
conn.execute("PRAGMA foreign_keys = ON")

# CHECK constraint should reject an invalid role
try:
    conn.execute("INSERT INTO FlightCrew VALUES (1, 1, 'Navigator')")
    print("FAIL: bad role accepted")
except sqlite3.IntegrityError as e:
    print("PASS - CHECK blocked bad role:", e)

conn.close()