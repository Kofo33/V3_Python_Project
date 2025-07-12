from typing import List, Dict
from utils import general
from cart.cart_management import add_to_cart
import os


def load_products() -> None:
    """
    Load products from all warehouse*.txt files in data directory.

    File format: name1:price1;name2:price2;...
    Assigns sequential IDs and default stock of 10 to each product.
    Skips empty files and malformed entries.
    """
    from utils.general import ensure_data_directory

    general.products = []
    ensure_data_directory()

    # Find all warehouse files
    warehouse_files = []
    for file in os.listdir('data'):
        if file.startswith('warehouse') and file.endswith('.txt'):
            warehouse_files.append(os.path.join('data', file))

    # Load products from each file
    product_id = 1
    for file_path in warehouse_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    continue

                items = content.split(';')
                for item in items:
                    if not item:
                        continue
                    try:
                        name, price = item.split(':')
                        general.products.append({
                            'id': product_id,
                            'name': name.strip(),
                            'price': float(price.strip()),
                            'stock': 10  # Default stock
                        })
                        product_id += 1
                    except ValueError:
                        continue
        except FileNotFoundError:
            continue


def search_products():
    """
    Search for products in inventory based on user input.

    Prompts user for search terms and searches through the global products list.
    Performs case-insensitive partial matching on product names.
    If multiple search terms are provided, matches products containing ANY of the terms.

    Returns:
        List[Dict]: List of matching product dictionaries. Each product contains:
                   - 'id': Unique product identifier
                   - 'name': Product name
                   - 'price': Product price
                   - 'stock': Available stock quantity
                   Returns empty list if no matches found or invalid input.

    Global Variables:
        products (List[Dict]): Global inventory list that gets searched

    Note:
        - Performs partial string matching (case-insensitive)
        - Displays formatted search results to console
        - Handles empty input gracefully
        - Avoids duplicate results when multiple terms match same product
    """
    query = input("\nEnter search query: ").strip()
    if not query:
        print("Please enter a search term")
        return []

    search_terms: List[str] = query.split()
    results = []

    for product in general.products:
        for term in search_terms:
            if term.lower() in product['name'].lower():
                results.append(product)

    if not results:
        print("\nNo matching items found")
        return []

    print("\n=== Search Results ===")
    for i, product in enumerate(results, 1):
        print(f"{i}. {product['name']} - NGN {product['price']:,.2f} ({product['stock']} available)")

    return results


def handle_search_results(results: list[dict]) -> None:
    """
    Handle user interactions with search results.

    Displays a menu allowing users to:
    1. Add a selected item to their cart (with stock validation)
    2. Perform a new search
    3. Return to the purchase menu

    Args:
        results (list[dict]): List of product dictionaries from search results.
                            Each product should contain 'id', 'name', 'price', and 'stock' keys.

    Returns:
        None

    Note:
        - Validates item selection bounds and stock availability
        - Handles invalid input gracefully with error messages
        - Continues looping until user chooses to search again or go back
    """
    while True:
        print("\n1. Add to Cart")
        print("2. Search Again")
        print("3. Back to Purchase Menu")

        choice: str = input("Enter choice (1-3): ").strip()

        if choice == "1":
            try:
                selection: int = int(input("Enter item number to add: ")) - 1
                if 0 <= selection < len(results):
                    product = results[selection]
                    if product['stock'] <= 0:
                        print("❌ Item out of stock")
                        continue
                    add_to_cart(product)
                else:
                    print("💢 Invalid item number!")
            except ValueError:
                print("Invalid input")
        elif choice == "2":
            results = search_products()
            if not results:
                continue
        elif choice == "3":
            break
        else:
            print("Invalid choice")
