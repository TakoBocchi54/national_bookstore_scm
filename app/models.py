"""
Database models for National Book Store SCM System
"""
from datetime import datetime
from app import db

class User(db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('Manager', 'Inventory Staff', 'Cashier'), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
    
    def has_permission(self, permission):
        """Check if user has specific permission based on role."""
        permissions = {
            'Manager': ['view', 'create', 'edit', 'delete', 'manage_users'],
            'Inventory Staff': ['view', 'create', 'edit', 'manage_inventory', 'manage_po', 'manage_delivery'],
            'Cashier': ['view', 'create_sales']
        }
        return permission in permissions.get(self.role, [])


class Supplier(db.Model):
    """Supplier model for managing book suppliers."""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    contact_person = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    products = db.relationship('Product', back_populates='supplier', lazy='dynamic')
    purchase_orders = db.relationship('PurchaseOrder', back_populates='supplier', lazy='dynamic')
    
    def __repr__(self):
        return f'<Supplier {self.name}>'


class Product(db.Model):
    """Product model for managing book inventory items."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(100), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    reorder_level = db.Column(db.Integer, default=10, nullable=False)
    current_stock = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    supplier = db.relationship('Supplier', back_populates='products')
    purchase_order_items = db.relationship('PurchaseOrderItem', back_populates='product', lazy='dynamic')
    delivery_items = db.relationship('DeliveryItem', back_populates='product', lazy='dynamic')
    sales_items = db.relationship('SalesItem', back_populates='product', lazy='dynamic')
    inventory_logs = db.relationship('InventoryLog', back_populates='product', lazy='dynamic')
    
    def __repr__(self):
        return f'<Product {self.title}>'
    
    @property
    def stock_status(self):
        """Get current stock status."""
        if self.current_stock == 0:
            return 'Out of Stock'
        elif self.current_stock <= self.reorder_level:
            return 'Low Stock'
        else:
            return 'In Stock'
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock."""
        return self.current_stock <= self.reorder_level and self.current_stock > 0
    
    @property
    def is_out_of_stock(self):
        """Check if product is out of stock."""
        return self.current_stock == 0


class PurchaseOrder(db.Model):
    """Purchase Order model for ordering from suppliers."""
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expected_delivery_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum('Pending', 'Approved', 'Ordered', 'Delivered', 'Cancelled'), 
                      default='Pending', nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    supplier = db.relationship('Supplier', back_populates='purchase_orders')
    creator = db.relationship('User', foreign_keys=[created_by])
    items = db.relationship('PurchaseOrderItem', back_populates='purchase_order', 
                           cascade='all, delete-orphan', lazy='dynamic')
    deliveries = db.relationship('Delivery', back_populates='purchase_order', lazy='dynamic')
    
    def __repr__(self):
        return f'<PurchaseOrder {self.po_number}>'
    
    def calculate_total(self):
        """Calculate total amount from line items."""
        total = sum(item.subtotal for item in self.items)
        self.total_amount = total
        return total


class PurchaseOrderItem(db.Model):
    """Line items for purchase orders."""
    __tablename__ = 'purchase_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Relationships
    purchase_order = db.relationship('PurchaseOrder', back_populates='items')
    product = db.relationship('Product', back_populates='purchase_order_items')
    
    def __repr__(self):
        return f'<PurchaseOrderItem PO:{self.purchase_order_id} Product:{self.product_id}>'


class Delivery(db.Model):
    """Delivery model for tracking received purchase orders."""
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    delivery_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.Enum('Partial', 'Complete'), default='Complete', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    received_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    purchase_order = db.relationship('PurchaseOrder', back_populates='deliveries')
    receiver = db.relationship('User', foreign_keys=[received_by])
    items = db.relationship('DeliveryItem', back_populates='delivery', 
                           cascade='all, delete-orphan', lazy='dynamic')
    
    def __repr__(self):
        return f'<Delivery {self.delivery_number}>'


class DeliveryItem(db.Model):
    """Line items for deliveries."""
    __tablename__ = 'delivery_items'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('deliveries.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_received = db.Column(db.Integer, nullable=False)
    
    # Relationships
    delivery = db.relationship('Delivery', back_populates='items')
    product = db.relationship('Product', back_populates='delivery_items')
    
    def __repr__(self):
        return f'<DeliveryItem Delivery:{self.delivery_id} Product:{self.product_id}>'


class Sales(db.Model):
    """Sales transaction model."""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    customer_name = db.Column(db.String(200), nullable=True)
    total_amount = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    payment_method = db.Column(db.Enum('Cash', 'Credit Card', 'Debit Card', 'GCash', 'PayMaya'), 
                               default='Cash', nullable=False)
    cashier_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    cashier = db.relationship('User', foreign_keys=[cashier_id])
    items = db.relationship('SalesItem', back_populates='sale', 
                           cascade='all, delete-orphan', lazy='dynamic')
    
    def __repr__(self):
        return f'<Sales {self.transaction_number}>'
    
    def calculate_total(self):
        """Calculate total amount from line items."""
        total = sum(item.subtotal for item in self.items)
        self.total_amount = total
        return total


class SalesItem(db.Model):
    """Line items for sales transactions."""
    __tablename__ = 'sales_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sales_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Relationships
    sale = db.relationship('Sales', back_populates='items')
    product = db.relationship('Product', back_populates='sales_items')
    
    def __repr__(self):
        return f'<SalesItem Sale:{self.sales_id} Product:{self.product_id}>'


class InventoryLog(db.Model):
    """Audit log for inventory changes."""
    __tablename__ = 'inventory_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    transaction_type = db.Column(db.Enum('Purchase', 'Sale', 'Adjustment', 'Return'), nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)  # Positive for increase, negative for decrease
    previous_stock = db.Column(db.Integer, nullable=False)
    new_stock = db.Column(db.Integer, nullable=False)
    reference_type = db.Column(db.String(50), nullable=True)  # 'Delivery', 'Sales', etc.
    reference_id = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    product = db.relationship('Product', back_populates='inventory_logs')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<InventoryLog Product:{self.product_id} {self.transaction_type}>'
