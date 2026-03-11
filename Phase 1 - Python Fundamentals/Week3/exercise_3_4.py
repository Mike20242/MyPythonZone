class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"Hi, I'm {self.name} and I'm {self.age} years old."

class SchoolMember(Person):
    """Intermediate class to demonstrate multi-level inheritance"""
    def __init__(self, name, age, school_name):
        super().__init__(name, age)
        self.school_name = school_name

    def describe_school(self):
        return f"I am part of {self.school_name}."

class Student(SchoolMember):
    def __init__(self, name, age, school_name, student_id):
        super().__init__(name, age, school_name)
        self.student_id = student_id

    def introduce(self):
        base_intro = super().introduce()
        return f"{base_intro} I am a student with ID {self.student_id} at {self.school_name}."

class Teacher(SchoolMember):
    def __init__(self, name, age, school_name, subject):
        super().__init__(name, age, school_name)
        self.subject = subject

    def introduce(self):
        base_intro = super().introduce()
        return f"{base_intro} I teach {self.subject} at {self.school_name}."

# Verification
if __name__ == "__main__":
    s = Student("Charlie", 15, "Lincoln High", "S12345")
    t = Teacher("Mr. Smith", 40, "Lincoln High", "Mathematics")

    print(s.introduce())
    print(s.describe_school())
    print(t.introduce())
