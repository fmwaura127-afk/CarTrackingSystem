from app import app, Admin

with app.app_context():
    admins = Admin.query.all()
    print([admin.username for admin in admins])
