class Product:
    def __init__(self, product_id, name, price):
        self.product_id = product_id
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} (${self.price})"

class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_product(self, product, quantity=1):
        for item in self.items:
            if item['product'].product_id == product.product_id:
                item['quantity'] += quantity
                print(f"Updated quantity of {product.name} to {item['quantity']}")
                return
        self.items.append({'product': product, 'quantity': quantity})
        print(f"Added {quantity}x {product.name} to cart.")

    def remove_product(self, product_id):
        for item in self.items:
            if item['product'].product_id == product_id:
                self.items.remove(item)
                print(f"Removed product ID {product_id} from cart.")
                return
        print("Product not found in cart.")

    def calculate_total(self):
        total = sum(item['product'].price * item['quantity'] for item in self.items)
        return total

    def show_cart(self):
        if not self.items:
            print("Cart is empty.")
            return
        print("--- Cart Contents ---")
        for item in self.items:
            p = item['product']
            q = item['quantity']
            print(f"{p.name}: ${p.price} x {q} = ${p.price * q}")
        print(f"Total: ${self.calculate_total()}")

class Order:
    def __init__(self, cart, customer_name):
        self.cart = cart
        self.customer_name = customer_name
        self.status = "Pending"

    def place_order(self):
        if not self.cart.items:
            print("Cannot place order with empty cart.")
            return
        total = self.cart.calculate_total()
        self.status = "Placed"
        print(f"Order placed for {self.customer_name}. Total: ${total}. Status: {self.status}")

# Verification
if __name__ == "__main__":
    p1 = Product(1, "Laptop", 800)
    p2 = Product(2, "Mouse", 20)
    p3 = Product(3, "Keyboard", 50)

    cart = ShoppingCart()
    cart.add_product(p1, 1)
    cart.add_product(p2, 2)
    cart.add_product(p3, 1)
    
    cart.show_cart()
    
    cart.remove_product(2)
    cart.show_cart()

    order = Order(cart, "John Doe")
    order.place_order()
