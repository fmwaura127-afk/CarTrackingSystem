import unittest
import json
from app import app, db
import sqlite3
from bs4 import BeautifulSoup

class VehicleMovementTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Setup test database
        conn = sqlite3.connect('car_system.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM vehicle_movements")
        cur.execute("DELETE FROM registrations")
        # Insert a test registered vehicle
        cur.execute("""
            INSERT INTO registrations (plate, pj_number, driver_name, phone, id_number, date_registered, qr_path)
            VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
        """, ("TEST123", "12345", "Test Driver", "1234567890", "987654321", "static/TEST123.png"))
        conn.commit()
        conn.close()

    def test_scan_registered_vehicle_entry(self):
        response = self.app.get('/scan/TEST123')
        soup = BeautifulSoup(response.data, 'html.parser')
        message = soup.find('h1').text.upper()
        self.assertIn('VEHICLE TEST123 ENTRY RECORDED', message)

    def test_scan_registered_vehicle_exit(self):
        # First entry
        self.app.get('/scan/TEST123')
        # Then exit
        response = self.app.get('/scan/TEST123')
        soup = BeautifulSoup(response.data, 'html.parser')
        message = soup.find('h1').text.upper()
        self.assertIn('VEHICLE TEST123 EXIT RECORDED', message)

    def test_scan_unregistered_vehicle(self):
        response = self.app.get('/scan/UNREG123')
        soup = BeautifulSoup(response.data, 'html.parser')
        message = soup.find('h1').text.upper()
        self.assertIn('NOT VERIFIED FOR ENTRY', message)

    def test_api_scan_registered_vehicle_entry(self):
        response = self.app.post('/api/scan', json={"plate": "TEST123", "location": "Gate 1"})
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('ENTRY recorded', data['message'])

    def test_api_scan_unregistered_vehicle(self):
        response = self.app.post('/api/scan', json={"plate": "UNREG123", "location": "Gate 1"})
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('NOT VERIFIED', data['message'])

    def test_api_scan_missing_plate(self):
        response = self.app.post('/api/scan', json={"location": "Gate 1"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Plate number is required', data['message'])

if __name__ == '__main__':
    unittest.main()
