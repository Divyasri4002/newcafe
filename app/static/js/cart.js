// LocalStorage key
const CART_KEY = 'delight_cafe_cart';

// Load cart from localStorage
function getCart() {
    return JSON.parse(localStorage.getItem(CART_KEY)) || [];
}

// Save cart to localStorage
function saveCart(cart) {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    // Sync with backend
    syncCartWithBackend(cart);
}

// Clear cart completely
function clearCart() {
    localStorage.removeItem(CART_KEY);
    updateCartBadge();
    displayCart();
    // Sync empty cart with backend
    syncCartWithBackend([]);
}

// Sync cart with backend
function syncCartWithBackend(cart) {
    fetch('/api/save-cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cart: cart })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Cart synced with backend successfully');
        } else {
            console.error('Failed to sync cart with backend:', data.message || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Failed to sync cart with backend:', error);
    });
}

// Add item to cart
function addToCart(id, name, price) {
    let cart = getCart();
    let item = cart.find(i => i.id === id);
    if (item) {
        item.quantity += 1;
    } else {
        cart.push({ id, name, price, quantity: 1 });
    }
    saveCart(cart);
    updateCartBadge();
    showAddToCartSuccess(name);
}

// Remove item from cart
function removeFromCart(id) {
    let cart = getCart();
    cart = cart.filter(i => i.id !== id);
    saveCart(cart);
    updateCartBadge();
    displayCart();
}

// Update quantity of an item in the cart
function updateQuantity(id, change) {
    let cart = getCart();
    let item = cart.find(i => i.id === id);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(id);
        } else {
            saveCart(cart);
            updateCartBadge();
            displayCart();
        }
    }
}

// Update cart badge count
function updateCartBadge() {
    const cart = getCart();
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    // Update cart badge if it exists
    const cartLink = document.querySelector('a[href*="cart"]');
    if (cartLink) {
        let badge = cartLink.querySelector('.cart-badge');
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'cart-badge';
            cartLink.appendChild(badge);
        }
        badge.textContent = totalItems;
        badge.style.display = totalItems > 0 ? 'block' : 'none';
    }
}

// Render cart items (for cart.html)
function displayCart() {
    const cartContainer = document.getElementById('cartItems');
    const orderSummary = document.getElementById('orderSummary');
    const emptyCartMessage = document.getElementById('emptyCartMessage');
    const checkoutBtn = document.getElementById('checkoutBtn');
    
    if (!cartContainer) return;
    
    let cart = getCart();
    if (cart.length === 0) {
        cartContainer.innerHTML = '';
        if (emptyCartMessage) emptyCartMessage.style.display = 'block';
        if (checkoutBtn) checkoutBtn.style.display = 'none';
        if (orderSummary) {
            orderSummary.innerHTML = '<p class="text-muted">Your cart is empty</p>';
        }
        return;
    }
    
    if (emptyCartMessage) emptyCartMessage.style.display = 'none';
    if (checkoutBtn) checkoutBtn.style.display = 'block';
    
    let cartHTML = '';
    let total = 0;
    
    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        cartHTML += `
            <div class="cart-item">
                <div class="d-flex align-items-center">
                    <div class="bg-light rounded-circle d-flex align-items-center justify-content-center me-3" 
                         style="width: 50px; height: 50px;">
                        <i class="fas fa-utensils text-primary"></i>
                    </div>
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${item.name}</h6>
                        <p class="text-muted mb-0">₹${item.price} per item</p>
                    </div>
                </div>
                <div class="d-flex align-items-center">
                    <div class="d-flex align-items-center me-3">
                        <button class="btn btn-sm btn-outline-secondary" onclick="updateQuantity('${item.id}', -1)">
                            <i class="fas fa-minus"></i>
                        </button>
                        <span class="mx-3 fw-bold">${item.quantity}</span>
                        <button class="btn btn-sm btn-outline-secondary" onclick="updateQuantity('${item.id}', 1)">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    <div class="text-end me-3">
                        <div class="fw-bold">₹${itemTotal}</div>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeFromCart('${item.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    cartHTML += `
        <div class="cart-total">
            <div class="d-flex justify-content-between align-items-center">
                <span class="fs-5">Total Amount:</span>
                <span class="fs-4 fw-bold text-primary">₹${total}</span>
            </div>
        </div>
    `;
    
    cartContainer.innerHTML = cartHTML;
    
    // Update order summary
    if (orderSummary) {
        let summaryHTML = '';
        cart.forEach(item => {
            const itemTotal = item.price * item.quantity;
            summaryHTML += `
                <div class="d-flex justify-content-between mb-2">
                    <span class="text-white">${item.name}</span>
                    <span class="text-white">₹${itemTotal}</span>
                </div>
            `;
        });
        
        summaryHTML += `
            <hr class="border-white">
            <div class="d-flex justify-content-between fw-bold">
                <span class="text-white">Total:</span>
                <span class="text-white">₹${total}</span>
            </div>
        `;
        
        orderSummary.innerHTML = summaryHTML;
    }
}

// Show success notification for adding to cart
function showAddToCartSuccess(itemName) {
    // Create success notification
    const notification = document.createElement('div');
    notification.className = 'position-fixed top-0 end-0 p-3';
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show shadow" role="alert">
            <div class="d-flex align-items-center">
                <i class="fas fa-check-circle me-2"></i>
                <strong>Added to Cart!</strong> ${itemName} has been added to your cart.
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Show cart notification
function showCartNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = 'position-fixed top-0 end-0 p-3';
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show shadow" role="alert">
            <div class="d-flex align-items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Save cart to server
function saveCartToServer() {
    const cart = getCart();
    fetch('/api/save-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cart: cart })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Cart saved to server successfully');
        } else {
            console.error('Failed to save cart to server:', data.message || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error saving cart to server:', error);
    });
}

// Automatically run renderCart() if on cart.html and update cart badge
window.addEventListener('DOMContentLoaded', () => {
    try {
        displayCart();
        updateCartBadge();
        
        // Save cart to server periodically
        setInterval(saveCartToServer, 30000); // Save every 30 seconds
    } catch (error) {
        console.error('Error initializing cart:', error);
    }
});

// Add smooth animations to cart items
function animateCartItem(element) {
    if (!element) return;
    
    element.style.transform = 'scale(1.05)';
    element.style.transition = 'transform 0.2s ease-in-out';
    
    setTimeout(() => {
        element.style.transform = 'scale(1)';
    }, 200);
}

// Add loading states to buttons
function setButtonLoading(button, loading) {
    if (!button) return;
    
    if (loading) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
    } else {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-shopping-cart me-2"></i>Add to Cart';
    }
}

// Enhanced add to cart with loading state
function addToCartWithLoading(id, name, price, button) {
    if (!id || !name || !price) {
        console.error('Invalid parameters for addToCartWithLoading');
        return;
    }
    
    setButtonLoading(button, true);
    
    setTimeout(() => {
        try {
            addToCart(id, name, price);
            setButtonLoading(button, false);
            if (button && button.closest('.food-item')) {
                animateCartItem(button.closest('.food-item'));
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            setButtonLoading(button, false);
        }
    }, 500);
}

// Export functions for use in other scripts
window.cartFunctions = {
    addToCart,
    removeFromCart,
    updateQuantity,
    getCart,
    clearCart,
    displayCart,
    showAddToCartSuccess,
    showCartNotification,
    addToCartWithLoading
};
