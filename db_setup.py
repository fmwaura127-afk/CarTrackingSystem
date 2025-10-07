import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('car_system.db')
cursor = conn.cursor()

# Admin users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
''')

# Add email column if not exists
cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]
if 'email' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")

# Create password_resets table
cursor.execute('''
CREATE TABLE IF NOT EXISTS password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE,
    email TEXT,
    expiry TEXT
)
''')

# Vehicle registrations
cursor.execute('''
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate TEXT,
    pj_number TEXT,
    driver_name TEXT,
    phone TEXT,
    id_number TEXT,
    date_registered TEXT,
    qr_path TEXT
)
''')

# Vehicle movements (entry/exit tracking)
cursor.execute('''
DROP TABLE IF EXISTS vehicle_movements;
''')

cursor.execute('''
CREATE TABLE vehicle_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate TEXT,
    entry_time TEXT,
    exit_time TEXT,
    scan_type TEXT,
    scan_status TEXT,
    scanned_by TEXT,
    location TEXT
)
''')

# Update or insert admin user with hashed password and email
hashed_password = generate_password_hash('admin123')
cursor.execute("SELECT id FROM users WHERE username='admin'")
if cursor.fetchone():
    cursor.execute("UPDATE users SET password=?, email=? WHERE username='admin'", (hashed_password, 'fkuria204@gmail.com'))
else:
    cursor.execute("INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)", ('admin', hashed_password, 'admin', 'fkuria204@gmail.com'))

# Check latest 5 vehicle movements
cursor.execute("SELECT * FROM vehicle_movements ORDER BY id DESC LIMIT 5;")
rows = cursor.fetchall()

for row in rows:
    print(row)


conn.commit()
conn.close()
