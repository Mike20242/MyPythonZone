"""
Exercise 2.3: JSON File Processing
This script demonstrates how to Write data to a JSON file and Read it back.
"""
import json
import os

def main():
    print("--- Exercise 2.3: JSON Processing ---\n")
    
    filename = "products.json"
    
    # 1. Prepare data (List of dictionaries)
    products = [
        {"id": 101, "name": "Laptop", "price": 1200.50, "in_stock": True},
        {"id": 102, "name": "Mouse", "price": 25.00, "in_stock": True},
        {"id": 103, "name": "Monitor", "price": 300.00, "in_stock": False}
    ]
    
    print(f"Data to write:\n{products}\n")
    
    # 2. WRITE to JSON file
    try:
        # 'w' mode for writing. 'indent=4' makes it human-readable.
        with open(filename, 'w') as file:
            json.dump(products, file, indent=4)
        print(f"Successfully wrote data to '{filename}'")
    except IOError as e:
        print(f"Error writing file: {e}")
        return

    print("-" * 30)

    # 3. READ from JSON file
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                loaded_data = json.load(file)
            
            print(f"Read data from '{filename}':\n")
            # Print cleanly
            for item in loaded_data:
                print(f"ID: {item['id']}, Name: {item['name']}, Price: ${item['price']}")
        else:
            print(f"File '{filename}' not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from '{filename}'.")
    except IOError as e:
        print(f"Error reading file: {e}")

    # Cleanup (Optional: remove file after test to keep directory clean, 
    # but usually we want to keep it to see the result. I will leave it.)
    
    print("-" * 30)

if __name__ == "__main__":
    main()
