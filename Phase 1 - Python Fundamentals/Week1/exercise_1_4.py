class Student:
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score

    def __str__(self):
        return f"Name: {self.name}, Age: {self.age}, Score: {self.score}"

class StudentManager:
    def __init__(self):
        self.students = []

    def add_student(self, name, age, score):
        new_student = Student(name, age, score)
        self.students.append(new_student)
        print(f"Student {name} added.")

    def show_all_students(self):
        if not self.students:
            print("No students found.")
            return
        
        print("\n--- Student List ---")
        for st in self.students:
            print(st)
        print("--------------------")

    def find_student_by_name(self, name):
        found = False
        for st in self.students:
            if st.name.lower() == name.lower():
                print(f"Found: {st}")
                found = True
        if not found:
            print(f"Student {name} not found.")

def main():
    manager = StudentManager()
    
    while True:
        print("\n=== Student Management System ===")
        print("1. Add Student")
        print("2. Show All Students")
        print("3. Find Student")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            name = input("Enter name: ")
            try:
                age = int(input("Enter age: "))
                score = float(input("Enter score: "))
                manager.add_student(name, age, score)
            except ValueError:
                print("Invalid input for age or score.")
        elif choice == '2':
            manager.show_all_students()
        elif choice == '3':
            name = input("Enter name to search: ")
            manager.find_student_by_name(name)
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
