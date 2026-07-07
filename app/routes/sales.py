"""
Sales transaction routes with automatic stock reduction
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Sales, SalesItem, Product, InventoryLog
from app.routes.auth import login_required
from datetime import datetime

bp = Blueprint('sales', __name__, url_prefix='/sales')

def generate_transaction_number():
    """Generate unique transaction number."""
    today = datetime.utcnow()
    prefix = f"TXN-{today.strftime('%Y%m%d')}"
    last_txn = Sales.query.filter(Sales.transaction_number.like(f"{prefix}%")).order_by(Sales.id.desc()).first()
    new_seq = int(last_txn.transaction_number.split('-')[-1]) + 1 if last_txn else 1
    return f"{prefix}-{new_seq:04d}"

@bp.route('/')
@login_required
def list_sales():
    """List all sales transactions."""
    page = request.args.get('page', 1, type=int)
    sales = Sales.query.order_by(Sales.transaction_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('sales/list.html', sales=sales)

@bp.route('/view/<int:sale_id>')
@login_required
def view_sale(sale_id):
    """View sale details."""
    sale = Sales.query.get_or_404(sale_id)
    return render_template('sales/view.html', sale=sale)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_sale():
    """Create new sales transaction with automatic stock reduction."""
    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        payment_method = request.form.get('payment_method', 'Cash')
        product_ids = request.form.getlist('product_id[]', type=int)
        quantities = request.form.getlist('quantity[]', type=int)
        unit_prices = request.form.getlist('unit_price[]', type=float)
        
        if not product_ids or not any(q > 0 for q in quantities):
            flash('Please add at least one product.', 'error')
            return redirect(url_for('sales.create_sale'))
        
        try:
            sale = Sales(
                transaction_number=generate_transaction_number(),
                transaction_date=datetime.utcnow(),
                customer_name=customer_name if customer_name else None,
                payment_method=payment_method,
                cashier_id=session.get('user_id', 1)
            )
            db.session.add(sale)
            db.session.flush()
            
            total_amount = 0
            for i, prod_id in enumerate(product_ids):
                if quantities[i] > 0:
                    product = Product.query.get(prod_id)
                    
                    # Check stock availability
                    if product.current_stock < quantities[i]:
                        raise Exception(f'Insufficient stock for {product.title}. Available: {product.current_stock}')
                    
                    # Create sales item
                    subtotal = quantities[i] * unit_prices[i]
                    item = SalesItem(
                        sales_id=sale.id,
                        product_id=prod_id,
                        quantity=quantities[i],
                        unit_price=unit_prices[i],
                        subtotal=subtotal
                    )
                    db.session.add(item)
                    total_amount += subtotal
                    
                    # Update stock
                    prev_stock = product.current_stock
                    product.current_stock -= quantities[i]
                    
                    # Create inventory log
                    log = InventoryLog(
                        product_id=prod_id,
                        transaction_type='Sale',
                        quantity_change=-quantities[i],
                        previous_stock=prev_stock,
                        new_stock=product.current_stock,
                        reference_type='Sales',
                        reference_id=sale.id,
                        notes=f'Sale {sale.transaction_number}',
                        created_by=session.get('user_id', 1)
                    )
                    db.session.add(log)
            
            sale.total_amount = total_amount
            db.session.commit()
            
            flash(f'Sale {sale.transaction_number} completed successfully. Stock updated.', 'success')
            return redirect(url_for('sales.view_sale', sale_id=sale.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating sale: {str(e)}', 'error')
    
    products = Product.query.filter_by(is_active=True).filter(Product.current_stock > 0).order_by(Product.title).all()
    return render_template('sales/form.html', products=products)
