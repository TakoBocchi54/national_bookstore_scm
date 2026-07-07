"""
Product management routes - CRUD operations with hybrid category system
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Product, Supplier, InventoryLog
from app.routes.auth import login_required, role_required
from sqlalchemy import or_, func
from datetime import datetime

bp = Blueprint('products', __name__, url_prefix='/products')

# Predefined category list for dropdown
PRODUCT_CATEGORIES = [
    'Fiction',
    'Non-Fiction',
    'Biography',
    'Self-Help',
    'Business',
    'Technology',
    'Science',
    'History',
    'Children\'s Books',
    'Young Adult',
    'Comics & Graphic Novels',
    'Educational',
    'Reference',
    'Poetry',
    'Arts & Photography'
]

@bp.route('/')
@login_required
def list_products():
    """List all products with search and filter."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category = request.args.get('category', '', type=str)
    status = request.args.get('status', 'all', type=str)
    supplier_id = request.args.get('supplier_id', 0, type=int)
    per_page = 20
    
    query = Product.query
    
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
    
    # Apply supplier filter
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)
    
    # Apply status filter
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    elif status == 'low_stock':
        query = query.filter(
            Product.is_active == True,
            Product.current_stock <= Product.reorder_level,
            Product.current_stock > 0
        )
    elif status == 'out_of_stock':
        query = query.filter(
            Product.is_active == True,
            Product.current_stock == 0
        )
    
    # Order by title
    query = query.order_by(Product.title.asc())
    
    # Paginate results
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all unique categories for filter dropdown
    all_categories = db.session.query(Product.category).filter(
        Product.category.isnot(None),
        Product.category != ''
    ).distinct().order_by(Product.category).all()
    all_categories = [cat[0] for cat in all_categories]
    
    # Get all suppliers for filter
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
    
    return render_template('products/list.html',
                         products=products,
                         search=search,
                         category=category,
                         status=status,
                         supplier_id=supplier_id,
                         all_categories=all_categories,
                         suppliers=suppliers)

@bp.route('/view/<int:product_id>')
@login_required
def view_product(product_id):
    """View detailed product information."""
    product = Product.query.get_or_404(product_id)
    
    # Get inventory logs
    inventory_logs = InventoryLog.query.filter_by(product_id=product_id).order_by(
        InventoryLog.created_at.desc()
    ).limit(20).all()
    
    return render_template('products/view.html',
                         product=product,
                         inventory_logs=inventory_logs)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Manager', 'Inventory Staff')
def add_product():
    """Add a new product with hybrid category system."""
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
    
    # Get supplier_id from query parameter if provided
    preselected_supplier = request.args.get('supplier_id', 0, type=int)
    
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        
        # Hybrid category system
        category_select = request.form.get('category_select', '').strip()
        category_custom = request.form.get('category_custom', '').strip()
        category = category_custom if category_custom else category_select
        
        description = request.form.get('description', '').strip()
        supplier_id = request.form.get('supplier_id', type=int)
        unit_price = request.form.get('unit_price', type=float)
        reorder_level = request.form.get('reorder_level', 10, type=int)
        current_stock = request.form.get('current_stock', 0, type=int)
        
        # Validation
        if not title:
            flash('Product title is required.', 'error')
            return render_template('products/form.html', product=None, 
                                 suppliers=suppliers, categories=PRODUCT_CATEGORIES,
                                 preselected_supplier=preselected_supplier)
        
        if not supplier_id:
            flash('Please select a supplier.', 'error')
            return render_template('products/form.html', product=None, 
                                 suppliers=suppliers, categories=PRODUCT_CATEGORIES,
                                 preselected_supplier=preselected_supplier)
        
        if unit_price is None or unit_price < 0:
            flash('Please enter a valid unit price.', 'error')
            return render_template('products/form.html', product=None, 
                                 suppliers=suppliers, categories=PRODUCT_CATEGORIES,
                                 preselected_supplier=preselected_supplier)
        
        # Check for duplicate ISBN if provided
        if isbn:
            existing = Product.query.filter_by(isbn=isbn).first()
            if existing:
                flash(f'Product with ISBN "{isbn}" already exists.', 'error')
                return render_template('products/form.html', product=None, 
                                     suppliers=suppliers, categories=PRODUCT_CATEGORIES,
                                     preselected_supplier=preselected_supplier)
        
        # Create new product
        product = Product(
            isbn=isbn if isbn else None,
            title=title,
            author=author if author else None,
            category=category if category else None,
            description=description if description else None,
            supplier_id=supplier_id,
            unit_price=unit_price,
            reorder_level=reorder_level,
            current_stock=current_stock,
            is_active=True
        )
        
        try:
            db.session.add(product)
            db.session.flush()  # Get product ID
            
            # Create initial inventory log if stock > 0
            if current_stock > 0:
                log = InventoryLog(
                    product_id=product.id,
                    transaction_type='Adjustment',
                    quantity_change=current_stock,
                    previous_stock=0,
                    new_stock=current_stock,
                    notes='Initial stock',
                    created_by=request.cookies.get('user_id', 1)
                )
                db.session.add(log)
            
            db.session.commit()
            flash(f'Product "{title}" has been added successfully.', 'success')
            return redirect(url_for('products.view_product', product_id=product.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'error')
            return render_template('products/form.html', product=None, 
                                 suppliers=suppliers, categories=PRODUCT_CATEGORIES,
                                 preselected_supplier=preselected_supplier)
    
    return render_template('products/form.html', product=None, 
                         suppliers=suppliers, categories=PRODUCT_CATEGORIES,
                         preselected_supplier=preselected_supplier)

@bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required('Manager', 'Inventory Staff')
def edit_product(product_id):
    """Edit an existing product."""
    product = Product.query.get_or_404(product_id)
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
    
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        
        # Hybrid category system
        category_select = request.form.get('category_select', '').strip()
        category_custom = request.form.get('category_custom', '').strip()
        category = category_custom if category_custom else category_select
        
        description = request.form.get('description', '').strip()
        supplier_id = request.form.get('supplier_id', type=int)
        unit_price = request.form.get('unit_price', type=float)
        reorder_level = request.form.get('reorder_level', type=int)
        is_active = request.form.get('is_active') == 'on'
        
        # Validation
        if not title:
            flash('Product title is required.', 'error')
            return render_template('products/form.html', product=product, 
                                 suppliers=suppliers, categories=PRODUCT_CATEGORIES)
        
        if not supplier_id:
            flash('Please select a supplier.', 'error')
            return render_template('products/form.html', product=product, 
                                 suppliers=suppliers, categories=PRODUCT_CATEGORIES)
        
        if unit_price is None or unit_price < 0:
            flash('Please enter a valid unit price.', 'error')
            return render_template('products/form.html', product=product, 
                                 suppliers=suppliers, categories=PRODUCT_CATEGORIES)
        
        # Check for duplicate ISBN (excluding current product)
        if isbn:
            existing = Product.query.filter(
                Product.isbn == isbn,
                Product.id != product_id
            ).first()
            if existing:
                flash(f'Another product with ISBN "{isbn}" already exists.', 'error')
                return render_template('products/form.html', product=product, 
                                     suppliers=suppliers, categories=PRODUCT_CATEGORIES)
        
        # Update product
        product.isbn = isbn if isbn else None
        product.title = title
        product.author = author if author else None
        product.category = category if category else None
        product.description = description if description else None
        product.supplier_id = supplier_id
        product.unit_price = unit_price
        product.reorder_level = reorder_level
        product.is_active = is_active
        
        try:
            db.session.commit()
            flash(f'Product "{title}" has been updated successfully.', 'success')
            return redirect(url_for('products.view_product', product_id=product.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'error')
            return render_template('products/form.html', product=product, 
                                 suppliers=suppliers, categories=PRODUCT_CATEGORIES)
    
    return render_template('products/form.html', product=product, 
                         suppliers=suppliers, categories=PRODUCT_CATEGORIES)

@bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
@role_required('Manager')
def delete_product(product_id):
    """Delete a product (Manager only)."""
    product = Product.query.get_or_404(product_id)
    
    # Check if product has sales
    from app.models import SalesItem
    sales_count = SalesItem.query.filter_by(product_id=product_id).count()
    if sales_count > 0:
        flash(f'Cannot delete product "{product.title}" because it has {sales_count} associated sales transactions.', 'error')
        return redirect(url_for('products.view_product', product_id=product_id))
    
    try:
        title = product.title
        db.session.delete(product)
        db.session.commit()
        flash(f'Product "{title}" has been deleted successfully.', 'success')
        return redirect(url_for('products.list_products'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
        return redirect(url_for('products.view_product', product_id=product_id))

@bp.route('/adjust-stock/<int:product_id>', methods=['POST'])
@login_required
@role_required('Manager', 'Inventory Staff')
def adjust_stock(product_id):
    """Manual stock adjustment."""
    product = Product.query.get_or_404(product_id)
    
    adjustment = request.form.get('adjustment', 0, type=int)
    notes = request.form.get('notes', '').strip()
    
    if adjustment == 0:
        flash('Please enter a valid adjustment amount.', 'error')
        return redirect(url_for('products.view_product', product_id=product_id))
    
    previous_stock = product.current_stock
    new_stock = previous_stock + adjustment
    
    if new_stock < 0:
        flash('Stock adjustment would result in negative stock. Operation cancelled.', 'error')
        return redirect(url_for('products.view_product', product_id=product_id))
    
    try:
        product.current_stock = new_stock
        
        # Create inventory log
        log = InventoryLog(
            product_id=product_id,
            transaction_type='Adjustment',
            quantity_change=adjustment,
            previous_stock=previous_stock,
            new_stock=new_stock,
            notes=notes if notes else 'Manual adjustment',
            created_by=request.cookies.get('user_id', 1)
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Stock adjusted successfully. New stock: {new_stock}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adjusting stock: {str(e)}', 'error')
    
    return redirect(url_for('products.view_product', product_id=product_id))

@bp.route('/api/search')
@login_required
def api_search():
    """API endpoint for product search (for AJAX)."""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    search_term = f"%{query}%"
    products = Product.query.filter(
        Product.is_active == True,
        or_(
            Product.title.like(search_term),
            Product.author.like(search_term),
            Product.isbn.like(search_term)
        )
    ).limit(10).all()
    
    results = [{
        'id': p.id,
        'title': p.title,
        'author': p.author,
        'isbn': p.isbn,
        'unit_price': float(p.unit_price),
        'current_stock': p.current_stock,
        'stock_status': p.stock_status
    } for p in products]
    
    return jsonify(results)
