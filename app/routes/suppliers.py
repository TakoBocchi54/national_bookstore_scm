"""
Supplier management routes - CRUD operations for suppliers
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Supplier, Product
from app.routes.auth import login_required, role_required
from sqlalchemy import or_

bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

@bp.route('/')
@login_required
def list_suppliers():
    """List all suppliers with search and filter."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status = request.args.get('status', 'all', type=str)
    per_page = 20
    
    query = Supplier.query
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Supplier.name.like(search_term),
                Supplier.contact_person.like(search_term),
                Supplier.email.like(search_term)
            )
        )
    
    # Apply status filter
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    # Order by name
    query = query.order_by(Supplier.name.asc())
    
    # Paginate results
    suppliers = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('suppliers/list.html',
                         suppliers=suppliers,
                         search=search,
                         status=status)

@bp.route('/view/<int:supplier_id>')
@login_required
def view_supplier(supplier_id):
    """View detailed supplier information."""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # Get products from this supplier
    products = Product.query.filter_by(supplier_id=supplier_id).order_by(Product.title.asc()).all()
    
    # Get purchase orders from this supplier
    from app.models import PurchaseOrder
    purchase_orders = PurchaseOrder.query.filter_by(supplier_id=supplier_id).order_by(
        PurchaseOrder.order_date.desc()
    ).limit(10).all()
    
    return render_template('suppliers/view.html',
                         supplier=supplier,
                         products=products,
                         purchase_orders=purchase_orders)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Manager', 'Inventory Staff')
def add_supplier():
    """Add a new supplier."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        
        # Validation
        if not name:
            flash('Supplier name is required.', 'error')
            return render_template('suppliers/form.html', supplier=None)
        
        # Check for duplicate supplier name
        existing = Supplier.query.filter_by(name=name).first()
        if existing:
            flash(f'Supplier "{name}" already exists.', 'error')
            return render_template('suppliers/form.html', supplier=None)
        
        # Create new supplier
        supplier = Supplier(
            name=name,
            contact_person=contact_person if contact_person else None,
            phone=phone if phone else None,
            email=email if email else None,
            address=address if address else None,
            is_active=True
        )
        
        try:
            db.session.add(supplier)
            db.session.commit()
            flash(f'Supplier "{name}" has been added successfully.', 'success')
            return redirect(url_for('suppliers.view_supplier', supplier_id=supplier.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding supplier: {str(e)}', 'error')
            return render_template('suppliers/form.html', supplier=None)
    
    return render_template('suppliers/form.html', supplier=None)

@bp.route('/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
@role_required('Manager', 'Inventory Staff')
def edit_supplier(supplier_id):
    """Edit an existing supplier."""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        # Validation
        if not name:
            flash('Supplier name is required.', 'error')
            return render_template('suppliers/form.html', supplier=supplier)
        
        # Check for duplicate supplier name (excluding current supplier)
        existing = Supplier.query.filter(
            Supplier.name == name,
            Supplier.id != supplier_id
        ).first()
        if existing:
            flash(f'Another supplier with name "{name}" already exists.', 'error')
            return render_template('suppliers/form.html', supplier=supplier)
        
        # Update supplier
        supplier.name = name
        supplier.contact_person = contact_person if contact_person else None
        supplier.phone = phone if phone else None
        supplier.email = email if email else None
        supplier.address = address if address else None
        supplier.is_active = is_active
        
        try:
            db.session.commit()
            flash(f'Supplier "{name}" has been updated successfully.', 'success')
            return redirect(url_for('suppliers.view_supplier', supplier_id=supplier.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating supplier: {str(e)}', 'error')
            return render_template('suppliers/form.html', supplier=supplier)
    
    return render_template('suppliers/form.html', supplier=supplier)

@bp.route('/delete/<int:supplier_id>', methods=['POST'])
@login_required
@role_required('Manager')
def delete_supplier(supplier_id):
    """Delete a supplier (Manager only)."""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # Check if supplier has products
    product_count = Product.query.filter_by(supplier_id=supplier_id).count()
    if product_count > 0:
        flash(f'Cannot delete supplier "{supplier.name}" because it has {product_count} associated products.', 'error')
        return redirect(url_for('suppliers.view_supplier', supplier_id=supplier_id))
    
    # Check if supplier has purchase orders
    from app.models import PurchaseOrder
    po_count = PurchaseOrder.query.filter_by(supplier_id=supplier_id).count()
    if po_count > 0:
        flash(f'Cannot delete supplier "{supplier.name}" because it has {po_count} associated purchase orders.', 'error')
        return redirect(url_for('suppliers.view_supplier', supplier_id=supplier_id))
    
    try:
        name = supplier.name
        db.session.delete(supplier)
        db.session.commit()
        flash(f'Supplier "{name}" has been deleted successfully.', 'success')
        return redirect(url_for('suppliers.list_suppliers'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting supplier: {str(e)}', 'error')
        return redirect(url_for('suppliers.view_supplier', supplier_id=supplier_id))

@bp.route('/toggle-status/<int:supplier_id>', methods=['POST'])
@login_required
@role_required('Manager', 'Inventory Staff')
def toggle_status(supplier_id):
    """Toggle supplier active status."""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    try:
        supplier.is_active = not supplier.is_active
        db.session.commit()
        status = 'activated' if supplier.is_active else 'deactivated'
        flash(f'Supplier "{supplier.name}" has been {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating supplier status: {str(e)}', 'error')
    
    return redirect(url_for('suppliers.view_supplier', supplier_id=supplier_id))
