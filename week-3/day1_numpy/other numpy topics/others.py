#1. Comparison Operators
import numpy as np

scores = np.array([91,55,100,73,82,64])

print(scores == 100)

print(scores >= 60)

scores[scores < 60] = 0

print(scores)

#2. Aggregate Functions

array = np.array([
    [1,2,3,4,5],
    [6,7,8,9,10]
])

print(np.sum(array, axis=0))
print(np.sum(array, axis=1))

print(np.mean(array))
print(np.std(array))
print(np.var(array))

print(np.negative(array))

print(np.argmax(array))
print(np.argmin(array))

#3. Filtering Data


ages = np.array([
    [21,17,19,20,30,16,18,65],
    [39,22,15,99,18,19,20,21]
])

teenagers = ages[ages < 18]
print(teenagers)

adults = ages[(ages >= 18) & (ages < 65)]
print(adults)

seniors = ages[ages >= 65]
print(seniors)

evens = ages[ages % 2 == 0]
print(evens)

#4. np.where() Function

ages = np.array([
    [21,17,19,20],
    [39,22,15,99]
])

adults = np.where(ages >= 18, ages, 'Minor')

print(adults)