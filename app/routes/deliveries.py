"""
Delivery tracking routes with automatic stock updates
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Delivery, DeliveryItem, PurchaseOrder, Product, InventoryLog
from app.routes.auth import login_required, role_required
from datetime import datetime

bp = Blueprint('deliveries', __name__, url_prefix='/deliveries')

def generate_delivery_number():
    """Generate unique delivery number."""
    today = datetime.utcnow()
    prefix = f"DEL-{today.strftime('%Y%m%d')}"
    last_del = Delivery.query.filter(Delivery.delivery_number.like(f"{prefix}%")).order_by(Delivery.id.desc()).first()
    new_seq = int(last_del.delivery_number.split('-')[-1]) + 1 if last_del else 1
    return f"{prefix}-{new_seq:04d}"

@bp.route('/')
@login_required
@role_required('Manager', 'Inventory Staff')
def list_deliveries():
    """List all deliveries."""
    page = request.args.get('page', 1, type=int)
    deliveries = Delivery.query.order_by(Delivery.delivery_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('deliveries/list.html', deliveries=deliveries)

@bp.route('/view/<int:delivery_id>')
@login_required
@role_required('Manager', 'Inventory Staff')
def view_delivery(delivery_id):
    """View delivery details."""
    delivery = Delivery.query.get_or_404(delivery_id)
    return render_template('deliveries/view.html', delivery=delivery)

@bp.route('/record/<int:po_id>', methods=['GET', 'POST'])
@login_required
@role_required('Manager', 'Inventory Staff')
def record_delivery(po_id):
    """Record delivery for a PO with automatic stock update."""
    po = PurchaseOrder.query.get_or_404(po_id)
    
    if request.method == 'POST':
        notes = request.form.get('notes', '').strip()
        product_ids = request.form.getlist('product_id[]', type=int)
        quantities = request.form.getlist('quantity_received[]', type=int)
        
        try:
            delivery = Delivery(
                delivery_number=generate_delivery_number(),
                purchase_order_id=po_id,
                delivery_date=datetime.utcnow(),
                status='Complete',
                notes=notes,
                received_by=session.get('user_id', 1)
            )
            db.session.add(delivery)
            db.session.flush()
            
            # Add delivery items and update stock
            for i, prod_id in enumerate(product_ids):
                if quantities[i] > 0:
                    product = Product.query.get(prod_id)
                    prev_stock = product.current_stock
                    product.current_stock += quantities[i]
                    
                    # Create delivery item
                    item = DeliveryItem(delivery_id=delivery.id, product_id=prod_id, quantity_received=quantities[i])
                    db.session.add(item)
                    
                    # Create inventory log
                    log = InventoryLog(
                        product_id=prod_id,
                        transaction_type='Purchase',
                        quantity_change=quantities[i],
                        previous_stock=prev_stock,
                        new_stock=product.current_stock,
                        reference_type='Delivery',
                        reference_id=delivery.id,
                        notes=f'Delivery {delivery.delivery_number}',
                        created_by=session.get('user_id', 1)
                    )
                    db.session.add(log)
            
            # Update PO status
            po.status = 'Delivered'
            db.session.commit()
            
            flash(f'Delivery {delivery.delivery_number} recorded successfully. Stock updated.', 'success')
            return redirect(url_for('deliveries.view_delivery', delivery_id=delivery.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording delivery: {str(e)}', 'error')
    
    return render_template('deliveries/record.html', po=po)
