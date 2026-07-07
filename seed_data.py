"""
Seed script for National Book Store SCM System
Creates realistic sample data for testing
"""
from app import create_app, db
from app.models import User, Supplier, Product, PurchaseOrder, PurchaseOrderItem, Delivery, DeliveryItem, Sales, SalesItem, InventoryLog
from app.routes.auth import hash_password
from datetime import datetime, timedelta
import random

def seed_database():
    """Populate database with sample data."""
    app = create_app()
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Seeding users...")
        users = [
            User(username='manager', password=hash_password('password'), full_name='Juan Dela Cruz', 
                 role='Manager', email='manager@nbs.com', is_active=True),
            User(username='staff', password=hash_password('password'), full_name='Maria Santos', 
                 role='Inventory Staff', email='staff@nbs.com', is_active=True),
            User(username='cashier', password=hash_password('password'), full_name='Pedro Reyes', 
                 role='Cashier', email='cashier@nbs.com', is_active=True),
        ]
        db.session.add_all(users)
        db.session.commit()
        
        print("Seeding suppliers...")
        suppliers = [
            Supplier(name='Anvil Publishing', contact_person='Ana Reyes', phone='02-1234-5678', 
                    email='sales@anvil.com.ph', address='Manila, Philippines', is_active=True),
            Supplier(name='Summit Books', contact_person='Carlos Santos', phone='02-2345-6789', 
                    email='orders@summitbooks.ph', address='Quezon City, Philippines', is_active=True),
            Supplier(name='Precious Pages Corp', contact_person='Linda Garcia', phone='02-3456-7890', 
                    email='info@preciouspages.com', address='Makati City, Philippines', is_active=True),
            Supplier(name='Adarna House', contact_person='Rosa Cruz', phone='02-4567-8901', 
                    email='sales@adarna.com.ph', address='Mandaluyong City, Philippines', is_active=True),
        ]
        db.session.add_all(suppliers)
        db.session.commit()
        
        print("Seeding products...")
        products_data = [
            {'isbn': '9789719234567', 'title': 'Noli Me Tangere', 'author': 'Jose Rizal', 'category': 'Fiction', 
             'description': 'Classic Filipino novel', 'supplier_id': 1, 'unit_price': 350.00, 'reorder_level': 10, 'current_stock': 25},
            {'isbn': '9789719234574', 'title': 'El Filibusterismo', 'author': 'Jose Rizal', 'category': 'Fiction', 
             'description': 'Sequel to Noli Me Tangere', 'supplier_id': 1, 'unit_price': 380.00, 'reorder_level': 10, 'current_stock': 20},
            {'isbn': '9789719234581', 'title': 'Mga Kuwento ni Lola Basyang', 'author': 'Severino Reyes', 'category': "Children's Books", 
             'description': 'Classic Filipino children stories', 'supplier_id': 4, 'unit_price': 295.00, 'reorder_level': 15, 'current_stock': 8},
            {'isbn': '9789719234598', 'title': 'Bata, Bata, Pa\'no Ka Ginawa?', 'author': 'Lualhati Bautista', 'category': 'Fiction', 
             'description': 'Contemporary Filipino novel', 'supplier_id': 2, 'unit_price': 320.00, 'reorder_level': 12, 'current_stock': 30},
            {'isbn': '9789719234604', 'title': 'Smaller and Smaller Circles', 'author': 'F.H. Batacan', 'category': 'Fiction', 
             'description': 'Filipino crime novel', 'supplier_id': 2, 'unit_price': 425.00, 'reorder_level': 8, 'current_stock': 5},
            {'isbn': '9789719234611', 'title': 'Ilustrado', 'author': 'Miguel Syjuco', 'category': 'Fiction', 
             'description': 'Man Asian Literary Prize winner', 'supplier_id': 1, 'unit_price': 495.00, 'reorder_level': 10, 'current_stock': 15},
            {'isbn': None, 'title': 'Philippine History: A Comprehensive Guide', 'author': 'Teodoro Agoncillo', 'category': 'History', 
             'description': 'Comprehensive Philippine history book', 'supplier_id': 3, 'unit_price': 550.00, 'reorder_level': 5, 'current_stock': 0},
            {'isbn': None, 'title': 'Basic Mathematics for Filipinos', 'author': 'Various Authors', 'category': 'Educational', 
             'description': 'Math textbook', 'supplier_id': 3, 'unit_price': 285.00, 'reorder_level': 20, 'current_stock': 45},
            {'isbn': '9789719234628', 'title': 'The Woman Who Had Two Navels', 'author': 'Nick Joaquin', 'category': 'Fiction', 
             'description': 'Classic Filipino novel', 'supplier_id': 1, 'unit_price': 365.00, 'reorder_level': 10, 'current_stock': 18},
            {'isbn': '9789719234635', 'title': 'Dekada \'70', 'author': 'Lualhati Bautista', 'category': 'Fiction', 
             'description': 'Historical fiction set in Marcos era', 'supplier_id': 2, 'unit_price': 340.00, 'reorder_level': 12, 'current_stock': 22},
            {'isbn': None, 'title': 'Ang Mga Kaibigan ni Mama Susan', 'author': 'Bob Ong', 'category': 'Non-Fiction', 
             'description': 'Popular Filipino humor book', 'supplier_id': 2, 'unit_price': 250.00, 'reorder_level': 15, 'current_stock': 3},
            {'isbn': None, 'title': 'ABNKKBSNPLAko?!', 'author': 'Bob Ong', 'category': 'Non-Fiction', 
             'description': 'Humorous take on Filipino school life', 'supplier_id': 2, 'unit_price': 220.00, 'reorder_level': 15, 'current_stock': 35},
        ]
        
        for data in products_data:
            product = Product(**data)
            db.session.add(product)
            if data['current_stock'] > 0:
                log = InventoryLog(
                    product_id=product.id,
                    transaction_type='Adjustment',
                    quantity_change=data['current_stock'],
                    previous_stock=0,
                    new_stock=data['current_stock'],
                    notes='Initial stock',
                    created_by=1
                )
                db.session.add(log)
        
        db.session.commit()
        print(f"Created {len(products_data)} products")
        
        print("Seeding purchase orders...")
        # Create some sample POs
        po1 = PurchaseOrder(
            po_number='PO-20250101-0001',
            supplier_id=1,
            order_date=datetime.utcnow() - timedelta(days=15),
            expected_delivery_date=(datetime.utcnow() - timedelta(days=10)).date(),
            status='Delivered',
            total_amount=2000.00,
            notes='Initial order',
            created_by=1
        )
        db.session.add(po1)
        db.session.flush()
        
        # Add PO items
        po_item1 = PurchaseOrderItem(purchase_order_id=po1.id, product_id=1, quantity=10, unit_price=350.00, subtotal=3500.00)
        po_item2 = PurchaseOrderItem(purchase_order_id=po1.id, product_id=2, quantity=10, unit_price=380.00, subtotal=3800.00)
        db.session.add_all([po_item1, po_item2])
        po1.total_amount = 7300.00
        db.session.commit()
        
        print("Seeding sales transactions...")
        # Create sample sales
        for i in range(5):
            sale = Sales(
                transaction_number=f'TXN-2025010{i+1}-000{i+1}',
                transaction_date=datetime.utcnow() - timedelta(days=i),
                customer_name=random.choice(['Juan Dela Cruz', 'Maria Santos', 'Pedro Garcia', None]),
                payment_method=random.choice(['Cash', 'Credit Card', 'GCash']),
                cashier_id=3
            )
            db.session.add(sale)
            db.session.flush()
            
            # Add sales items
            num_items = random.randint(1, 3)
            total = 0
            available_products = [p for p in Product.query.filter(Product.current_stock > 0).all()]
            selected_products = random.sample(available_products, min(num_items, len(available_products)))
            
            for product in selected_products:
                qty = random.randint(1, min(3, product.current_stock))
                subtotal = qty * float(product.unit_price)
                
                item = SalesItem(sales_id=sale.id, product_id=product.id, quantity=qty, 
                               unit_price=float(product.unit_price), subtotal=subtotal)
                db.session.add(item)
                total += subtotal
                
                # Update stock
                prev_stock = product.current_stock
                product.current_stock -= qty
                
                log = InventoryLog(
                    product_id=product.id,
                    transaction_type='Sale',
                    quantity_change=-qty,
                    previous_stock=prev_stock,
                    new_stock=product.current_stock,
                    reference_type='Sales',
                    reference_id=sale.id,
                    notes=f'Sale {sale.transaction_number}',
                    created_by=3
                )
                db.session.add(log)
            
            sale.total_amount = total
        
        db.session.commit()
        
        print("\n✅ Database seeded successfully!")
        print("\n📋 Demo Credentials:")
        print("   Manager:        username: manager  | password: password")
        print("   Inventory Staff: username: staff    | password: password")
        print("   Cashier:        username: cashier  | password: password")
        print("\n🎉 You can now run the application with: python run.py")

if __name__ == '__main__':
    seed_database()
