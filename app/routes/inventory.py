"""
Inventory tracking and low stock alert routes
"""
from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Product, InventoryLog
from app.routes.auth import login_required
from sqlalchemy import or_

bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@bp.route('/')
@login_required
def view_inventory():
    """View complete inventory with stock status indicators."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    stock_filter = request.args.get('stock_filter', 'all', type=str)
    category = request.args.get('category', '', type=str)
    per_page = 20
    
    query = Product.query.filter_by(is_active=True)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.title.like(search_term),
                Product.author.like(search_term),
                Product.isbn.like(search_term)
            )
        )
    
    # Apply category filter
    if category:
        query = query.filter_by(category=category)
    
    # Apply stock status filter
    if stock_filter == 'in_stock':
        query = query.filter(Product.current_stock > Product.reorder_level)
    elif stock_filter == 'low_stock':
        query = query.filter(
            Product.current_stock <= Product.reorder_level,
            Product.current_stock > 0
        )
    elif stock_filter == 'out_of_stock':
        query = query.filter(Product.current_stock == 0)
    
    # Order by stock status (out of stock first, then low stock, then in stock)
    query = query.order_by(
        Product.current_stock.asc(),
        Product.title.asc()
    )
    
    # Paginate results
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all unique categories for filter dropdown
    all_categories = db.session.query(Product.category).filter(
        Product.category.isnot(None),
        Product.category != '',
        Product.is_active == True
    ).distinct().order_by(Product.category).all()
    all_categories = [cat[0] for cat in all_categories]
    
    # Calculate summary statistics
    total_products = Product.query.filter_by(is_active=True).count()
    in_stock_count = Product.query.filter(
        Product.is_active == True,
        Product.current_stock > Product.reorder_level
    ).count()
    low_stock_count = Product.query.filter(
        Product.is_active == True,
        Product.current_stock <= Product.reorder_level,
        Product.current_stock > 0
    ).count()
    out_of_stock_count = Product.query.filter(
        Product.is_active == True,
        Product.current_stock == 0
    ).count()
    
    # Calculate total inventory value
    from sqlalchemy import func
    inventory_value = db.session.query(
        func.coalesce(func.sum(Product.current_stock * Product.unit_price), 0)
    ).filter(Product.is_active == True).scalar()
    
    return render_template('inventory/view.html',
                         products=products,
                         search=search,
                         stock_filter=stock_filter,
                         category=category,
                         all_categories=all_categories,
                         total_products=total_products,
                         in_stock_count=in_stock_count,
                         low_stock_count=low_stock_count,
                         out_of_stock_count=out_of_stock_count,
                         inventory_value=float(inventory_value))

@bp.route('/low-stock-alerts')
@login_required
def low_stock_alerts():
    """Display all low stock and out of stock products."""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Get all products that need attention (low stock or out of stock)
    query = Product.query.filter(
        Product.is_active == True,
        Product.current_stock <= Product.reorder_level
    ).order_by(
        Product.current_stock.asc(),
        Product.title.asc()
    )
    
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Separate into out of stock and low stock
    out_of_stock_products = [p for p in products.items if p.current_stock == 0]
    low_stock_products = [p for p in products.items if p.current_stock > 0]
    
    return render_template('inventory/low_stock_alerts.html',
                         products=products,
                         out_of_stock_products=out_of_stock_products,
                         low_stock_products=low_stock_products)

@bp.route('/api/low-stock-count')
@login_required
def get_low_stock_count():
    """API endpoint to get count of low stock items for notification bell."""
    count = Product.query.filter(
        Product.is_active == True,
        Product.current_stock <= Product.reorder_level
    ).count()
    
    return jsonify({'count': count})

@bp.route('/history')
@login_required
def inventory_history():
    """View complete inventory transaction history."""
    page = request.args.get('page', 1, type=int)
    transaction_type = request.args.get('transaction_type', '', type=str)
    product_id = request.args.get('product_id', 0, type=int)
    per_page = 50
    
    query = InventoryLog.query
    
    # Apply transaction type filter
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    # Apply product filter
    if product_id:
        query = query.filter_by(product_id=product_id)
    
    # Order by most recent first
    query = query.order_by(InventoryLog.created_at.desc())
    
    # Paginate results
    logs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all products for filter dropdown
    products = Product.query.filter_by(is_active=True).order_by(Product.title).all()
    
    return render_template('inventory/history.html',
                         logs=logs,
                         transaction_type=transaction_type,
                         product_id=product_id,
                         products=products)

@bp.route('/report')
@login_required
def inventory_report():
    """Generate comprehensive inventory report."""
    # Get all active products
    products = Product.query.filter_by(is_active=True).order_by(Product.title).all()
    
    # Calculate statistics
    from sqlalchemy import func
    
    total_products = len(products)
    total_items = sum(p.current_stock for p in products)
    total_value = sum(p.current_stock * float(p.unit_price) for p in products)
    
    in_stock = [p for p in products if p.stock_status == 'In Stock']
    low_stock = [p for p in products if p.stock_status == 'Low Stock']
    out_of_stock = [p for p in products if p.stock_status == 'Out of Stock']
    
    # Group by category
    from collections import defaultdict
    by_category = defaultdict(lambda: {'count': 0, 'total_stock': 0, 'total_value': 0})
    
    for product in products:
        cat = product.category or 'Uncategorized'
        by_category[cat]['count'] += 1
        by_category[cat]['total_stock'] += product.current_stock
        by_category[cat]['total_value'] += product.current_stock * float(product.unit_price)
    
    # Convert to sorted list
    category_stats = sorted([
        {
            'category': cat,
            'count': stats['count'],
            'total_stock': stats['total_stock'],
            'total_value': stats['total_value']
        }
        for cat, stats in by_category.items()
    ], key=lambda x: x['total_value'], reverse=True)
    
    return render_template('inventory/report.html',
                         products=products,
                         total_products=total_products,
                         total_items=total_items,
                         total_value=total_value,
                         in_stock_count=len(in_stock),
                         low_stock_count=len(low_stock),
                         out_of_stock_count=len(out_of_stock),
                         in_stock=in_stock,
                         low_stock=low_stock,
                         out_of_stock=out_of_stock,
                         category_stats=category_stats)
