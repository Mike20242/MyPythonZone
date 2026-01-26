"""
Exercise 2.1: String Processing (Email Split)
This script demonstrates how to split an email address into a username and a domain
using Python's string manipulation methods.
"""

def process_email(email):
    """
    Parses an email address to extract the username and domain.

    Args:
        email (str): The email address string (e.g., "user@example.com").

    Returns:
        tuple: A tuple containing (username, domain).
               Returns (None, None) if the email format is invalid.
    """
    # Check if '@' is in the email string
    if "@" not in email:
        return None, None
    
    # Split the email string at the first occurrence of '@'
    # The maxsplit=1 ensures we only split once even if there are unusual characters,
    # though standard emails strictly have one '@'.
    parts = email.split("@", 1)
    
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, None

def main():
    print("--- Exercise 2.1: Email Processing ---\n")
    
    # Test cases
    emails = [
        "john.doe@gmail.com",
        "support@python.org",
        "invalid-email",
        "admin@company.co.uk"
    ]
    
    for email in emails:
        username, domain = process_email(email)
        if username and domain:
            print(f"Email: {email}")
            print(f"  -> Username: {username}")
            print(f"  -> Domain:   {domain}")
        else:
            print(f"Email: {email}")
            print("  -> Error: Invalid email format")
        print("-" * 30)

if __name__ == "__main__":
    main()
