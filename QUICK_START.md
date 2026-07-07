# Quick Start Guide

## Installation & Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database
Create MySQL database:
```sql
CREATE DATABASE national_bookstore_scm;
```

Update `.env` (or edit `config.py` directly):
```
DATABASE_URL=mysql+pymysql://root:password@localhost/national_bookstore_scm
```

### 3. Seed Database
```bash
python seed_data.py
```

### 4. Run Application
```bash
python run.py
```

Visit: http://localhost:5000

## Login Credentials

| Role | Username | Password |
|------|----------|----------|
| **Manager** | `manager` | `password` |
| **Inventory Staff** | `staff` | `password` |
| **Cashier** | `cashier` | `password` |

## Quick Test Scenarios

### Scenario 1: View Dashboard (All Roles)
1. Login with any account
2. View key metrics and alerts
3. Check low stock notifications

### Scenario 2: Create Purchase Order (Manager/Staff)
1. Login as `staff` or `manager`
2. Go to Procurement → Purchase Orders
3. Click "Create PO"
4. Select supplier and add products
5. Submit (auto-approved)

### Scenario 3: Record Delivery (Manager/Staff)
1. View a purchase order
2. Click "Record Delivery"
3. Confirm quantities received
4. Submit (stock automatically increases)

### Scenario 4: Make a Sale (All Roles)
1. Login (any role can make sales)
2. Go to Sales → New Sale
3. Select products and quantities
4. Complete sale (stock automatically decreases)

### Scenario 5: Check Inventory (All Roles)
1. Go to Inventory
2. View stock levels with color coding
3. Check low stock alerts
4. Generate inventory report

## Key Features Checklist

✅ **Authentication**
- Session-based login
- Role-based access control
- Auto-logout on browser close

✅ **Supplier Management**
- CRUD operations
- Contact tracking
- View associated products

✅ **Product Management**
- Hybrid category system (dropdown + custom)
- ISBN tracking
- Stock status indicators
- Manual stock adjustments

✅ **Inventory Tracking**
- Real-time stock levels
- Color-coded status (In Stock/Low/Out)
- Comprehensive reports
- Inventory value calculation

✅ **Purchase Orders**
- Auto-approval workflow
- Line-by-line items
- Automatic PO numbering

✅ **Deliveries**
- Link to PO
- Automatic stock increase
- Inventory audit trail

✅ **Sales**
- Line-by-line entry
- Automatic stock decrease
- Multiple payment methods
- Receipt generation

✅ **Low Stock Alerts**
- Dashboard notifications
- Notification bell with badge
- Dedicated alerts page

✅ **Reports**
- Sales analytics
- Top products
- Inventory reports
- Print-friendly

## Architecture Overview

```
Flask App
├── Authentication Layer (Session-based)
├── Authorization Layer (Role decorators)
├── Business Logic (Routes)
│   ├── Dashboard
│   ├── Suppliers
│   ├── Products
│   ├── Inventory
│   ├── Purchase Orders
│   ├── Deliveries
│   ├── Sales
│   └── Reports
├── Data Layer (SQLAlchemy Models)
└── Presentation Layer (Jinja2 Templates)
```

## Database Schema

**Core Tables:**
- `users` - System users
- `suppliers` - Book suppliers
- `products` - Inventory items
- `purchase_orders` - PO headers
- `purchase_order_items` - PO line items
- `deliveries` - Delivery receipts
- `delivery_items` - Delivery line items
- `sales` - Sales headers
- `sales_items` - Sales line items
- `inventory_logs` - Audit trail

## Business Logic

### Automatic Stock Updates
- **Delivery**: `product.current_stock += delivery_qty`
- **Sale**: `product.current_stock -= sale_qty`
- **Manual Adjustment**: `product.current_stock += adjustment`

### Low Stock Trigger
```python
if product.current_stock <= product.reorder_level:
    # Trigger low stock alert
```

### Stock Status
- **In Stock**: `current_stock > reorder_level`
- **Low Stock**: `current_stock ≤ reorder_level AND current_stock > 0`
- **Out of Stock**: `current_stock = 0`

## Troubleshooting

### Database Connection Error
```bash
# Check MySQL is running
mysql -u root -p

# Verify database exists
SHOW DATABASES;

# Update config.py with correct credentials
```

### Import Error
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
```python
# Edit run.py
app.run(port=5001)  # Change port
```

## Next Steps

1. ✅ Test all user roles
2. ✅ Create sample data for your scenario
3. ✅ Customize categories in `products.py`
4. ✅ Add more suppliers
5. ✅ Configure email notifications (future)
6. ✅ Set up backup procedures

## Support

For issues or questions:
1. Check README.md for detailed documentation
2. Review error messages in terminal
3. Check MySQL logs for database issues
4. Verify all dependencies are installed

---

**System Ready!** 🎉
Start with `python run.py` and login as `manager` / `password`
