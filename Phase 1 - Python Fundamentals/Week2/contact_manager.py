"""
Mini Project: Contact Management System
This script implements a simple contact management system that saves and loads data from a JSON file.
Features: Add, Remove, Search, List contacts.
"""
import json
import os
import re

CONTACTS_FILE = "contacts.json"

class ContactManager:
    def __init__(self, filename=CONTACTS_FILE):
        self.filename = filename
        self.contacts = self.load_contacts()

    def load_contacts(self):
        """Loads contacts from the JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("Error loading contacts. Starting with an empty list.")
                return []
        return []

    def save_contacts(self):
        """Saves current contacts to the JSON file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.contacts, f, indent=4)
            # print("Contacts saved successfully.") 
        except IOError:
            print("Error saving contacts.")

    def validate_email(self, email):
        """Validates email format using RegEx."""
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))

    def validate_phone(self, phone):
        """Validates that phone contains only digits and is 10-12 chars long."""
        pattern = r"^\d{10,12}$"
        return bool(re.match(pattern, phone))

    def add_contact(self, name, phone, email):
        """Adds a new contact with validation."""
        # Validation
        if not self.validate_email(email):
            print(f"Error: Invalid email format -> {email}")
            return False
            
        if not self.validate_phone(phone):
            print(f"Error: Invalid phone number (must be 10-12 digits) -> {phone}")
            return False

        # Check for duplicates
        for contact in self.contacts:
            if contact['name'].lower() == name.lower():
                print(f"Contact '{name}' already exists.")
                return False
        
        self.contacts.append({
            "name": name,
            "phone": phone,
            "email": email
        })
        self.save_contacts()
        print(f"Contact '{name}' added.")
        return True

    def remove_contact(self, name):
        """Removes a contact by name."""
        initial_count = len(self.contacts)
        self.contacts = [c for c in self.contacts if c['name'].lower() != name.lower()]
        
        if len(self.contacts) < initial_count:
            self.save_contacts()
            print(f"Contact '{name}' removed.")
            return True
        else:
            print(f"Contact '{name}' not found.")
            return False

    def search_contact(self, name):
        """Search for a contact by name."""
        for contact in self.contacts:
            if contact['name'].lower() == name.lower():
                return contact
        return None

    def list_contacts(self):
        """Lists all contacts."""
        if not self.contacts:
            print("No contacts found.")
            return

        print("\n--- Contact List ---")
        for i, contact in enumerate(self.contacts, 1):
            print(f"{i}. {contact['name']} | {contact['phone']} | {contact['email']}")
        print("--------------------\n")

# --- Interactive Menu ---
def print_menu():
    print("\n=== Contact Management System ===")
    print("1. Add Contact")
    print("2. Remove Contact")
    print("3. Search Contact")
    print("4. List All Contacts")
    print("5. Exit")

def interactive_mode():
    manager = ContactManager()
    
    while True:
        print_menu()
        choice = input("Enter choice (1-5): ")
        
        if choice == '1':
            name = input("Enter Name: ")
            phone = input("Enter Phone: ")
            email = input("Enter Email: ")
            manager.add_contact(name, phone, email)
        elif choice == '2':
            name = input("Enter Name to Remove: ")
            manager.remove_contact(name)
        elif choice == '3':
            name = input("Enter Name to Search: ")
            contact = manager.search_contact(name)
            if contact:
                print(f"\nFound: {contact}")
            else:
                print("\nContact not found.")
        elif choice == '4':
            manager.list_contacts()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

def test_run():
    """ Runs a predetermined sequence of operations for verification """
    print("Running automated test mode...")
    # Use a test file to avoid messing up main file if it exists (though for valid task, main file is fine)
    test_file = "test_contacts.json"
    if os.path.exists(test_file):
        os.remove(test_file)
        
    manager = ContactManager(test_file)
    
    print("\n1. Adding contacts (Valid)...")
    manager.add_contact("John Doe", "1234567890", "john@example.com")
    manager.add_contact("Jane Smith", "0987654321", "jane@example.com")
    
    print("\n2. Adding contacts (Invalid)...")
    print("  a) Invalid Email:")
    manager.add_contact("Invalid Email", "1112223333", "john.doe") # Missing @ and domain
    print("  b) Invalid Phone:")
    manager.add_contact("Invalid Phone", "123", "valid@email.com") # Too short

    print("\n3. Listing contacts...")
    manager.list_contacts()
    
    print("\n4. Searching for 'John Doe'...")
    c = manager.search_contact("John Doe")
    print(f"Result: {c}")
    
    print("\n5. Removing 'John Doe'...")
    manager.remove_contact("John Doe")
    
    print("\n6. Listing contacts after removal...")
    manager.list_contacts()
    
    # Cleanup test file
    if os.path.exists(test_file):
        os.remove(test_file)
        print("Test file cleaned up.")

if __name__ == "__main__":
    # If this script is imported or run directly, we might want to default to interactive 
    # BUT for the purpose of 'auto-verification' by the AI agent, we can check a flag or just run test if args.
    # We'll default to interactive unless a specific env var is set, OR since user wants to run it, 
    # I should leave it interactive. 
    # To test it myself, I will call the `test_run()` function via a temporary small script or 
    # just rely on code review. 
    # actually, I can just modify this line for now to Run test if I passed a specific argument? 
    # No, that complicates things for the user. 
    
    # I'll just comment out 'interactive_mode()' and call 'test_run()' for MY verification, 
    # then swap it back? 
    # Better: I will create a separate verification step. 
    # Or, I can check if an environment variable is set.
    
    # For user convenience, default is interactive.
    # To verify now, I will write a small separate test script or use python -c.
    
    interactive_mode()
