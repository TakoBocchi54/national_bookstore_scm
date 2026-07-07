# National Book Store - Inventory & Supply Chain Management System

A comprehensive web-based inventory and supply chain management system built with Flask, MySQL, and Bootstrap 5. Designed specifically for National Book Store to manage suppliers, products, inventory, purchase orders, deliveries, and sales transactions.

## 🎯 Features

### Authentication & Authorization
- **Session-based authentication** with automatic logout on browser close
- **Role-based access control** with three user roles:
  - **Manager**: Full system access (CRUD all modules, view reports)
  - **Inventory Staff**: Manage inventory, POs, and deliveries
  - **Cashier**: Record sales transactions only
- **Secure password hashing** using SHA-256

### Supplier Management
- Complete CRUD operations for suppliers
- Contact information management
- Active/inactive status tracking
- View associated products and purchase orders
- Search and filter capabilities

### Product Management
- **Hybrid category system**: Select from 15 predefined categories or enter custom categories
- ISBN tracking (optional)
- Author, title, and description fields
- Unit pricing and reorder level configuration
- Stock status indicators (In Stock, Low Stock, Out of Stock)
- Manual stock adjustment with audit logging
- Complete inventory history tracking

### Inventory Tracking
- Real-time stock level monitoring
- Color-coded status indicators
- Multi-filter search (status, category, supplier)
- Total inventory value calculation
- Comprehensive inventory reports with category breakdown
- Print-friendly report generation

### Low Stock Alert System
- **Dashboard alerts** for products at or below reorder level
- **Notification bell** with dynamic badge count
- Separate views for out-of-stock and low-stock items
- Quick access to create purchase orders

### Purchase Order Management
- Simple workflow: Create → Auto-approve → Order → Delivered
- Line-by-line item entry
- Automatic PO number generation
- Expected delivery date tracking
- Status management
- Total amount calculation

### Delivery Tracking
- Link deliveries to purchase orders
- **Automatic stock increase** upon delivery recording
- Delivery date and notes tracking
- Automatic inventory log creation
- PO status update to "Delivered"

### Sales Transaction
- Line-by-line sales entry
- **Automatic stock decrease** upon sale
- Multiple payment methods (Cash, Credit Card, Debit Card, GCash, PayMaya)
- Customer name tracking (optional)
- Real-time stock validation
- Automatic inventory log creation

### Dashboard & Reports
- Key metrics: Today's sales, monthly sales, inventory value
- Stock status overview
- Recent transactions display
- Top selling products (last 30 days)
- Low stock alerts
- Sales and inventory reports (Manager only)

### Data Visibility & Security
- All roles can view all data
- Edit/delete permissions based on role
- Managers have full control
- Inventory staff can manage procurement
- Cashiers limited to sales operations

## 🛠 Technology Stack

- **Backend**: Python Flask 3.0
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Template Engine**: Jinja2
- **Database Driver**: PyMySQL

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd national_bookstore_scm
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   
   Create a MySQL database:
   ```sql
   CREATE DATABASE national_bookstore_scm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
   
   Copy `.env.example` to `.env` and update database credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   ```
   DATABASE_URL=mysql+pymysql://your_username:your_password@localhost/national_bookstore_scm
   SECRET_KEY=your-secret-key-here
   ```

5. **Seed the database**
   ```bash
   python seed_data.py
   ```
   
   This will create:
   - Database tables
   - Sample users (3 roles)
   - Sample suppliers (4 suppliers)
   - Sample products (12 books)
   - Sample purchase orders
   - Sample sales transactions

6. **Run the application**
   ```bash
   python run.py
   ```
   
   Access the application at: `http://localhost:5000`

## 👥 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Manager | `manager` | `password` |
| Inventory Staff | `staff` | `password` |
| Cashier | `cashier` | `password` |

## 📁 Project Structure

```
national_bookstore_scm/
├── app/
│   ├── __init__.py           # App factory
│   ├── models.py             # Database models
│   ├── routes/
│   │   ├── auth.py           # Authentication
│   │   ├── dashboard.py      # Dashboard
│   │   ├── suppliers.py      # Supplier management
│   │   ├── products.py       # Product management
│   │   ├── inventory.py      # Inventory tracking
│   │   ├── purchase_orders.py
│   │   ├── deliveries.py
│   │   ├── sales.py
│   │   └── reports.py
│   ├── templates/            # Jinja2 templates
│   └── static/               # CSS, JS, images
├── config.py                 # Configuration
├── seed_data.py             # Database seeder
├── requirements.txt         # Dependencies
├── run.py                   # Application entry point
└── README.md
```

## 🎨 UI/UX Features

- **National Book Store branding** with crimson red (#DC143C) accent color
- **Responsive design** works on desktop, tablet, and mobile
- **Professional appearance** with clean, modern interface
- **Flash messages** for user feedback
- **Auto-hiding notifications** after 5 seconds
- **Print-friendly reports**
- **Color-coded status indicators**
- **Icon-based navigation**

## 🔄 Business Rules

1. **Sales automatically decrease inventory**
2. **Deliveries automatically increase inventory**
3. **Low stock alert** triggers when `current_stock ≤ reorder_level`
4. **Stock status**:
   - "In Stock": `current_stock > reorder_level`
   - "Low Stock": `current_stock ≤ reorder_level` AND `current_stock > 0`
   - "Out of Stock": `current_stock = 0`
5. **Purchase orders** are auto-approved upon creation
6. **All transactions** create audit logs in inventory history

## 📊 Database Schema

### Core Tables
- `users` - System users with role-based access
- `suppliers` - Book suppliers
- `products` - Book inventory items
- `purchase_orders` - Purchase order headers
- `purchase_order_items` - PO line items
- `deliveries` - Delivery receipts
- `delivery_items` - Delivery line items
- `sales` - Sales transaction headers
- `sales_items` - Sales line items
- `inventory_logs` - Audit trail for all stock changes

## 🔒 Security Features

- Password hashing (SHA-256)
- Session-based authentication
- Role-based authorization decorators
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)
- CSRF protection ready (can be enhanced with Flask-WTF)

## 🐛 Troubleshooting

### Database Connection Error
- Verify MySQL is running
- Check database credentials in `.env`
- Ensure database exists

### Import Errors
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Port Already in Use
- Change port in `run.py`: `app.run(port=5001)`

## 📝 License

This project is developed for National Book Store. All rights reserved.

## 👨‍💻 Developer Notes

### Adding New Users
```python
from app import create_app, db
from app.models import User
from app.routes.auth import hash_password

app = create_app()
with app.app_context():
    user = User(
        username='newuser',
        password=hash_password('password123'),
        full_name='New User',
        role='Cashier',
        email='newuser@nbs.com',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
```

### Database Migrations
For schema changes, consider using Flask-Migrate:
```bash
pip install Flask-Migrate
```

## 🎯 Future Enhancements

- [ ] Advanced reporting with charts (Chart.js)
- [ ] Export reports to PDF/Excel
- [ ] Email notifications for low stock
- [ ] Barcode scanning support
- [ ] Multi-branch support
- [ ] Advanced user management
- [ ] Backup and restore functionality
- [ ] API endpoints for mobile app integration

## 📞 Support

For issues or questions, please contact the development team.

---

**National Book Store** - Inventory & Supply Chain Management System v1.0
