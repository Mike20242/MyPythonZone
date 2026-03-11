def factorial(n):
    """
    Calculates the factorial of a non-negative integer n.
    Returns -1 if input is negative.
    """
    if n < 0:
        return -1
    if n == 0 or n == 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def main():
    print("=== Exercise 1.3: Factorial Function ===")
    try:
        user_input = input("Enter a non-negative integer: ")
        n = int(user_input)
        
        result = factorial(n)
        
        if result == -1:
            print("Error: Factorial is not defined for negative numbers.")
        else:
            print(f"Factorial of {n} ({n}!) is: {result}")
            
    except ValueError:
        print("Error: Please enter a valid integer.")

if __name__ == "__main__":
    main()
