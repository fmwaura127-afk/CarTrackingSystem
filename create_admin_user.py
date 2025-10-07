from app import db, Admin, app

def create_admin_user(username, password):
    with app.app_context():
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            print(f"Admin user with username {username} already exists.")
            return
        new_admin = Admin(username=username)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user with username {username} created successfully.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python create_admin_user.py <username> <password>")
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        create_admin_user(username, password)
