class Product:
    def __init__(self, product_id, name, price, quantity):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def update_quantity(self, change):
        new_quantity = self.quantity + change
        if new_quantity >= 0:
            self.quantity = new_quantity
            print(f"Updated quantity for {self.name}: {self.quantity}")
        else:
            print("Cannot reduce quantity below zero.")

    def calculate_value(self):
        return self.price * self.quantity

    def __str__(self):
        return f"ID: {self.product_id} | Name: {self.name} | Price: ${self.price} | Qty: {self.quantity}"

# Verification
if __name__ == "__main__":
    p1 = Product(101, "Laptop", 1000, 5)
    print(p1)
    p1.update_quantity(-2)
    print(f"Total Value: ${p1.calculate_value()}")
    p1.update_quantity(-10) # Should fail
