def sum_list_loop(numbers):
    """
    Calculates the sum of a list of numbers using a loop.
    """
    total = 0
    for num in numbers:
        total += num
    return total

def main():
    print("=== Exercise 1.2: Sum List Using Loop ===")
    try:
        input_str = input("Enter numbers separated by spaces (e.g., 1 2 3): ")
        if not input_str.strip():
             print("List is empty.")
             return

        # Convert input string to list of floats
        number_list = [float(x) for x in input_str.split()]
        print(f"List: {number_list}")
        
        result = sum_list_loop(number_list)
        print(f"Sum of list: {result}")
        
        # Verify with built-in sum
        assert result == sum(number_list), "Calculation error!"
        
    except ValueError:
        print("Error: Please enter valid numbers.")

if __name__ == "__main__":
    main()
