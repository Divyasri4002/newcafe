import pandas as pd
import razorpay
import os
from dotenv import load_dotenv
from twilio.rest import Client
from .menu_data import menu_items
load_dotenv()

# Debug prints for Razorpay keys
print("DEBUG: RAZORPAY_KEY_ID =", os.getenv('RAZORPAY_KEY_ID'))
print("DEBUG: RAZORPAY_KEY_SECRET =", os.getenv('RAZORPAY_KEY_SECRET'))

RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def load_menu_categories():
    category_images = {
        "Combos": "images/categories/combo.jpg",
        "Burger": "images/categories/delicious-burger.jpg",
        "Dessert & Ice Cream": "images/categories/desser-ice.jpg",
        "Fresh Juice": "images/categories/fresh-juice.jpg",
        "Milkshake": "images/categories/milkshake.jpg",
        "Mojito": "images/categories/mojito_cover.jpg",
        "Momos - Non-Veg": "images/categories/momos-nonveg.jpg",
        "Momos - Veg": "images/categories/momos-veg.jpg",
        "Non-Veg Wraps": "images/categories/non-veg-wraps.jpg",
        "Pizza - Non-Veg": "images/categories/pizza-non veg.jpg",
        "Pizza - Veg": "images/categories/pizza-veg.jpg",
        "Sandwich - Non-Veg": "images/categories/sandwich.jpg",
        "Ice Cream (Single Scoop)": "images/categories/single-scoop.jpg",
        "Starters - Non-Veg": "images/categories/Starters - Non-Veg.jpg",
        "Starters - Veg": "images/categories/starters-veg.jpg",
        "Sandwich - Veg": "images/categories/veg-sandwich.jpg",
        "Wrap - Veg": "images/categories/wrap-veg.jpg",
    }
    categories = list(set(item['category'] for item in menu_items))
    return [{
        "name": c,
        "image": category_images.get(c, "images/categories/combo.jpg")
    } for c in categories]

def load_menu_items_by_category(category_name):
    filtered = [item for item in menu_items if item['category'].lower() == category_name.lower()]
    return filtered


def create_razorpay_order(amount, receipt_id):
    print('DEBUG: Creating order with key:', RAZORPAY_KEY_ID, 'secret:', RAZORPAY_KEY_SECRET)
    print('DEBUG: Amount:', amount, 'Receipt:', receipt_id)
    order = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1',
        'receipt': receipt_id
    })
    return order

def send_whatsapp(order_data):
    try:
        # Get Twilio credentials from environment variables
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_whatsapp = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')  # Default Twilio WhatsApp number
        to_whatsapp = os.getenv('CAFE_OWNER_WHATSAPP', 'whatsapp:+919043479513')  # Owner's number with WhatsApp prefix
        
        # Debug prints
        print(f"DEBUG: Account SID: {account_sid}")
        print(f"DEBUG: Auth Token: {auth_token[:10]}..." if auth_token else "DEBUG: Auth Token: None")
        print(f"DEBUG: From WhatsApp: {from_whatsapp}")
        print(f"DEBUG: To WhatsApp: {to_whatsapp}")
        
        # Check if required credentials are available
        if not account_sid or not auth_token:
            print("ERROR: Twilio credentials not found in environment variables")
            return False
            
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Format the message body
        items_text = ', '.join([
            f"{item.get('name') or item.get('item_name') or 'Item'}"
            for item in order_data.get('items', [])
        ])
        
        message_body = f"""🧾 *New Order Received*

👤 *Customer Details:*
• Name: {order_data.get('name', 'N/A')}
• Phone: {order_data.get('phone', 'N/A')}
• Pickup Date: {order_data.get('pickup_date', 'N/A')}
• Pickup Time: {order_data.get('pickup_time', 'N/A')}

🛒 *Order Items:*
{items_text}

💰 *Total Amount:* ₹{order_data.get('total', 0)}

📝 *Special Notes:* {order_data.get('notes', 'None')}

⏰ *Order Time:* {order_data.get('order_time', 'Just now')}"""

        print(f"DEBUG: Sending WhatsApp message to {to_whatsapp}")
        print(f"DEBUG: Message body: {message_body}")
        
        # Send the message
        message = client.messages.create(
            body=message_body,
            from_=from_whatsapp,
            to=to_whatsapp
        )
        
        print(f"SUCCESS: WhatsApp message sent! SID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"ERROR: WhatsApp message failed: {str(e)}")
        print(f"ERROR: Exception type: {type(e).__name__}")
        return False
