from typing import Dict
from utils import general
import time


def add_to_cart(product: Dict) -> None:
    """
    Add a product to the shopping cart and update inventory.

    If the product already exists in the cart, increments its quantity by 1.
    If it's a new product, adds it to the cart with quantity 1.
    Updates the product's stock count in the inventory.

    Args:
        product (Dict): Product dictionary containing at minimum:
                       - 'id': Unique product identifier
                       - 'name': Product name for display
                       - 'price': Product price

    Returns:
        None: Function performs side effects on global cart and products lists

    Note:
        - Assumes product stock validation is handled by calling function
        - Modifies global state (cart and products lists)
        - Prints confirmation message to console
    """
    product_in_inventory: Dict | None = None
    for p in general.products:
        if p['id'] == product['id']:
            product_in_inventory = p
            break

    if not product_in_inventory:
        print(f"❌ Product '{product['name']}' not found in inventory")
        return

    if product_in_inventory['stock'] <= 0:
        print(f"❌ '{product['name']}' is out of stock")
        return

    # Find existing cart item and update quantity or add as a new item
    for item in general.cart:
        if item['product_id'] == product['id']:
            item['quantity'] += 1
            break
    else:
        general.cart.append({
            'product_id': product['id'],
            'quantity': 1,
            'name': product['name'],
            'price': product['price']
        })

    # Update inventory
    product_in_inventory['stock'] -= 1

    print(f"✅ Added {product['name']} to cart")
    print(f"📦 Remaining stock: {product_in_inventory['stock']}")


def view_cart() -> float:
    """
    Display the contents of the shopping cart and calculate total cost.

    Shows each cart item with quantity, individual cost, and running total.
    Handles empty cart case gracefully with appropriate message.

    :returns:
        float: Total cost of all items in the cart (0.0 if cart is empty)

    Display Format:
        - Empty cart: Shows empty cart message with emoji
        - Non-empty cart: Shows formatted list with item number, name, quantity,
          and total cost per line item, followed by grand total

    Note:
        - Uses Nigerian Naira (NGN) currency formatting
        - Handles floating-point arithmetic for price calculations
        - Returns 0.0 for empty cart to enable chaining with other functions
    """
    if not general.cart:
        print("\nYour cart is empty 🛒")
        return 0.0

    cart_total: float = 0.0
    print(f"\n{'===' * 8} Your Cart {'===' * 8}")

    for i, item in enumerate(general.cart, 1):
        product_cost: float = item['price'] * item['quantity']
        cart_total += product_cost
        print(f"{i}. {item['name']} x{item['quantity']} - NGN {product_cost:,.2f}")

    print(f"{'=' * 32}")
    print(f"Cart Total: NGN {cart_total:,.2f}")
    print(f"{'=' * 32}")

    return cart_total


def update_cart_item(item_id: int, quantity: int) -> bool:
    """
    Update the quantity of an item in the shopping cart.

    Updates both the cart quantity and adjusts the product inventory accordingly.
    Handles stock validation to ensure sufficient inventory is available.

    Args:
        item_id (int): Index of the item in the cart (0-based)
        quantity (int): New quantity to set for the item

    Returns:
        bool: True if update was successful, False otherwise

    Note:
        - Validates item_id bounds and quantity positivity
        - Adjusts product stock based on quantity difference
        - Prints appropriate error messages for validation failures
    """
    if item_id < 0 or item_id >= len(general.cart):
        print("❌ Invalid item number")
        return False

    if quantity <= 0:
        print("Quantity must be positive")
        return False

    product_id = general.cart[item_id]['product_id']
    current_quantity = general.cart[item_id]['quantity']

    product: Dict | None = None
    for p in general.products:
        if p['id'] == product_id:
            product = p
            break

    if not product:
        print("Product not found in inventory")
        return False

    # Calculate the difference in quantity
    quantity_diff = quantity - current_quantity

    # Check if we have enough stock for the increase
    if quantity_diff > 0 and product['stock'] < quantity_diff:
        print(f"Only {product['stock']} additional items available in inventory")
        return False

    # Update cart quantity
    general.cart[item_id]['quantity'] = quantity

    # Update inventory stock
    product['stock'] -= quantity_diff

    print(f"✅ Updated {general.cart[item_id]['name']} quantity to {quantity}")
    print(f"📦 Remaining stock: {product['stock']}")

    return True


def remove_from_cart(item_index: int) -> bool:
    """
    Remove an item from the shopping cart and restore its quantity to product stock.

    :param item_index: Index of the item to remove from the cart (0-based)
    :return: True if item was successfully removed, False if invalid index
    """
    if item_index < 0 or item_index >= len(general.cart):
        print("❌ Invalid item number")
        return False

    product_id: int = general.cart[item_index]['product_id']

    for p in general.products:
        if p['id'] == product_id:
            p['stock'] += general.cart[item_index]['quantity']
            break

    del general.cart[item_index]
    return True


def clear_cart() -> None:
    """
    Clear all items from the cart and restore their quantities to product stock.

    Prints a confirmation message when completed.
    """
    if not general.cart:
        print("Cart is already empty 🛒")
        return

    for item in general.cart:
        for p in general.products:
            if p['id'] == item['product_id']:
                p['stock'] += item['quantity']
                break

    general.cart.clear()
    print("Cart cleared successfully! 🛒")


def checkout():
    """
    Process checkout for items in cart.

    Validates sufficient wallet balance, confirms purchase with user,
    deducts total from balance, and clears cart upon successful purchase.
    """
    total = view_cart()
    if total == 0:
        return

    print(f"\nOrder Summary:")
    print(f"Total Amount: NGN {total:,.2f}")
    print(f"Your Balance: NGN {general.current_user['balance']:,.2f}")
    print(f"Balance After Purchase: NGN {general.current_user['balance'] - total:,.2f}")

    if total > general.current_user['balance']:
        print("\nInsufficient funds. Please fund your wallet.")
        return

    confirm = input("\nConfirm purchase (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            transaction_id = f"TXN{int(time.time())}"  # Simple transaction ID
            general.current_user['balance'] -= total
            general.save_users()
            general.cart.clear()
            print(f"\n✅ Purchase successful! Transaction ID: {transaction_id}")
            print("Thank you for your order. 💳")
        except Exception as e:
            print(f"❌ Error saving transaction: {e}")
    else:
        print("\n❌ Purchase cancelled")
