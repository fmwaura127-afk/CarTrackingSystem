from app import app, db, Registration, Movement

client = app.test_client()
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

def test_delete_happy_path():
    # Insert test data if not exists
    with app.app_context():
        reg = Registration.query.filter_by(plate='TESTDEL001').first()
        if not reg:
            reg = Registration(plate='TESTDEL001', pj_number='PJDEL001', driver_name='Delete Test', phone='999', id_number='DEL001', date_registered='2024-01-01 00:00:00')
            db.session.add(reg)
            db.session.commit()
        
        # Create a movement for the plate
        movement = VehicleMovement(plate='TESTDEL001', entry_time='2024-01-01 10:00:00', scan_type='entry', scan_status='verified', scanned_by='test', location='Gate 3')
        db.session.add(movement)
        db.session.commit()
    
    # Test happy path: correct password
    response = client.post('/delete_vehicle', json={'plate': 'TESTDEL001', 'password': 'admin123'})
    print(f"Status code: {response.status_code}")
    print(f"Response data: {response.get_data(as_text=True)}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'deleted successfully' in data['message']
    
    # Verify deletion from DB
    with app.app_context():
        reg_after = Registration.query.filter_by(plate='TESTDEL001').first()
        movement_after = VehicleMovement.query.filter_by(plate='TESTDEL001').first()
        assert reg_after is None
        assert movement_after is None
    
    print('Happy path test passed.')

def test_delete_wrong_password():
    # Insert test data again
    with app.app_context():
        reg = Registration(plate='TESTDEL002', pj_number='PJDEL002', driver_name='Wrong Pass Test', phone='888', id_number='WP001', date_registered='2024-01-01 00:00:00')
        db.session.add(reg)
        db.session.commit()
    
    # Test error path: wrong password
    response = client.post('/delete_vehicle', json={'plate': 'TESTDEL002', 'password': 'wrongpass'})
    assert response.status_code == 403
    data = response.get_json()
    assert data['success'] == False
    assert 'Unauthorized' in data['message']
    
    # Verify no deletion
    with app.app_context():
        reg_after = Registration.query.filter_by(plate='TESTDEL002').first()
        assert reg_after is not None
    
    print('Wrong password test passed.')

def test_delete_nonexistent_plate():
    response = client.post('/delete_vehicle', json={'plate': 'NONEXISTENT', 'password': 'admin123'})
    print(f"Status code: {response.status_code}")
    print(f"Response data: {response.get_data(as_text=True)}")
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] == False
    assert 'not found' in data['message'].lower()
    print('Non-existent plate test passed.')

def test_delete_empty_plate():
    response = client.post('/delete_vehicle', json={'plate': '', 'password': 'admin123'})
    print(f"Status code: {response.status_code}")
    print(f"Response data: {response.get_data(as_text=True)}")
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] == False
    assert 'plate number is required' in data['message'].lower()
    print('Empty plate test passed.')

def test_logs_integration():
    # Insert another test vehicle
    with app.app_context():
        reg = Registration.query.filter_by(plate='TESTLOG001').first()
        if not reg:
            reg = Registration(plate='TESTLOG001', pj_number='PJLOG001', driver_name='Log Test', phone='777', id_number='LOG001', date_registered='2024-01-01 00:00:00')
            db.session.add(reg)
            db.session.commit()
        
        # Verify exists before deletion
        assert Registration.query.filter_by(plate='TESTLOG001').first() is not None
    
    # Delete it
    response = client.post('/delete_vehicle', json={'plate': 'TESTLOG001', 'password': 'admin123'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    
    # Check after deletion
    with app.app_context():
        assert Registration.query.filter_by(plate='TESTLOG001').first() is None
    
    print('Logs integration test passed.')

def test_movements_integration():
    with app.app_context():
        reg = Registration.query.filter_by(plate='TESTMOV001').first()
        if not reg:
            reg = Registration(plate='TESTMOV001', pj_number='PJ001', driver_name='Test Driver', phone='123456', id_number='ID001', date_registered='2024-01-01 00:00:00')
            db.session.add(reg)
            db.session.commit()
        
        movement = VehicleMovement.query.filter_by(plate='TESTMOV001').first()
        if not movement:
            movement = VehicleMovement(plate='TESTMOV001', entry_time='2024-01-01 11:00:00', scan_type='entry', scan_status='verified', scanned_by='test', location='Gate 3')
            db.session.add(movement)
            db.session.commit()
        
        # Verify exists before deletion
        assert Registration.query.filter_by(plate='TESTMOV001').first() is not None
        assert VehicleMovement.query.filter_by(plate='TESTMOV001').first() is not None
    
    # Delete it (note: delete_vehicle deletes all movements for plate)
    response = client.post('/delete_vehicle', json={'plate': 'TESTMOV001', 'password': 'admin123'})
    print(f"Status code: {response.status_code}")
    print(f"Response data: {response.get_data(as_text=True)}")
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    
    # Check after deletion
    with app.app_context():
        assert Registration.query.filter_by(plate='TESTMOV001').first() is None
        assert VehicleMovement.query.filter_by(plate='TESTMOV001').first() is None
    
    print('Movements integration test passed.')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist
    test_delete_happy_path()
    test_delete_wrong_password()
    test_delete_nonexistent_plate()
    test_delete_empty_plate()
    test_logs_integration()
    test_movements_integration()
    print('All thorough tests passed.')
