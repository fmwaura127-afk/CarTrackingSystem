from app import db, Admin, app

def reset_admin_password(username, new_password):
    with app.app_context():
        admin = Admin.query.filter_by(username=username).first()
        if not admin:
            print(f"No admin user found with username {username}.")
            return
        admin.set_password(new_password)
        db.session.commit()
        print(f"Password for admin user '{username}' has been reset successfully.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python reset_admin_password.py <username> <new_password>")
    else:
        username = sys.argv[1]
        new_password = sys.argv[2]
        reset_admin_password(username, new_password)
