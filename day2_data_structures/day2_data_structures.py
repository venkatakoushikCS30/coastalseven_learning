'''
Day-02 : Data Structures + Problem Solving

1. python Lists
2. python Tuples
3. python Sets
4. python Dictionaries
5. Comprehension
6. JSON handling
7. mini coding exercises

'''

#1. python Lists - store multiple items in a single variable. lists are mutable (can be changed) , ordered and indexed , allows duplicate values

fruits = ["apple", "banana", "cherry"] #create a list
print(fruits)
print(len(fruits)) # len() returns the length of the list
print(fruits[1]) #accessing elements of the list by index - starts from 0
print(fruits[-1]) #accessing the last element of the list ; -2 is the second last element and so on.
print(fruits[0:2]) #slicing - accessing multiple elements of the list within a range - start index included , end index excluded
print(fruits[1:])
print(fruits[-2:])

if "papaya" in fruits:
    print(True)
else:
    print(False)
fruits[1]="mango" #updating an element of the list
fruits[0:2] = ["apple", "watermelon"] #updating multiple elements of the list

##list methods : append(), insert(), remove(), pop(), clear(), reverse(), sort()

fruits.append("orange") #adding an element to the end of the list.
fruits.insert(1, "kiwi") #adding an element at a specific index
fruits.remove("apple") #removing an element from the list
fruits.pop() #removing the last element of the list or if we specify index it will remove the element at that index eg ; pop(1)
fruits.reverse() #reversing the list
fruits.sort() #sorting the list

vegetables = ["carrot", "potato", "tomato"]

fruits.extend(vegetables) #adding multiple elements or a list to the end of the list , this method can work with tuples  , sets and dictionaries as well
fruits.clear()#clearing the list , but it will not delete the list itself - still available in the memory
del fruits #deleting the entire list ; if we try to print fruits , it will throw an error

fruits = ["apple", "banana", "cherry"]
##loop through a list
for i in range(len(vegetables)):
    print(vegetables[i])

fruits = fruits + vegetables #concatenating two lists

#2. python Tuples - store multiple items in a single variable. tuples are immutable (cannot be changed) , ordered and indexed , allows duplicate values
cars = ("BMW", "Audi", "Mercedes")
print(cars)
print(cars[0])
print(cars[-1])
##if want to update tuple , change the tuple into list, update it and change back into tuple
cars1 = list(cars)
cars1[0] = "Honda"
cars = tuple(cars1)

for i in range(len(cars)): #loop through a tuple
    print(cars[i])
cars = cars + ("Toyota",) #concatenating two tuples

#3. Python Sets - store multiple items in a single variable. sets are unordered , unindexed , no duplicate values allowed
fruits = {"apple", "banana", "cherry"}
print(fruits)
for i in fruits:
    print(fruits)
fruits.add("orange")
fruits.remove("banana")

#4. Python Dictionaries - represented in key value pairs and the items in dict are ordered , changable and do not allow duplicates

dict1 = {
    "brand" : "Ford",
    "model": "Mustang",
    "year": 1984, # if there is duplicate ; it will override the previous value of the key with the latest value
    "year": 1964, # so here ; the 1984 will be overridden by 1964
    
}
print(dict1["year"])
print(dict1.keys()) #returns the keys of the dictionary
print(dict1.values()) #returns the values of the dictionary
print(dict1.items()) #returns the key value pairs of the dictionary

for key, value in dict1.items(): #loop through a dictionary
    print(key, value)
dict1["color"] = "red" #adding a new key value pair to the dictionary
dict1["year"] = 1964 #updating a key value pair in the dictionary
del dict1["model"] #deleting a key value pair from the dictionary

family = { #nested dictionary
    "child1" : {
        "name" : "Ramu",
        "year" : 2004
    },
    "child2" : {
        "name" : "Ravi",
        "year" : 2007
    },
}
for key, value in family.items(): #loop through a nested dictionary
    print(key)
    for k, v in value.items():
        print(k, v)

#5. Comprehension - list , set and dictionary comprehensions
##list comprehension - [expression if condition else expression for item in iterable]
numbers = [1, 2, 3, 4]
result = ["Even" if n % 2 == 0 else "Odd" for n in numbers]

matrix = [ #nested list comprehension
    [1, 2],
    [3, 4],
    [5, 6]
]

flat = [num for row in matrix for num in row]
print(flat)

##set comprehension
numbers = [1, 2, 2, 3, 3, 4]
unique = {n for n in numbers}
print(unique)

##Dictionary Comprehension - {key: expression if condition else expression for item in iterable}
numbers = [1, 2, 3, 4]
result = {n: "Even" if n % 2 == 0 else "Odd" for n in numbers}
print(result)

#6. JSON handling

##json functions - dumps : converts python object into json string
##loads : converts json string into python object
##dump : converts python object into json file
##load : converts json file into python object

import json

data = {
    "name": "koushik",
    "age": 22,
    "city": "Hyderabad",
    "is_student": True,
}
print(data)
json_data = json.dumps(data , indent=4) #the 's' in dumps or loads is for string and indent for formatting the json's indentation
print(json_data)

python_data = json.loads(json_data ,)
print(python_data)
