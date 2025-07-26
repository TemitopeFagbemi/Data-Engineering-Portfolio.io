import json
from datetime import datetime
import os
from collections import Counter

# Pizza Information
pizza_data = {
    "1": {"name": "Classic", "price": 3.4},
    "2": {"name": "Chicken", "price": 4.5},
    "3": {"name": "Pepperoni", "price": 4.0},
    "4": {"name": "Deluxe", "price": 6.0},
    "5": {"name": "Vegetable", "price": 4.0},
    "6": {"name": "Chocolate", "price": 12.0},
    "7": {"name": "Cheese", "price": 5.0},
    "8": {"name": "Meat-feast", "price": 7.5}  # Task 1
}

ORDER_DB_FILE = "pizza_orders.json"
TAX_RATE = 0.075

def save_order_to_json(customer_name, pizza_name, quantity, total_price, order_type, discount_applied, tax_amount):
    order = {
        "orderdatetime": datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),
        "customer_name": customer_name,
        "pizza_type": pizza_name,
        "order_type": order_type,
        "quantity": quantity,
        "total_price": round(total_price, 2),
        "tax": round(tax_amount, 2),
        "discount_applied": discount_applied
    }

    if os.path.exists(ORDER_DB_FILE):
        with open(ORDER_DB_FILE, "r+", encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
            data.append(order)
            file.seek(0)
            json.dump(data, file, indent=4)
    else:
        with open(ORDER_DB_FILE, "w", encoding='utf-8') as file:
            json.dump([order], file, indent=4)

def calculate_payment(price, quantity, discount_rate=0.0):
    subtotal = price * quantity
    discount = subtotal * discount_rate
    total_after_discount = subtotal - discount
    tax = total_after_discount * TAX_RATE
    final_total = total_after_discount + tax
    return round(subtotal, 2), round(discount, 2), round(tax, 2), round(final_total, 2)

def handle_box_order(customer_name, pizza_name, price):
    while True:
        qty_input = input("How many boxes do you want? (or type 'q' to cancel): ").strip()
        if qty_input.lower() == 'q':
            print("Cancelled box order.")
            return
        if qty_input.isdigit():
            quantity = int(qty_input)
            if quantity <= 0:
                print("Quantity must be greater than 0.")
                continue
            break
        else:
            print("Please enter a valid positive number.")

    discount_rate = 0.2 if quantity >= 10 else 0.1 if quantity >= 5 else 0.0
    discount_applied = discount_rate > 0.0
    subtotal, discount, tax, final_total = calculate_payment(price, quantity, discount_rate)

    print(f"\n--- Order Summary ---")
    print(f"Customer: {customer_name}")
    print(f"Pizza: {pizza_name}")
    print(f"Quantity: {quantity} box(es)")
    if discount_applied:
        print(f"Discount Applied: {int(discount_rate * 100)}% (-${discount})")
    else:
        print("Discount Applied: None")
    print(f"Subtotal: ${subtotal}")
    print(f"Tax (7.5%): ${tax}")
    print(f"Total: ${final_total}\n")

    save_order_to_json(customer_name, pizza_name, quantity, final_total, "box", discount_applied, tax)

def handle_slice_order(customer_name, pizza_name, slice_price):
    while True:
        qty_input = input("How many slices do you want? (or type 'q' to cancel): ").strip()
        if qty_input.lower() == 'q':
            print("Cancelled slice order.")
            return
        if qty_input.isdigit():
            quantity = int(qty_input)
            if quantity <= 0:
                print("Quantity must be greater than 0.")
                continue
            break
        else:
            print("Please enter a valid positive number.")

    subtotal, discount, tax, final_total = calculate_payment(slice_price, quantity, 0.0)

    print(f"\n--- Order Summary ---")
    print(f"Customer: {customer_name}")
    print(f"Pizza: {pizza_name}")
    print(f"Quantity: {quantity} slice(s)")
    print("Discount Applied: None")
    print(f"Subtotal: ${subtotal}")
    print(f"Tax (7.5%): ${tax}")
    print(f"Total: ${final_total}\n")

    save_order_to_json(customer_name, pizza_name, quantity, final_total, "slice", False, tax)

def order_pizza(pizza_type):
    if pizza_type in pizza_data:
        pizza = pizza_data[pizza_type]
        price = pizza["price"]
        name = pizza["name"]
        slice_price = round(price / 8, 2)

        customer_name = input("Please enter your name: ").strip().title()
        if not customer_name:
            print("Invalid name. Cancelling order.")
            return

        print(f"You selected {name}!\nPrice: ${price:.2f} per box | ${slice_price:.2f} per slice")

        while True:
            choice = input("Select 'B' for Box or 'S' for Slice (or 'q' to cancel): ").strip().upper()
            if choice == "B":
                handle_box_order(customer_name, name, price)
                break
            elif choice == "S":
                handle_slice_order(customer_name, name, slice_price)
                break
            elif choice == "Q":
                print("Cancelled selection.")
                break
            else:
                print("Invalid choice. Please select 'B', 'S', or 'q'.")
    else:
        print("We do not have this type of pizza for now.")

def view_orders():
    if os.path.exists(ORDER_DB_FILE):
        with open(ORDER_DB_FILE, "r", encoding='utf-8') as file:
            try:
                orders = json.load(file)
                if not orders:
                    print("No orders found.")
                else:
                    for order in orders:
                        print(f"Order at {order.get('orderdatetime', 'N/A')} by {order.get('customer_name', 'N/A')}: "
                              f"{order.get('quantity', 'N/A')} {order.get('pizza_type', 'N/A')} ({order.get('order_type', 'N/A')}) - ${order.get('total_price', 'N/A')}")
            except json.JSONDecodeError:
                print("No orders found or the order database is empty.")
    else:
        print("No orders have been placed yet.")

def view_stats():
    if not os.path.exists(ORDER_DB_FILE):
        print("No stats to show. No orders placed yet.")
        return

    with open(ORDER_DB_FILE, "r", encoding='utf-8') as file:
        try:
            orders = json.load(file)
        except json.JSONDecodeError:
            print("Error reading stats.")
            return

    total_orders = len(orders)
    total_revenue = sum(order.get("total_price", 0) for order in orders)
    pizza_counter = Counter(order['pizza_type'] for order in orders)
    most_common = pizza_counter.most_common(1)[0] if pizza_counter else ("None", 0)

    print(f"\n--- Order Stats ---")
    print(f"Total Orders: {total_orders}")
    print(f"Most Ordered Pizza: {most_common[0]} ({most_common[1]} times)")
    print(f"Total Revenue: ${total_revenue:.2f}\n")

def main():
    while True:
        print("\nWelcome to RushMore Pizza!")
        print("Menu:")
        for key, value in pizza_data.items():
            print(f"{key}: {value['name']} - ${value['price']:.2f}")

        print("\nOptions:")
        print("Enter pizza number to order")
        print("Type 'v' to view all orders")
        print("Type 'stats' to view order stats")
        print("Type 'q' to quit")

        choice = input("What would you like to do? ").strip().lower()

        if choice == 'q':
            print("Goodbye from RushMore Pizza!")
            break
        elif choice == 'v':
            view_orders()
        elif choice == 'stats':
            view_stats()
        elif choice in pizza_data:
            order_pizza(choice)
        else:
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    main()