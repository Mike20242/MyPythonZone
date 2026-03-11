"""
Exercise 2.4: CSV File Processing
This script demonstrates how to Read, Modify, and Write data to a CSV file.
"""
import csv
import os

def main():
    print("--- Exercise 2.4: CSV Processing ---\n")
    
    input_file = "students.csv"
    output_file = "students_updated.csv"
    
    # 1. Prepare initial data (List of lists or List of dictionaries)
    # Using list of lists for simplicity with 'csv.writer'
    students = [
        ["Name", "Age", "Grade"],
        ["Alice", 20, "B"],
        ["Bob", 22, "C"],
        ["Charlie", 21, "A"]
    ]
    
    # 2. WRITE original data to CSV
    try:
        with open(input_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(students)
        print(f"Original data written to '{input_file}'")
    except IOError as e:
        print(f"Error writing file: {e}")
        return

    # 3. READ, MODIFY, and WRITE to new CSV
    # We will read 'students.csv', upgrade eveyone's grade (C->B, B->A, A->A+), and write to 'students_updated.csv'
    
    updated_students = []
    
    print("\nReading and modifying data...")
    try:
        with open(input_file, 'r', newline='') as file:
            reader = csv.reader(file)
            header = next(reader) # Read the header
            updated_students.append(header)
            
            for row in reader:
                name, age, grade = row
                # Logic to modify grade
                new_grade = grade
                if grade == "C":
                    new_grade = "B"
                elif grade == "B":
                    new_grade = "A"
                elif grade == "A":
                    new_grade = "A+"
                
                print(f"  Processed {name}: {grade} -> {new_grade}")
                updated_students.append([name, age, new_grade])
                
        # Write updated data
        with open(output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_students)
        print(f"\nUpdated data written to '{output_file}'")
        
    except IOError as e:
        print(f"Error processing CSV: {e}")

    # 4. Verify by reading the new file
    print("-" * 30)
    print(f"Content of '{output_file}':")
    try:
         with open(output_file, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)
    except IOError:
        print("Could not read verification file.")

    print("-" * 30)

if __name__ == "__main__":
    main()
