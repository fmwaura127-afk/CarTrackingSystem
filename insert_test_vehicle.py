import sqlite3

conn = sqlite3.connect('car_system.db')
cur = conn.cursor()

cur.execute("""
INSERT INTO registrations 
(plate, pj_number, driver_name, phone, id_number, date_registered, qr_path) 
VALUES ('TEST001', 'PJ123', 'Test Driver', '123456789', 'ID123', '2024-01-01 12:00:00', 'static/TEST001.png')
""")

conn.commit()
conn.close()

print('Test vehicle inserted.')
