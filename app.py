from flask import Flask, render_template, request, redirect, session, flash, jsonify, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os, qrcode, io, datetime, secrets, smtplib, pytz
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicle_log.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

nairobi_tz = pytz.timezone('Africa/Nairobi')

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pj_number = db.Column(db.String(20), unique=True, nullable=False)
    plate = db.Column(db.String(20), nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    qr_path = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Movement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # 'entry' or 'exit'
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class AuthorizedDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), unique=True, nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin'] = admin.username
            flash('Login successful', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid credentials', 'danger')
            return render_template('admin_login.html')
    return render_template('admin_login.html')

@app.route('/admin/devices', methods=['GET', 'POST'])
def manage_devices():
    if 'admin' not in session:
        return redirect('/admin-login')
    if request.method == 'POST':
        mac_address = request.form.get('mac_address')
        if not mac_address:
            flash('MAC address is required.', 'danger')
            return redirect('/admin/devices')
        existing = AuthorizedDevice.query.filter_by(mac_address=mac_address).first()
        if existing:
            flash('Device with this MAC address already exists.', 'warning')
            return redirect('/admin/devices')
        token = secrets.token_urlsafe(32)
        new_device = AuthorizedDevice(mac_address=mac_address, token=token)
        db.session.add(new_device)
        db.session.commit()
        flash(f'Device added successfully with token: {token}', 'success')
        return redirect('/admin/devices')
    devices = AuthorizedDevice.query.all()
    return render_template('admin_devices.html', devices=devices)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('Logged out successfully', 'info')
    return redirect('/admin-login')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            token = secrets.token_urlsafe(16)
            # Store token securely (e.g., in DB or cache)
            send_reset_email(email, token)
            flash('Password reset link sent to your email.', 'info')
        else:
            flash('Email not found.', 'danger')
    return render_template('reset_password.html')

def send_reset_email(to_email, token):
    msg = EmailMessage()
    msg['Subject'] = 'Password Reset'
    msg['From'] = 'noreply@judiciary.go.ke'
    msg['To'] = to_email
    msg.set_content(f'Click the link to reset your password: https://yourdomain.com/reset/{token}')
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
        smtp.send_message(msg)

@app.route('/register', methods=['GET', 'POST'])
def register_vehicle():
    if 'admin' not in session:
        return redirect('/admin-login')
    if request.method == 'POST':
        plate = request.form['plate'].upper()
        owner = request.form['owner']
        institution = request.form['institution']
        existing = Registration.query.filter_by(plate=plate).first()
        if existing:
            flash('Vehicle already registered.', 'warning')
        else:
            new_vehicle = Registration(plate=plate, owner=owner, institution=institution)
            db.session.add(new_vehicle)
            db.session.commit()
            flash('Vehicle registered successfully.', 'success')
    return render_template('register.html')

@app.route('/generate-qr/<plate>')
def generate_qr(plate):
    if 'admin' not in session:
        return redirect('/admin-login')
    # Generate QR code encoding the URL to scan and verify the plate with token
    base_url = os.getenv('BASE_URL')
    if not base_url:
        base_url = request.host_url.rstrip('/')
    print(f"Generating QR code with base_url: {base_url}")
    # For demo, get the first authorized device token
    device = AuthorizedDevice.query.first()
    token = device.token if device else ''
    qr_url = f"{base_url}/scan-qr?plate={plate}&token={token}"
    img = qrcode.make(qr_url)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/track/<plate>/<action>')
def track_movement(plate, action):
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Access denied: No token provided'}), 403
    authorized_device = AuthorizedDevice.query.filter_by(token=token).first()
    if not authorized_device:
        return jsonify({'error': 'Access denied: Invalid token'}), 403
    if action not in ['entry', 'exit']:
        return jsonify({'error': 'Invalid action'}), 400
    # Check if vehicle is registered
    vehicle = Registration.query.filter_by(plate=plate.upper()).first()
    if not vehicle:
        return jsonify({'status': 'error', 'message': 'Vehicle not registered'}), 404
    log = Movement(plate=plate.upper(), action=action)
    db.session.add(log)
    db.session.commit()
    return jsonify({'status': 'success', 'plate': plate, 'action': action})

@app.route('/scan-qr')
def scan_qr():
    plate = request.args.get('plate')
    token = request.args.get('token')
    if not plate or not token:
        return "Missing plate or token", 400
    authorized_device = AuthorizedDevice.query.filter_by(token=token).first()
    if not authorized_device:
        return "Access denied: Invalid token", 403
    return render_template('scan_qr.html', plate=plate, token=token)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'admin' not in session:
        return redirect('/admin-login')
    message = None
    if request.method == 'POST':
        pj_number = request.form.get('pj_number')
        plate = request.form.get('plate')
        driver_name = request.form.get('driver_name')
        phone_number = request.form.get('phone_number')
        id_number = request.form.get('id_number')

        # Check if PJ number is unique
        existing = Registration.query.filter_by(pj_number=pj_number).first()
        if existing:
            message = f"PJ Number {pj_number} is already registered."
        else:
            new_vehicle = Registration(
                pj_number=pj_number,
                plate=plate.upper() if plate else None,
                owner=driver_name,
                institution=phone_number  # Using institution field to store phone number temporarily
            )
            db.session.add(new_vehicle)
            db.session.commit()
            # Generate and save QR code
            if plate:
                base_url = os.getenv('BASE_URL')
                if not base_url:
                    base_url = request.host_url.rstrip('/')
                device = AuthorizedDevice.query.first()
                token = device.token if device else ''
                qr_url = f"{base_url}/scan-qr?plate={plate}&token={token}"
                img = qrcode.make(qr_url)
                qr_filename = f"{plate}.png"
                qr_path = f"static/{qr_filename}"
                img.save(qr_path)
                new_vehicle.qr_path = qr_path
                db.session.commit()
            message = f"Vehicle with plate number {plate} registered successfully. QR code generated."

    return render_template('dashboard.html', message=message)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_vehicle(id):
    if 'admin' not in session:
        return redirect('/admin-login')
    admin_username = session['admin']
    admin = Admin.query.filter_by(username=admin_username).first()
    if not admin:
        flash('Admin user not found.', 'danger')
        return redirect('/view-vehicles')
    password = request.form.get('admin_password')
    if not password:
        flash('Password is required to delete a vehicle.', 'danger')
        return redirect('/view-vehicles')
    if not admin.check_password(password):
        flash('Invalid admin password.', 'danger')
        return redirect('/view-vehicles')
    try:
        vehicle = Registration.query.get_or_404(id)
        db.session.delete(vehicle)
        db.session.commit()
        flash('Vehicle deleted successfully.', 'success')
    except Exception:
        flash('An error occurred while deleting the vehicle.', 'danger')
    return redirect('/view-vehicles')



@app.route('/test-post', methods=['POST'])
def test_post():
    print("Test POST route called")
    data = request.form.to_dict()
    print(f"Received data: {data}")
    return "POST request received successfully", 200

from flask import get_flashed_messages

@app.route('/view-vehicles')
def view_vehicles():
    if 'admin' not in session:
        return redirect('/admin-login')
    # Clear any existing flash messages to avoid showing stale messages
    get_flashed_messages()
    vehicles = Registration.query.order_by(Registration.timestamp.desc()).all()
    # Convert naive timestamps to aware in UTC, then to Nairobi timezone
    for vehicle in vehicles:
        if vehicle.timestamp.tzinfo is None:
            vehicle.timestamp = pytz.utc.localize(vehicle.timestamp)
        vehicle.timestamp = vehicle.timestamp.astimezone(nairobi_tz)
    return render_template('view_vehicles.html', vehicles=vehicles, nairobi_tz=nairobi_tz)

@app.route('/view-logs')
def view_logs():
    if 'admin' not in session:
        return redirect('/admin-login')
    logs = Movement.query.order_by(Movement.timestamp.desc()).all()
    # Convert naive timestamps to aware in UTC, then to Nairobi timezone
    for log in logs:
        if log.timestamp.tzinfo is None:
            log.timestamp = pytz.utc.localize(log.timestamp)
        log.timestamp = log.timestamp.astimezone(nairobi_tz)
    return render_template('view_logs.html', logs=logs, nairobi_tz=nairobi_tz)

@app.route('/')
def root():
    return redirect(url_for('admin_login'))

@app.route('/debug-base-url')
def debug_base_url():
    base_url = os.getenv('BASE_URL')
    if not base_url:
        base_url = request.host_url.rstrip('/')
    return f"Current BASE_URL used for QR code generation: {base_url}"


# Route to clear vehicle logs with admin password check
@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Invalid request.'}), 400
    data = request.get_json()
    password = data.get('password', '')
    admin = Admin.query.filter_by(username='admin').first()
    if not admin or not admin.check_password(password):
        return jsonify({'success': False, 'message': 'Incorrect admin password.'}), 403
    try:
        num_deleted = Movement.query.delete()
        db.session.commit()
        return jsonify({'success': True, 'message': f'Logs cleared ({num_deleted} entries deleted).'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error clearing logs.'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
