import sqlite3

def get_latest_vehicle_movements(limit=5):
    conn = sqlite3.connect('car_system.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM vehicle_movements ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    movements = get_latest_vehicle_movements()
    for movement in movements:
        print(movement)
