import sqlite3

conn = sqlite3.connect('car_system.db')
cursor = conn.cursor()
cursor.execute("SELECT plate, qr_path FROM registrations")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()
