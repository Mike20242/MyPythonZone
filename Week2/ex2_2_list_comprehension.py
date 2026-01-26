"""
Exercise 2.2: List Comprehension (Filter & Map)
This script demonstrates how to use list comprehensions for filtering and mapping operations.
"""

def main():
    print("--- Exercise 2.2: List Comprehension ---\n")

    # 1. Working with Integers
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"Original numbers: {numbers}")

    # FILTER: Get even numbers
    # Syntax: [x for x in list if condition]
    even_numbers = [n for n in numbers if n % 2 == 0]
    print(f"Even numbers (Filter): {even_numbers}")

    # MAP: Square each number
    # Syntax: [operation(x) for x in list]
    squared_numbers = [n**2 for n in numbers]
    print(f"Squared numbers (Map): {squared_numbers}")
    print("-" * 30)

    # 2. Working with Strings
    words = ["apple", "is", "banana", "to", "cherry", "go"]
    print(f"Original words: {words}")

    # FILTER: Get words with length > 3
    long_words = [w for w in words if len(w) > 3]
    print(f"Words length > 3 (Filter): {long_words}")

    # MAP: Convert to uppercase
    uppercase_words = [w.upper() for w in words]
    print(f"Uppercase words (Map): {uppercase_words}")

    # COMBINED: Uppercase words that are longer than 3 characters
    long_uppercase = [w.upper() for w in words if len(w) > 3]
    print(f"Long Uppercase words (Map + Filter): {long_uppercase}")
    print("-" * 30)

if __name__ == "__main__":
    main()
