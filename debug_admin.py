from app import db, User, app
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"Admin found. Updating password.")
        hashed = generate_password_hash('admin123')
        admin.password = hashed
        db.session.commit()
        print("Admin password updated.")
    else:
        print("No admin user found.")
        hashed = generate_password_hash('admin123')
        admin = User(username='admin', password=hashed, email='fkuria204@gmail.com', role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin created.")
