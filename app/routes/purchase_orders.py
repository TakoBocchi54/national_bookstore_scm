"""
Purchase Order management routes with auto-approval workflow
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import PurchaseOrder, PurchaseOrderItem, Product, Supplier
from app.routes.auth import login_required, role_required
from datetime import datetime, timedelta

bp = Blueprint('purchase_orders', __name__, url_prefix='/purchase-orders')

def generate_po_number():
    """Generate unique PO number."""
    today = datetime.utcnow()
    prefix = f"PO-{today.strftime('%Y%m%d')}"
    
    # Find last PO number for today
    last_po = PurchaseOrder.query.filter(
        PurchaseOrder.po_number.like(f"{prefix}%")
    ).order_by(PurchaseOrder.id.desc()).first()
    
    if last_po:
        # Extract sequence number and increment
        last_seq = int(last_po.po_number.split('-')[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    
    return f"{prefix}-{new_seq:04d}"

@bp.route('/')
@login_required
@role_required('Manager', 'Inventory Staff')
def list_pos():
    """List all purchase orders."""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '', type=str)
    supplier_id = request.args.get('supplier_id', 0, type=int)
    per_page = 20
    
    query = PurchaseOrder.query
    
    # Apply status filter
    if status:
        query = query.filter_by(status=status)
    
    # Apply supplier filter
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)
    
    # Order by most recent first
    query = query.order_by(PurchaseOrder.order_date.desc())
    
    # Paginate
    pos = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get suppliers for filter
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
    
    return render_template('purchase_orders/list.html',
                         pos=pos,
                         status=status,
                         supplier_id=supplier_id,
                         suppliers=suppliers)

@bp.route('/view/<int:po_id>')
@login_required
@role_required('Manager', 'Inventory Staff')
def view_po(po_id):
    """View purchase order details."""
    po = PurchaseOrder.query.get_or_404(po_id)
    return render_template('purchase_orders/view.html', po=po)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Manager', 'Inventory Staff')
def create_po():
    """Create new purchase order."""
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
    products = Product.query.filter_by(is_active=True).order_by(Product.title).all()
    product_id = request.args.get('product_id', 0, type=int)
    preselected_product = Product.query.get(product_id) if product_id else None
    
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id', type=int)
        expected_delivery_date = request.form.get('expected_delivery_date')
        notes = request.form.get('notes', '').strip()
        
        # Get line items
        product_ids = request.form.getlist('product_id[]', type=int)
        quantities = request.form.getlist('quantity[]', type=int)
        unit_prices = request.form.getlist('unit_price[]', type=float)
        
        # Validation
        if not supplier_id:
            flash('Please select a supplier.', 'error')
            return redirect(url_for('purchase_orders.create_po'))
        
        if not product_ids or not any(q > 0 for q in quantities):
            flash('Please add at least one product with valid quantity.', 'error')
            return redirect(url_for('purchase_orders.create_po'))
        
        try:
            # Create PO
            po = PurchaseOrder(
                po_number=generate_po_number(),
                supplier_id=supplier_id,
                order_date=datetime.utcnow(),
                expected_delivery_date=datetime.strptime(expected_delivery_date, '%Y-%m-%d').date() if expected_delivery_date else None,
                status='Approved',  # Auto-approve
                notes=notes,
                created_by=session.get('user_id', 1)
            )
            db.session.add(po)
            db.session.flush()
            
            # Add line items
            total_amount = 0
            for i, prod_id in enumerate(product_ids):
                if quantities[i] > 0:
                    subtotal = quantities[i] * unit_prices[i]
                    item = PurchaseOrderItem(
                        purchase_order_id=po.id,
                        product_id=prod_id,
                        quantity=quantities[i],
                        unit_price=unit_prices[i],
                        subtotal=subtotal
                    )
                    db.session.add(item)
                    total_amount += subtotal
            
            po.total_amount = total_amount
            db.session.commit()
            
            flash(f'Purchase Order {po.po_number} created and approved successfully.', 'success')
            return redirect(url_for('purchase_orders.view_po', po_id=po.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating purchase order: {str(e)}', 'error')
            return redirect(url_for('purchase_orders.create_po'))
    
    return render_template('purchase_orders/form.html',
                         po=None,
                         suppliers=suppliers,
                         products=products,
                         preselected_product=preselected_product)

@bp.route('/update-status/<int:po_id>', methods=['POST'])
@login_required
@role_required('Manager', 'Inventory Staff')
def update_status(po_id):
    """Update PO status."""
    po = PurchaseOrder.query.get_or_404(po_id)
    new_status = request.form.get('status')
    
    if new_status in ['Pending', 'Approved', 'Ordered', 'Delivered', 'Cancelled']:
        po.status = new_status
        db.session.commit()
        flash(f'Purchase Order {po.po_number} status updated to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('purchase_orders.view_po', po_id=po_id))

@bp.route('/delete/<int:po_id>', methods=['POST'])
@login_required
@role_required('Manager')
def delete_po(po_id):
    """Delete purchase order (Manager only)."""
    po = PurchaseOrder.query.get_or_404(po_id)
    
    # Check if PO has deliveries
    if po.deliveries.count() > 0:
        flash(f'Cannot delete PO {po.po_number} because it has associated deliveries.', 'error')
        return redirect(url_for('purchase_orders.view_po', po_id=po_id))
    
    try:
        po_number = po.po_number
        db.session.delete(po)
        db.session.commit()
        flash(f'Purchase Order {po_number} deleted successfully.', 'success')
        return redirect(url_for('purchase_orders.list_pos'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting purchase order: {str(e)}', 'error')
        return redirect(url_for('purchase_orders.view_po', po_id=po_id))
