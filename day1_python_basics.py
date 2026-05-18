'''
Day 1 - Python Basics :

1. Variables
2. Data Types
3. conditions
4. loops
5. functions
6. debugging using print/logging
7. understanding errors & stack traces
'''

#1. Variables

x = 10 #Creating Variables
print(x)

name = "koushik"
salary = float(50000.00) #type casting
print(type(name)) #type checking using type()
Name = "Venkata Koushik"
#both name and Name are not same because they are case sensitive
#variable name shouldn't start with number or symbol and also space is not allowed
a,b,c = "apple", "banana", "cherry" #multiple variable assignment
print(a , b , c)


#2. Data Types
name = "venkata koushik" #string
print(type(name))

#numeric types: int, float, complex
age = 20 #integer
print(type(age))

salary = 50000.00 #float
print(type(salary))

complex_number = 3 + 4j #complex number
print(type(complex_number))

is_married = False #boolean
print(type(is_married))

cars = ["bmw", "audi", "toyota"] #list
subject = ("python", "java", "c++") #tuple
fruits = {"apple", "banana", "cherry"} #set
person = {"name": "John", "age": 30, "city": "New York"} #dictionary
x = range(6) #range
x = frozenset({"apple", "banana", "cherry"}) #frozenset - this is a certain type of set that is immutable ( with no methods to add or remove elements)
by = b'Hello' #bytes
print(type(by))
print(by[0]) #(The ASCII code for the capital letter 'H')
n = None #NoneType

#3. conditions
### if, if-else, if-elif-else , nested if , ternary operator
#####operators: ==, !=, <, >, <=, >=, and, or, not

if 5 > 2: #basic if statement
    print("Five is greater than two!")


age = 20
if age >= 18: #if-else statement
    print("You are eligible to vote.")
else:
    print("You are not eligible to vote.")

marks = 70
if marks >=90: #if-elif-else statement
    grade = "A"
elif marks >=80:
    grade = "B"
elif marks >=70:
    grade = "C"
else:
    grade = "D"
print("Your grade is:", grade)

has_id = True
if age>=18:
    if has_id:
        print("Entry allowed.")
    else:
        print("ID required.")
else:
    print("Underage.")

# Ternary Operator - {value_if_true} if {condition} else {value_if_false} - this is used in one line of code
result = "Adult." if age >= 18 else "Minor."
print(result)

#4. loops

#for loop and while loop
##control flow statements: break, continue, pass
for i in range(6): #for loop
    print(i)
for i in range (2,6): #start and end range
    print(i)
for i in range ( 2,6,2): #start , end and step range
    print(i)
for i in range(5):
    for j in range(5):
        print(i,j)
i=3
while i<=6: #while loop - run the loop until the condition is false
    print(i)
    i+=1

for i in range(8):
    if i==4: #break the loop when condition met
        break
    print(i)
for i in range(6):
    if i==4: #continue the loop when condition met
        continue
    print(i)

for i in range(5):
    pass #pass statement - do nothing

#5. functions
###two types - built-in functions and user-defined functions
print("Hello World!") #built-in function

def display(): #user-defined function 
     print("Hello, welcome!")
display() #calling the function

def add(a, b): #user-defined function with parameters
    return a + b
result = add(3, 5)
print(result)

square = lambda x: x * x #lambda function (Short Function) - a function in one line which has no name

print(square(5))

def outer(): #nested function
    
    print("Outer function")

    def inner():
        print("Inner function")

    inner()

outer()


#6. debugging using print/logging

##using print

def add(a,b):
    print("a =", a) #this is debugging using print statement
    print("b =", b)
    print("expected  a + b =", a+b)
    return a-b #this is intentional

result = add(10,5)
print(result) #expected is 15 , but will get 5

##using logging
import logging
logging.basicConfig(level=logging.DEBUG)  #if level is not provided ; then default will be warning
def divide(a,b):
    logging.info(f"a = {a} , b = {b}")
    
    if b == 0:
        logging.error("cannot didive with zero")
        return None
    else:
        result = a / b
        logging.info(f"{a} / {b} = {result}")
        return result

result = divide(10,0)
print(result)

logging.debug("Debug: checking variables")
logging.info("Info: program started")
logging.warning("Warning: low disk space")
logging.error("Error: file missing")
logging.critical("Critical: system failure")

#7. understanding errors & stack traces  
### the below error is intentional only to understand the stack trace``
logging.basicConfig(level=logging.ERROR)

try:
    10 / 0
except Exception as e:
    logging.error("Error occurred", exc_info=True) #exc_info=True will print the stack trace
