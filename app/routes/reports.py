"""
Reports module for comprehensive analytics
"""
from flask import Blueprint, render_template
from app import db
from app.models import Product, Sales, PurchaseOrder, Supplier, SalesItem
from app.routes.auth import login_required, role_required
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
@role_required('Manager')
def index():
    """Main reports dashboard."""
    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)
    thirty_days_ago = today - timedelta(days=30)
    
    # Sales reports
    total_sales = db.session.query(func.coalesce(func.sum(Sales.total_amount), 0)).scalar()
    month_sales = db.session.query(func.coalesce(func.sum(Sales.total_amount), 0)).filter(
        func.date(Sales.transaction_date) >= start_of_month
    ).scalar()
    
    # Top products
    top_products = db.session.query(
        Product.title,
        func.sum(SalesItem.quantity).label('total_sold'),
        func.sum(SalesItem.subtotal).label('revenue')
    ).join(SalesItem).join(Sales).filter(
        func.date(Sales.transaction_date) >= thirty_days_ago
    ).group_by(Product.id, Product.title).order_by(func.sum(SalesItem.quantity).desc()).limit(10).all()
    
    # Inventory stats
    total_products = Product.query.filter_by(is_active=True).count()
    low_stock_count = Product.query.filter(Product.is_active == True, Product.current_stock <= Product.reorder_level).count()
    
    # Supplier stats
    active_suppliers = Supplier.query.filter_by(is_active=True).count()
    
    return render_template('reports/index.html',
                         total_sales=float(total_sales),
                         month_sales=float(month_sales),
                         top_products=top_products,
                         total_products=total_products,
                         low_stock_count=low_stock_count,
                         active_suppliers=active_suppliers)
