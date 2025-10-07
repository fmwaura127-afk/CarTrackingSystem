from app import db, Registration, app

with app.app_context():
    reg = Registration(
        plate='TEST001',
        pj_number='PJ001',
        driver_name='Test Driver',
        phone='123456',
        id_number='ID001',
        date_registered='2024-01-01 00:00:00'
    )
    db.session.add(reg)
    db.session.commit()
    print('Test vehicle inserted.')
