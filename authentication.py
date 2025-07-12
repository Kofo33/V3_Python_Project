import hashlib
import random
import string
from typing import Dict, List
from utils import general
from auth.validation import validate_email, validate_password


def generate_password() -> str:
    """
    Generate a random 16-character password with the following requirements:
    - At least one number
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one symbol
    Returns: str: Generated 16-character password
    """
    numbers_pass_chars: str = string.digits
    lower_pass_chars: str = string.ascii_lowercase
    upper_pass_chars: str = string.ascii_uppercase
    sym_pass_chars: str = string.punctuation

    password: List = [
        random.choice(numbers_pass_chars),
        random.choice(lower_pass_chars),
        random.choice(upper_pass_chars),
        random.choice(sym_pass_chars)
    ]
    all_pass_chars: str = numbers_pass_chars + lower_pass_chars + upper_pass_chars + sym_pass_chars[0]
    for _ in range(12):
        password.append(random.choice(all_pass_chars))
    random.shuffle(password)
    return ''.join(password)


def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def sign_in_user() -> bool:
    """
    Function for signing in a user with validated credentials.
    Returns: bool: True if signin was successful, False otherwise
    """
    print("\n" + "=" * 8 + "Login to your Account" + "=" * 8 + "\n")

    user_log_identity: str = input(f"Enter your Username / Email: ").strip()
    user_log_pass: str = input("Enter your password: ").strip()
    hashed_input: str = hash_password(user_log_pass)

    for user in general.users:
        if (user['username'] == user_log_identity or user['email'] == user_log_identity):
            if user['password_hash'] == hashed_input:
                general.current_user = user
                print("\nLogin successful! 😄")
                return True
            else:
                print(f"\nDebug: Stored hash: {user['password_hash']}")
                print(f"Debug: Input hash: {hashed_input}")
                print("\nLogin failed! Invalid password. 😡")
                return False

    print("\nLogin failed! Username or email not found. 😡")
    return False


def sign_up_user() -> bool:
    """
    Function for signing up a new user with validated credentials.
    Returns: bool: True if signup was successful, False otherwise
    """
    print("\n" + "=" * 8 + "Create an Account" + "=" * 8 + "\n")

    # Username handling
    while True:
        user_reg_username: str = input(f"Enter your Username: ").strip()
        if not user_reg_username:
            print("Username cannot be empty")
            continue
        if len(user_reg_username) < 2:
            print("Username must be at least 2 characters")
            continue
        if not user_reg_username.isalnum():
            print("Username must contain only letters and numbers")
            continue
        for user in general.users:
            if user['username'] == user_reg_username:
                print("Username already exist! ❌")
                continue
        break

    # Email handling
    while True:
        user_reg_email: str = input("Enter your E-mail: ").strip().lower()
        if not user_reg_email:
            print("Email cannot be empty")
            continue

        if not validate_email(user_reg_email):
            print("Email is not correct! 😒")
            continue

        email_exists = False
        for user in general.users:
            if user['email'] == user_reg_email:
                print("Email already exist! ❌")
                email_exists = True
                break

        if not email_exists:
            break

    # Password handling
    while True:
        password_choice: str = input("Do you want to auto-gen password? [y/n]\n: ").lower().strip()
        user_reg_password: str = ""
        if password_choice in ['y', 'yes']:
            user_reg_password = generate_password()
            print(f"Your password is {user_reg_password}")
            break
        elif password_choice in ['n', 'no']:
            print("Password must be 16 characters long!")
            print("Password must contain an Uppercase letter")
            print("Password must contain a lowercase letter")
            print("Password must contain a number")
            print("Contains at least one special character/symbol\n")

            user_pass: str = input("Enter your password: ").strip()
            if not validate_password(user_pass):
                print("Password doesn't meet requirements!")
                continue
            user_reg_password = user_pass
            break
        else:
            print("Invalid entry. Try again!")
            continue

    new_user: Dict = {
        'username': user_reg_username,
        'email': user_reg_email,
        'password_hash': hash_password(user_reg_password),
        'balance': 0
    }

    general.users.append(new_user)
    general.save_users()
    general.current_user = new_user
    print(f"Account created successfully for {user_reg_username}! ✅")
    return True


def handle_user_choice(choice: str) -> bool:
    """
    Process user menu selection
    :param choice: str
    :return: bool
    """
    if choice == '1':
        return sign_in_user()
    elif choice == '2':
        return sign_up_user()
    elif choice in ('3', 'exit', 'quit'):
        print("Thank you for using the app!\nShutting down...")
        import time
        import sys
        time.sleep(1)
        sys.exit()
    else:
        print("Invalid entry! Please try again.")
        return False
