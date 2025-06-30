from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from .utils import load_menu_categories, load_menu_items_by_category, send_whatsapp, create_razorpay_order
import os
import uuid
import razorpay
from datetime import datetime

main = Blueprint('main', __name__)

# Temporary in-memory cart and order (for simplicity)
cart = []
last_order = {}

@main.route('/')
def index():
    categories = load_menu_categories()
    return render_template('index.html', categories=categories)

@main.route('/menu')
def menu():
    categories = load_menu_categories()
    return render_template('menu.html', categories=categories)

@main.route('/menu/<category>')
def items(category):
    items = load_menu_items_by_category(category)
    categories = load_menu_categories()
    return render_template('items.html', category_name=category, items=items, categories=categories)

@main.route('/cart')
def cart_view():
    return render_template('cart.html')

@main.route('/checkout', methods=['GET'])
def checkout():
    return render_template('checkout.html')

@main.route('/api/save-cart', methods=['POST'])
def save_cart():
    """Sync cart data from frontend to backend session"""
    try:
        cart_data = request.get_json()
        if not cart_data or 'cart' not in cart_data:
            return jsonify({"success": False, "message": "Invalid cart data"}), 400
        
        session['cart_items'] = cart_data['cart']
        return jsonify({"success": True, "message": "Cart saved successfully"})
    except Exception as e:
        print(f"Error saving cart: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@main.route('/create-order', methods=['POST'])
def create_order():
    client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))

    name = request.form['name']
    phone = request.form['phone']
    pickup_date = request.form['pickup_date']
    pickup_time = request.form['pickup_time']
    notes = request.form.get('notes', '')

    items = session.get('cart_items', [])
    total = sum(item['price'] * item['quantity'] for item in items)
    total_paisa = int(total * 100)

    session['last_order'] = {
        "name": name,
        "phone": phone,
        "pickup_date": pickup_date,
        "pickup_time": pickup_time,
        "notes": notes,
        "items": items,
        "total": total
    }

    # Create Razorpay order
    razorpay_order = client.order.create(dict(
        amount=total_paisa,
        currency='INR',
        payment_capture='1',
        receipt='order_rcptid_11'
    ))

    return {
        "order_id": razorpay_order['id'],
        "amount": total_paisa,
        "key": os.getenv("RAZORPAY_KEY_ID")
    }

@main.route('/payment-success-verify', methods=['POST'])
def payment_success_verify():
    try:
        data = request.get_json()
        print(f"DEBUG: Received payment success data: {data}")
        
        # Get the order data from session
        order_data = session.get('last_order', {})
        if not order_data:
            print("ERROR: No order data found in session")
            return jsonify({"error": "No order data found"}), 400
        
        # Add order time to the data
        order_data['order_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update session with complete order data
        session['last_order'] = order_data
        print(f"DEBUG: Updated session['last_order']: {order_data}")
        
        # Send WhatsApp notification (but do not fail if this fails)
        try:
            whatsapp_success = send_whatsapp(order_data)
        except Exception as e:
            print(f"ERROR: WhatsApp notification failed: {e}")
            whatsapp_success = False
        
        if whatsapp_success:
            print("SUCCESS: WhatsApp notification sent successfully")
        else:
            print("WARNING: WhatsApp notification failed, but payment was successful")
        return jsonify({"status": "success", "whatsapp_sent": bool(whatsapp_success)}), 200
        
    except Exception as e:
        print(f"ERROR: Payment success verification failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@main.route('/test-whatsapp')
def test_whatsapp():
    """Test endpoint to manually trigger WhatsApp notification"""
    try:
        # Sample order data for testing
        test_order = {
            'name': 'Test Customer',
            'phone': '+919876543210',
            'pickup_time': '2:30 PM',
            'items': [
                {'name': 'Cappuccino', 'quantity': 2, 'price': 150},
                {'name': 'Chocolate Cake', 'quantity': 1, 'price': 200}
            ],
            'total': 500,
            'notes': 'Test order for WhatsApp integration',
            'order_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("🧪 Testing WhatsApp notification...")
        success = send_whatsapp(test_order)
        
        if success:
            return jsonify({
                "status": "success", 
                "message": "WhatsApp test message sent successfully! Check your WhatsApp (+919043479513)",
                "whatsapp_sent": True
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "WhatsApp test failed. Check server logs for details.",
                "whatsapp_sent": False
            })
            
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Test failed with error: {str(e)}",
            "whatsapp_sent": False
        })

@main.route('/payment-success')
def payment_success():
    return render_template('payment_success.html', customer_name=last_order.get('name', 'Customer'))

@main.route('/receipt')
def receipt():
    order = session.get('last_order')
    print(f"DEBUG: /receipt session['last_order']: {order}")
    if not order or not order.get("name"):
        print("ERROR: No order found for receipt.")
        return render_template('receipt.html', order=None)
    return render_template('receipt.html', order=order)

@main.route('/feedback', methods=['GET'])
def feedback():
    return render_template('feedback.html')

@main.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    # Here you would process the feedback form data
    # For now, just redirect to home or show a thank you message
    name = request.form.get('name')
    phone = request.form.get('phone')
    experience = request.form.get('experience')
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    # Optionally handle file upload
    # file = request.files.get('image')
    # Save feedback to database or send notification as needed
    return redirect(url_for('main.index'))

@main.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page not found"), 404
