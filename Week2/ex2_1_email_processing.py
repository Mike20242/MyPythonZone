import re

def process_email(email):
    """
    Parses an email address to extract the username and domain using RegEx.

    Args:
        email (str): The email address string.

    Returns:
        tuple: (username, domain) if valid, otherwise (None, None).
    """
    # Pattern explanation:
    # ^         Start of string
    # ([\w\.-]+) Group 1: Username (alphanumeric, dots, hyphens)
    # @         Literal '@' symbol
    # ([\w\.-]+) Group 2: Domain (alphanumeric, dots, hyphens)
    # $         End of string
    pattern = r"^([\w\.-]+)@([\w\.-]+)$"
    
    match = re.match(pattern, email)
    
    if match:
        return match.group(1), match.group(2)
    return None, None

def main():
    print("--- Exercise 2.1: Email Processing (with RegEx) ---\n")
    
    # Test cases
    emails = [
        "john.doe@gmail.com",
        "support@python.org",
        "invalid-email",
        "admin@company.co.uk",
        "bad@domain@com" # invalid format
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
