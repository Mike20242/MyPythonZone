class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class Bird(Animal):
    def speak(self):
        return "Chirp!"

# Verification
if __name__ == "__main__":
    animals = [Dog("Buddy"), Cat("Whiskers"), Bird("Tweety")]
    for animal in animals:
        print(f"{animal.name} says {animal.speak()}")
