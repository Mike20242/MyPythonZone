def check_even_odd(number):
    """
    Checks if a number is even or odd.
    """
    if number % 2 == 0:
        return "Even"
    else:
        return "Odd"

def main():
    print("=== Exercise 1.1: Check Even/Odd Number ===")
    try:
        user_input = input("Enter a number: ")
        num = int(user_input)
        result = check_even_odd(num)
        print(f"The number {num} is {result}.")
    except ValueError:
        print("Error: Please enter a valid integer.")

if __name__ == "__main__":
    main()
