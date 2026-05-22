#types of methods
class Car:
    no_of_wheels = 4 #this is a class variable ; it is shared by all objects
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year
    
    #types of methods - instance methods (using self keyword), class methods(using cls keyword and @classmethod decorator)
    #  and static methods - it is just a helper function ( using @staticmethod decorator)
    def drive(self): #instance method - used by objects
        print(f"{self.brand} {self.model} is driving")
    @classmethod
    def get_no_of_wheels(cls): #class method - used by class
        return cls.no_of_wheels
    @staticmethod
    def is_car(car): #static method - used by class
        return isinstance(car, Car)

toyota = Car("Toyota", "Camry", 2022)
#these are instance variables - they are unique to each objectn( like toyota has its own brand while bmw has its own brand)
print(toyota.brand)
print(toyota.model)
print(toyota.year)

bmw = Car("BMW", "X5", 2023)
print(toyota.no_of_wheels) # accessing the class variable
print(toyota.drive())
print(Car.is_car(toyota))

#INHERITANCE - subclass inheriting from superclass

class Parent:
    def __init__(self , name):
        self.name = name
        print("Parent class is called")
class Child(Parent):
    def __init__(self , name , age):
        super().__init__(name) #this is super constructor through which we can access the values of parent
        self.age = age
        print("Child class is called")

child = Child("Koushik", 22)
print(child.name)
print(child.age)

#ENCAPSULATION - hiding the implementation details ( we implement it by adding _ in front of variable name to make it private)
class Bank:
    def __init__(self):
        self.__balance = 1000 #private variable ( if the object try to access it driectly ,  it will throw an error)
    def show_balance(self):
        print(f"Balance: {self.__balance}") #here , we can access the private variable
sbi = Bank()
sbi.show_balance()

#POLYMORPHISM - same method name but different implementations
class Dog:
    def sound(self):
        print("Bark")

class Cat:
    def sound(self):
        print("Meow")

animals = [Dog(), Cat()]

for a in animals:
    a.sound()

#method overriding
class Animal:
    def sound(self):
        print("Animal sound")

class Dog(Animal):
    def sound(self):
        print("Bark") # overriding the method in parent class
d = Dog()
d.sound()