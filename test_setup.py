"""
Test script to verify database setup
"""
from app import create_app, db
from app.models import User
from app.routes.auth import hash_password

print("Creating Flask app...")
app = create_app()

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("✅ Tables created successfully!")
    
    print("\nCreating test user...")
    user = User(
        username='manager',
        password=hash_password('password'),
        full_name='Test Manager',
        role='Manager',
        email='manager@test.com',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    print("✅ Test user created!")
    
    # Verify
    test_user = User.query.filter_by(username='manager').first()
    if test_user:
        print(f"✅ Verification successful! User: {test_user.full_name} ({test_user.role})")
    else:
        print("❌ Could not verify user creation")
    
    print("\n🎉 Setup test completed successfully!")
    print("\nYou can now:")
    print("1. Run: python run.py")
    print("2. Visit: http://localhost:5000")
    print("3. Login with: manager / password")
