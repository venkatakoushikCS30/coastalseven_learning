'''
1. Create a list called colors with the values "red", "green", "blue"
Print the first item in the list
Change the second item to "yellow"
Add "purple" to the end of the list using append()
Remove "red" from the list using remove()
Print the list'''

colors = ["red", "green", "blue"]
print(colors[0])
colors[1] = "yellow"
colors.append("purple")
colors.remove("red")
print(colors)

'''
2. Create a tuple called fruits with the values "apple", "banana", "cherry"
Print the second item in the tuple
Print the number of items using len()
Unpack the tuple into three variables a, b, c
Print the variable b
'''
fruits = ("apple", "banana", "cherry")
print(fruits[1])
print(len(fruits))
a, b, c = fruits
print(b)


'''
3. Create a set called colors with the values "red", "green", "blue"
Print the set
Add "yellow" to the set using add()
Remove "green" from the set using discard()
Print the number of items using len()
'''
colors = {"red", "green", "blue"}
print(colors)
colors.add("yellow")
colors.discard("green")
print(len(colors))

'''
4. Create a dictionary called car with the keys "brand", "model", "year" and values "Ford", "Mustang", 2024
Print the value of the "model" key
Add a new key "color" with the value "red"
Remove the "brand" key using pop()
Print the dictionary
'''
car = {
    "brand": "Ford",
    "model": "Mustang",
    "year": 2024
}
print(car["model"])
car["color"] = "red"
car.pop("brand")
print(car)

'''
5. Create a list called numbers with the values 1, 2, 3, 4, 5
Create a new list called squares using a list comprehension that squares each number in the numbers list
Print the squares list
Create a third list called even_squares using a list comprehension that only squares the even numbers from the original numbers list
Print the even_squares list
'''
numbers = [1, 2, 3, 4, 5]
squares = [n**2 for n in numbers]
print(squares)
even_squares = [n**2 for n in numbers if n % 2 == 0]
print(even_squares)

'''
6. Create a string variable called word with the value "comprehension"
Create a set called unique_vowels using a set comprehension that extracts only the vowels (a, e, i, o, u) from the word
Print the unique_vowels set
Create a list called words with the values "apple", "banana", "cherry", "date"
Create a set called word_lengths using a set comprehension that stores the length of each string in the words list
Print the word_lengths set
'''
word = "comprehension"
unique_vowels = {char for char in word if char in "aeiou"}
print(unique_vowels)
words = ["apple", "banana", "cherry", "date"]
word_lengths = {len(word) for word in words}
print(word_lengths)

'''
7. Create a list called keys with the values "a", "b", "c"
Create a dictionary called ascii_dict using a dictionary comprehension that pairs each key with its ASCII integer value using the ord() function
Print ascii_dict
Create a dictionary called prices with the values {"apple": 1.50, "banana": 0.50, "cherry": 3.00}
Create a new dictionary called discounted_prices using a dictionary comprehension that reduces each price in prices by 10% (multiply by 0.9)
Print discounted_prices
'''
keys = ["a", "b", "c"]
ascii_dict = {key: ord(key) for key in keys}
print(ascii_dict)
prices = {"apple": 1.50, "banana": 0.50, "cherry": 3.00}
discounted_prices = {key: value * 0.9 for key, value in prices.items()}
print(discounted_prices)

'''
8. Import the json module
Create a variable x with this JSON string: '{"name": "Emil", "age": 30}'
Convert the JSON string into a Python dictionary and store it in y
Print the age from y
'''
import json
x = '{"name": "Emil", "age": 30}'
y = json.loads(x)
print(y["age"])