"""Quick database seed with minimal data"""
from app import create_app, db
from app.models import User, Supplier, Product
from app.routes.auth import hash_password

print("1/5 Creating app...")
app = create_app()

with app.app_context():
    print("2/5 Creating tables...")
    db.create_all()
    
    print("3/5 Adding users...")
    users = [
        User(username='manager', password=hash_password('password'), full_name='Juan Manager', role='Manager', email='mgr@nbs.com', is_active=True),
        User(username='staff', password=hash_password('password'), full_name='Maria Staff', role='Inventory Staff', email='staff@nbs.com', is_active=True),
        User(username='cashier', password=hash_password('password'), full_name='Pedro Cashier', role='Cashier', email='cashier@nbs.com', is_active=True),
    ]
    db.session.add_all(users)
    db.session.commit()
    
    print("4/5 Adding suppliers...")
    suppliers = [
        Supplier(name='Anvil Publishing', contact_person='Ana Cruz', phone='02-1234-5678', email='anvil@test.com', address='Manila', is_active=True),
        Supplier(name='Summit Books', contact_person='Ben Santos', phone='02-2345-6789', email='summit@test.com', address='QC', is_active=True),
    ]
    db.session.add_all(suppliers)
    db.session.commit()
    
    print("5/5 Adding products...")
    products = [
        Product(title='Noli Me Tangere', author='Jose Rizal', category='Fiction', supplier_id=1, unit_price=350.00, reorder_level=10, current_stock=25),
        Product(title='El Filibusterismo', author='Jose Rizal', category='Fiction', supplier_id=1, unit_price=380.00, reorder_level=10, current_stock=5),
        Product(title='Lola Basyang Stories', author='Severino Reyes', category="Children's Books", supplier_id=2, unit_price=295.00, reorder_level=15, current_stock=0),
        Product(title='Math Workbook', author='Various', category='Educational', supplier_id=2, unit_price=285.00, reorder_level=20, current_stock=45),
    ]
    db.session.add_all(products)
    db.session.commit()
    
    print("\n✅ DONE! Database seeded successfully!")
    print("\n📋 Login Credentials:")
    print("   Manager:   manager  / password")
    print("   Staff:     staff    / password")
    print("   Cashier:   cashier  / password")
    print("\n🚀 Run: python run.py")
    print("🌐 Visit: http://localhost:5000")
