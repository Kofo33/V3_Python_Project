from auth.authentication import handle_user_choice
from user.account_management import dashboard
from products.product_management import load_products
from utils import general


def main() -> None:
    """Main application entry point"""
    # Load data
    general.load_users()
    load_products()

    print("Welcome to the E-Commerce App! 💳")

    while True:
        general.clear_screen()
        print("\n Sign In / Sign Up\n")
        print("1. Sign In")
        print("2. Sign Up")
        print("3. Exit\n")
        user_choice = input(
            "Do you wish to Sign In or Sign Up? Enter [1-3]\n[To exit, enter 'quit'/'exit']: ").strip().lower()
        if handle_user_choice(user_choice) and general.current_user:
            dashboard()


if __name__ == "__main__":
    main()
