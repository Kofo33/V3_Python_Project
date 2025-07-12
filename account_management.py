from utils import general
from auth.authentication import hash_password
from auth.validation import validate_email, validate_password
from cart.cart_management import view_cart, update_cart_item, remove_from_cart, clear_cart, checkout
import time


def verify_current_password() -> bool:
    """
    Verify the current user's password by comparing hashed values.

    Prompts user to enter their password and compares the hash
    with the stored password hash.

    Returns:
        bool: True if password is correct, False otherwise
    """
    password = input("Enter your password to verify: ").strip()

    if not password:
        print("Password cannot be empty")
        return False
    return hash_password(password) == general.current_user['password_hash']


def change_username() -> None:
    """
    Change the current user's username after password verification.

    Requires current password confirmation and ensures new username
    is not empty and unique across all users.
    """
    while True:
        if not verify_current_password():
            print("Incorrect password ❌")
            return
        new_username: str = input("Enter new username: ").strip()
        if not new_username:
            print("Username cannot be empty")
            continue
        if len(new_username) < 2:
            print("Username must be at least 2 characters")
            continue
        if not new_username.isalnum():
            print("Username must contain only letters and numbers")
            continue
        for user in general.users:
            if user['username'] == new_username:
                print("Username already taken! ❌")
                continue
        break

    try:
        general.current_user['username'] = new_username
        general.save_users()
        print("\nUsername updated successfully ✅")
    except Exception as e:
        print(f"Error saving username: {e}")


def change_email() -> None:
    """
    Change the current user's email address after password verification.

    Requires current password confirmation and ensures new email
    has valid format and is unique across all users.
    """
    if not verify_current_password():
        print("Incorrect password")
        return

    while True:
        new_email = input("Enter new email: ").strip().lower()
        if not validate_email(new_email):
            print("Email is not correct! 😒")
            continue

        email_exists = False
        for user in general.users:
            if user['email'] == new_email:
                print("Email already exist! ❌")
                email_exists = True
                break
        if not email_exists:
            break
    try:
        general.current_user['email'] = new_email
        general.save_users()
        print("\nEmail updated successfully! 📧")
    except Exception as e:
        print(f"Error saving email: {e}")


def change_password() -> None:
    """
    Change the current user's password after verification.

    Requires current password confirmation and ensures new password
    meets security requirements (16+ chars, uppercase, lowercase,
    number, special character). Final confirmation before applying changes.
    """
    if not verify_current_password():
        print("Incorrect password")
        return

    print("\nNew password must be at least 16 characters with:")
    print("- At least one uppercase letter")
    print("- At least one lowercase letter")
    print("- At least one number")
    print("- At least one special character")

    while True:
        new_password = input("Enter new password: ").strip()
        if not validate_password(new_password):
            print("Password does not meet requirements")
            continue

        confirm_password = input("Confirm new password: ").strip()
        if new_password != confirm_password:
            print("Passwords do not match")
            continue
        if hash_password(new_password) == general.current_user['password_hash']:
            print("New password cannot be the same as current password")
            continue
        break

    confirm = input("Are you sure you want to change your password? (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            general.current_user['password_hash'] = hash_password(new_password)
            general.save_users()
            print("\nPassword changed successfully ✅")
        except Exception as e:
            print(f"Error saving password: {e}")
    else:
        print("\nPassword change cancelled")


def view_account_details() -> None:
    """
    Display the current user's account information after password verification.

    Shows username, email, and current wallet balance.
    Requires password confirmation for security.
    """
    if not verify_current_password():
        print("Incorrect password")
        return

    print("\n" + "=" * 30)
    print("      ACCOUNT DETAILS")
    print("=" * 30)
    print(f"Username:  {general.current_user['username']}")
    print(f"Email:     {general.current_user['email']}")
    print(f"Balance:   NGN {general.current_user['balance']:,.2f}")
    print("\n" + "=" * 30)


def reset_balance() -> None:
    """
    Reset the current user's wallet balance to zero.

    Requires password verification and user confirmation before proceeding.
    This action is irreversible and will permanently remove all funds.
    """
    if not verify_current_password():
        print("Incorrect password")
        return
    print(f"\nCurrent balance: NGN {general.current_user['balance']:,.2f}")
    confirm: str = input("Are you sure you want to reset your balance to zero? (y/n): ").strip().lower()
    if confirm == 'y':
        if general.current_user['balance'] > 50000:  # For large amounts
            print("⚠️  WARNING: You have a significant balance!")
            confirm_again: str = input("Type 'RESET' to confirm: ").strip()
            if confirm_again != 'RESET':
                print("\nBalance reset cancelled")
                return
        general.current_user['balance'] = 0.0
        try:
            general.save_users()
            print("\nBalance reset to zero ✅")
        except Exception as e:
            print(f"Error saving balance reset: {e}")
    else:
        print("\nBalance reset cancelled")


def delete_account() -> bool:
    """
    Delete the current user's account after verification and confirmation.

    Requires password verification and explicit user confirmation.
    Removes user from system, clears current session, and returns to main menu.

    Returns:
        bool: True if account was deleted, False if cancelled or failed
    """
    if not verify_current_password():
        print("Incorrect password")
        return False

    if general.current_user['balance'] > 0:
        print(f"⚠️  WARNING: You have NGN {general.current_user['balance']:,.2f} in your wallet!")
        print("This balance will be permanently lost if you delete your account.")

    confirm = input("ARE YOU SURE YOU WANT TO DELETE YOUR ACCOUNT? THIS CANNOT BE UNDONE! (y/n): ").strip().lower()
    if confirm == 'y':
        confirm2 = input("Type 'DELETE' to confirm deletion: ").strip()
        if confirm2 != 'DELETE':
            print("\nAccount deletion cancelled")
            return False
        general.users.remove(general.current_user)
        try:
            general.save_users()
            general.current_user = None
            general.cart = []
            print("\nAccount deleted successfully. Returning to main menu. 🗑️")
            return True
        except Exception as e:
            print(f"Error deleting account: {e}")
            return False
    else:
        print("\nAccount deletion cancelled")
        return False


def fund_wallet() -> None:
    """
    Add funds to the current user's wallet balance.

    Provides predefined amounts (10k, 20k, 50k, 100k) and custom amount option.
    Updates the user's balance and displays confirmation.
    """
    print("\n=== Fund Wallet ===")
    print(f"Current balance: NGN {general.current_user['balance']:,.2f}")

    options = {
        '1': 10000,
        '2': 20000,
        '3': 50000,
        '4': 100000,
        '5': "Custom Amount"
    }

    for key, value in options.items():
        print(f"{key}. NGN {value:,.2f}" if isinstance(value, int) else f"{key}. {value}")

    while True:
        fund_choice: str = input("Select amount to add (1-5): ").strip()
        if fund_choice in options:
            if fund_choice == '5':
                try:
                    amount: float = float(input("Enter custom amount: "))
                    if amount <= 0:
                        print("Amount must be a positive number 😒")
                        continue
                    elif amount > 100000000:  # Example limit
                        print("Maximum funding amount is NGN 100,000,000 at a time 🫤")
                        continue
                except ValueError:
                    print("Invalid amount ❌")
                    continue
            else:
                amount = options[fund_choice]

            general.current_user['balance'] += amount
            general.save_users()
            print(f"\nProcessing payment of NGN {amount:,.2f}...")
            time.sleep(1)
            print("Payment successful! ✅")
            break
        else:
            print("Invalid Entry! 💢")


def purchase_menu():
    """
    Main purchase menu interface.

    Provides options for product search, cart management, checkout, and exit.
    Continues until user chooses to exit.
    """
    while True:
        print(f"\n{'===' * 8} Purchase Items {'===' * 8}")
        print("1. Search Items")
        print("2. Manage Cart")
        print("3. Checkout")
        print("4. Back to Store Menu")
        purchase_choice: str = input("Enter choice (1-4): ").strip()
        if purchase_choice == "1":
            from products.product_management import search_products, handle_search_results
            results = search_products()
            if results:
                handle_search_results(results)
        elif purchase_choice == "2":
            handle_cart_management()
        elif purchase_choice == "3":
            if general.cart:
                checkout()
            else:
                print("Your cart is empty! Add items before checkout.")
        elif purchase_choice == "4":
            break
        else:
            print("Invalid choice! Please enter 1-4 💢")


def handle_cart_management() -> None:
    """
    Interactive menu for managing cart items (modify quantity, remove items, clear cart).

    Continues until user chooses to exit or cart becomes empty.
    """
    print("Handle cart Management")
    while True:
        total: float = view_cart()
        if not general.cart:
            print("Cart is empty! 🛒")
            break
        if total == 0.0:
            break

        print("\n1. Change Quantity")
        print("2. Remove Item")
        print("3. Clear Cart")
        print("4. Back to Purchase Menu")

        user_choice: str = input("Enter choice (1-4): ").strip()

        if user_choice == "1":
            try:
                item_id: int = int(input("Enter item number to modify: ")) - 1
                new_quantity: int = int(input("Enter new quantity: "))
                update_cart_item(item_id, new_quantity)
            except ValueError:
                print("❌ Please enter a valid number")
        elif user_choice == "2":
            try:
                selected_item_index: int = int(input("Enter item number to remove: ")) - 1
                remove_from_cart(selected_item_index)
            except ValueError:
                print("❌ Please enter a valid number")
        elif user_choice == "3":
            confirm = input("Are you sure you want to clear the cart? (y/n): ").lower()
            if confirm == 'y':
                clear_cart()
                break
        elif user_choice == "4":
            break
        else:
            print("Invalid choice")


def account_menu() -> None:
    """
    Handle account management menu operations.

    Provides options for users to modify account settings including username,
    email, password, view details, reset balance, and delete account.
    Continues until user chooses to exit or account is deleted.
    """
    while True:
        print(f"\n{'===' * 8} Manage Account {'===' * 8}")
        print("1. Change Username")
        print("2. Change Email")
        print("3. Change Password")
        print("4. View Account Details")
        print("5. Reset Balance")
        print("6. Delete Account")
        print("7. Back to Store Menu")
        user_choice: str = input("Enter choice (1-7): ").strip()
        if user_choice == '1':
            change_username()
        elif user_choice == '2':
            change_email()
        elif user_choice == '3':
            change_password()
        elif user_choice == '4':
            view_account_details()
        elif user_choice == "5":
            reset_balance()
        elif user_choice == "6":
            if delete_account():
                return  # Return to main menu if account deleted
        elif user_choice == "7":
            break
        else:
            print("Invalid choice")


def dashboard():
    """
    A Function for the dashboard menu
    :return:
    """
    from utils.general import clear_screen
    while True:
        clear_screen()
        print(f"\n{'===' * 8} Welcome, {general.current_user['username']} {'===' * 8}")
        print("1. Fund Wallet")
        print("2. Purchase Items")
        print("3. Manage Account")
        print("4. Logout")
        dashboard_choice: str = input("Enter choice (1-4): ").strip()

        if dashboard_choice == "1":
            fund_wallet()
        elif dashboard_choice == "2":
            purchase_menu()
        elif dashboard_choice == "3":
            account_menu()
        elif dashboard_choice == "4":
            general.current_user = None
            general.cart = []
            break
        else:
            print("Invalid choice")
