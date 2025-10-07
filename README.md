# Car Tracking System for Milimani Law Courts

## Overview
This is a Flask-based web application designed for the Judiciary of Kenya at Milimani Law Courts to manage vehicle registrations and track entry/exit movements. It allows administrators to register vehicles, generate QR codes for scanning, log movements, and export reports. The system includes secure admin login with hashed passwords and a forgot password feature using Gmail SMTP for resets. QR codes use a constant hostname-based URL (e.g., `http://{hostname}.local:5000/scan/{plate}`) to remain valid indefinitely, even if the server's IP changes (requires mDNS/Bonjour support).

The app runs on port 5000 and can be deployed as a standalone Windows EXE for easy client presentation without requiring Python installation.

### Key Features
- **Admin Authentication**: Login with username `admin` and password `admin123` (hashed in DB). Supports forgot password with email reset links (1-hour expiry).
- **Vehicle Registration**: Register vehicles with plate number, PJ number, driver details. Generates and saves QR code PNG to `static/`.
- **QR Code Scanning**: Scan QR to record entry/exit at locations (default: Gate 3). Handles registered/unregistered vehicles and prevents duplicate entries.
- **Logs & Movements**: View registered vehicles with QR previews, delete vehicles (password-protected), view entry/exit logs, export CSV, and print QRs/logs.
- **Security**: Password hashing (Werkzeug), session management, role-based access (admin only for logs/movements).
- **Email Integration**: SMTP via Gmail for password resets (configured for `fkuria204@gmail.com`).
- **Standalone Deployment**: Built into Windows EXE using PyInstaller, bundling DB, static files, and dependencies.

## System Requirements
- Python 3.8+ (with virtual environment recommended).
- Dependencies: Flask, qrcode[pil], psutil, Werkzeug (for hashing), smtplib (built-in).
- SQLite (built-in).
- For email: Gmail account with App Password (no 2FA or less secure apps enabled).
- Windows for EXE build (uses PyInstaller).
- mDNS support (Bonjour on Windows) for constant QR URLs.

## Setup
1. **Clone/Navigate to Project**:
   ```
   cd a:/CarTrackingSystem
   ```

2. **Create Virtual Environment** (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**:
   ```
   pip install flask qrcode[pil] psutil pyinstaller
   ```

4. **Database Setup**:
   - Run `python db_setup.py` to create `car_system.db` with tables: `users`, `registrations`, `vehicle_movements`, `password_resets`.
   - Default admin: Username `admin`, Password `admin123` (hashed), Email `fkuria204@gmail.com`, Role `admin`.
   - Optional: Run `python hash_password.py` to hash new passwords and update DB.
   - Test data: Run `python insert_test_vehicle.py` to add sample vehicles.

5. **Static Files**:
   - Ensure `static/` contains `Judiciary's logo.png` and any existing QR PNGs.
   - The app creates `static/` if missing.

6. **SMTP Configuration** (for forgot password):
   - In `app.py`: Update `SENDER_EMAIL` and `APP_PASSWORD` with your Gmail details.
   - Generate App Password: Google Account > Security > App Passwords.

7. **Run the App**:
   ```
   python app.py
   ```
   - Access at `http://localhost:5000` or `http://192.168.0.107:5000` (replace with your IP).
   - Server info: Visit `/server-info` for IP/hostname details.

## Usage
1. **Login**:
   - Go to `/` (root).
   - Enter `admin` / `admin123`.
   - On failure, error message displays (e.g., "❌ Invalid credentials.").

2. **Register Vehicle** (`/register`):
   - Fill form: Plate (e.g., `KAA987M`), PJ Number, Driver Name, Phone, ID.
   - Submit: Validates (no duplicates, PJ required), generates QR with constant URL, saves to DB and `static/{plate}.png`.
   - Success: Alert and redirect.

3. **View Logs** (`/logs`):
   - Table of registrations with details and QR preview.
   - Actions: Print QR (opens new tab), Delete (prompts password, removes from DB).

4. **View Movements** (`/movements`):
   - Table of entry/exit logs.
   - Actions: Export CSV (`/export_movements`), Print logs, Back to register.

5. **Scan QR**:
   - Use QR scanner app to scan generated QR (URL: `http://{hostname}.local:5000/scan/{plate}`).
   - Records entry/exit in DB, shows success/error page with links to movements/register.
   - Unregistered: Logs as "not registered".

6. **Forgot Password** (`/forgot-password`):
   - Enter email (`fkuria204@gmail.com`).
   - Receives reset link via email.
   - `/reset-password?token={token}`: Set new password (must match confirmation).

7. **Logout** (`/logout`): Clears session, redirects to login.

### Edge Cases Handled
- Duplicate plate: Alert and redirect.
- Invalid PJ: Alert.
- Already entered/exited: Logs appropriately, no duplicate action.
- Expired reset token: Error message.
- Unauthorized access: 403 redirect.
- QR not found: 404.

## Database Schema
SQLite `car_system.db` (auto-created/updated):

- **users**:
  - id (INTEGER PRIMARY KEY)
  - username (TEXT UNIQUE)
  - password (TEXT, hashed)
  - role (TEXT, e.g., 'admin')
  - email (TEXT)

- **registrations**:
  - id (INTEGER PRIMARY KEY)
  - plate (TEXT UNIQUE)
  - pj_number (TEXT)
  - driver_name (TEXT)
  - phone (TEXT)
  - id_number (TEXT)
  - date_registered (TEXT, ISO datetime)
  - qr_path (TEXT, e.g., 'static/KAA987M.png')

- **vehicle_movements**:
  - id (INTEGER PRIMARY KEY)
  - plate (TEXT)
  - entry_time (TEXT)
  - exit_time (TEXT)
  - scan_type (TEXT, 'entry'/'exit')
  - scan_status (TEXT, 'verified'/'not registered'/'already exited')
  - scanned_by (TEXT)
  - location (TEXT, default 'Gate 3')

- **password_resets**:
  - id (INTEGER PRIMARY KEY)
  - token (TEXT UNIQUE)
  - email (TEXT)
  - expiry (TEXT, ISO datetime)

Query example (using `query_vehicle_movements.py`):
```
python query_vehicle_movements.py
```

## API Endpoints
- **GET /**: Login page.
- **POST /login**: Authenticate (returns redirect).
- **GET/POST /register_vehicle**: Register vehicle.
- **GET /logs**: Vehicle registrations table.
- **GET /movements**: Entry/exit logs.
- **GET /export_movements**: CSV download.
- **GET /qr-code/{plate}**: Serve QR PNG.
- **GET /scan/{plate}?location=Gate3**: Process scan (HTML response).
- **POST /api/scan**: JSON scan (for integrations).
- **POST /delete_vehicle**: Delete vehicle (JSON, password required).
- **GET/POST /forgot-password**: Email reset.
- **GET/POST /reset-password?token=...**: Reset form.
- **GET /server-info**: Network details.
- **GET /debug-qr-url/{plate}**: View generated QR URL (debug).

Test endpoints with curl, e.g.:
```
curl http://localhost:5000/scan/KAA987M
```

## Building Standalone EXE (Windows)
1. Install PyInstaller: `pip install pyinstaller`.
2. Run: `pyinstaller app.spec` (includes datas for `static/`, `car_system.db`; hiddenimports for deps).
3. Output: `dist/CarTrackingSystem.exe` (bundles everything, ~100MB).
4. Run EXE: Double-click or `dist/CarTrackingSystem.exe` – starts server on 0.0.0.0:5000.
5. Distribute: Copy EXE + any updates to DB/static (EXE embeds initial files).

Notes:
- EXE uses bundled DB (copy `car_system.db` to EXE dir if updating).
- Antivirus may flag (false positive; sign if needed).
- For production: Use WSGI (e.g., Waitress) instead of dev server.

## Troubleshooting
- **IP Changes**: QR URLs use hostname.local (restart Bonjour/mDNS if resolution fails).
- **Email Fails**: Check Gmail App Password, firewall, or logs.
- **DB Errors**: Run `db_setup.py`; ensure write permissions.
- **EXE Issues**: Rebuild with `pyinstaller --clean app.spec`; check `build/app/warn-app.txt`.
- **Port 5000 Busy**: Kill processes: `taskkill /f /im python.exe` or `/im CarTrackingSystem.exe`.
- **No mDNS**: Manually add to hosts file or use fixed IP (but breaks constancy).

## Development
- Edit `app.py` for changes.
- Test: Run `python test_vehicle_movements.py` for unit tests.
- TODO: See `TODO.md` for pending items (e.g., IP fixes, enhancements).

## License & Contact
Open-source for Judiciary of Kenya use. Contact: fkuria204@gmail.com.

Last Updated: [Current Date]
