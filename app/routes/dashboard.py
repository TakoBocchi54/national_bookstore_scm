"""
Dashboard routes for displaying key metrics and overview
"""
from flask import Blueprint, render_template, session
from app.routes.auth import login_required
from app import db
from app.models import Product, Sales, PurchaseOrder, Supplier, Delivery, SalesItem
from sqlalchemy import func, desc
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/')

@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    """Main dashboard with key metrics."""
    
    # Get current date and calculate date ranges
    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)
    thirty_days_ago = today - timedelta(days=30)
    
    # 1. Product Statistics
    total_products = Product.query.filter_by(is_active=True).count()
    low_stock_count = Product.query.filter(
        Product.is_active == True,
        Product.current_stock <= Product.reorder_level,
        Product.current_stock > 0
    ).count()
    out_of_stock_count = Product.query.filter(
        Product.is_active == True,
        Product.current_stock == 0
    ).count()
    in_stock_count = total_products - low_stock_count - out_of_stock_count
    
    # 2. Sales Statistics
    # Today's sales
    today_sales = db.session.query(func.coalesce(func.sum(Sales.total_amount), 0)).filter(
        func.date(Sales.transaction_date) == today
    ).scalar()
    
    # This month's sales
    month_sales = db.session.query(func.coalesce(func.sum(Sales.total_amount), 0)).filter(
        func.date(Sales.transaction_date) >= start_of_month
    ).scalar()
    
    # Total sales count
    total_sales_count = Sales.query.count()
    
    # Recent sales (last 30 days)
    recent_sales = db.session.query(func.coalesce(func.sum(Sales.total_amount), 0)).filter(
        func.date(Sales.transaction_date) >= thirty_days_ago
    ).scalar()
    
    # 3. Purchase Order Statistics
    pending_pos = PurchaseOrder.query.filter(
        PurchaseOrder.status.in_(['Pending', 'Approved', 'Ordered'])
    ).count()
    
    total_pos = PurchaseOrder.query.count()
    
    # Recent deliveries count
    recent_deliveries = Delivery.query.filter(
        func.date(Delivery.delivery_date) >= thirty_days_ago
    ).count()
    
    # 4. Supplier Statistics
    active_suppliers = Supplier.query.filter_by(is_active=True).count()
    
    # 5. Low Stock Products (for alerts)
    low_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.current_stock <= Product.reorder_level
    ).order_by(Product.current_stock.asc()).limit(10).all()
    
    # 6. Recent Sales Transactions
    recent_sales_transactions = Sales.query.order_by(
        Sales.transaction_date.desc()
    ).limit(5).all()
    
    # 7. Top Selling Products (last 30 days)
    top_products = db.session.query(
        Product.title,
        func.sum(SalesItem.quantity).label('total_sold'),
        func.sum(SalesItem.subtotal).label('total_revenue')
    ).join(SalesItem).join(Sales).filter(
        func.date(Sales.transaction_date) >= thirty_days_ago
    ).group_by(Product.id, Product.title).order_by(
        desc('total_sold')
    ).limit(5).all()
    
    # 8. Pending Purchase Orders
    pending_purchase_orders = PurchaseOrder.query.filter(
        PurchaseOrder.status.in_(['Pending', 'Approved', 'Ordered'])
    ).order_by(PurchaseOrder.order_date.desc()).limit(5).all()
    
    # Calculate total inventory value
    inventory_value = db.session.query(
        func.coalesce(func.sum(Product.current_stock * Product.unit_price), 0)
    ).filter(Product.is_active == True).scalar()
    
    return render_template('dashboard/index.html',
                         total_products=total_products,
                         in_stock_count=in_stock_count,
                         low_stock_count=low_stock_count,
                         out_of_stock_count=out_of_stock_count,
                         today_sales=float(today_sales),
                         month_sales=float(month_sales),
                         recent_sales=float(recent_sales),
                         total_sales_count=total_sales_count,
                         pending_pos=pending_pos,
                         total_pos=total_pos,
                         recent_deliveries=recent_deliveries,
                         active_suppliers=active_suppliers,
                         low_stock_products=low_stock_products,
                         recent_sales_transactions=recent_sales_transactions,
                         top_products=top_products,
                         pending_purchase_orders=pending_purchase_orders,
                         inventory_value=float(inventory_value))
