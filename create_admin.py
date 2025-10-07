import sqlite3

conn = sqlite3.connect('car_system.db')
cur = conn.cursor()

# Insert initial admin account
cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
            ("admin", "newpass123", "admin"))

conn.commit()
conn.close()