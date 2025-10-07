# Thorough Testing Plan for CarTrackingSystem Flask App

## 1. Root URL and Redirection
- Access http://127.0.0.1:5000/
- Confirm it redirects to /admin-login

## 2. Admin Login and Logout
- Test login with valid admin credentials
- Test login with invalid credentials
- Test logout functionality

## 3. Password Reset Flow
- Access /reset-password
- Submit valid and invalid email addresses
- Confirm email sending (mock or check logs)

## 4. Vehicle Registration
- Access /register after login
- Register new vehicle with valid data
- Attempt to register duplicate vehicle plate
- Confirm success and warning messages

## 5. QR Code Generation
- Access /generate-qr/<plate> for registered vehicle
- Confirm QR code image is generated and displayed

## 6. Vehicle Movement Tracking
- Access /track/<plate>/<action> with valid and invalid actions
- Confirm JSON response and database logging

## 7. Dashboard Display
- Access /dashboard after login
- Confirm vehicle list and recent logs display correctly

## 8. Vehicle Deletion
- Attempt to delete vehicle with correct admin password
- Attempt deletion with incorrect password
- Confirm success and error messages

---

# Deployment with WSGI

## 1. Add Waitress to requirements.txt
- Add 'waitress' to requirements.txt (changed from gunicorn due to Windows compatibility)

## 2. Create WSGI entry point
- Create wsgi.py file with app import

## 3. Install dependencies
- Run pip install -r requirements.txt

## 4. Run with Waitress
- Execute waitress-serve --host=0.0.0.0 --port=8000 wsgi:app
- App is now running on http://0.0.0.0:8000

---

Please confirm if you want me to proceed with the thorough testing as outlined above.
