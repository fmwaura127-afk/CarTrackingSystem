from werkzeug.security import generate_password_hash
import sqlite3

conn = sqlite3.connect('car_system.db')
cur = conn.cursor()

hashed = generate_password_hash('admin123')
cur.execute("UPDATE users SET password = ? WHERE username = 'admin'", (hashed,))
conn.commit()
conn.close()

print('Admin password updated to hashed version.')
