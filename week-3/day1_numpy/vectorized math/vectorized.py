#1. Scalar Arithmetic
import numpy as np

array = np.array([1,2,3])

print(array + 1)
print(array - 2)
print(array * 2)
print(array / 2)
print(array ** 2)

#2. Vectorized Functions

array = np.array([1,2,3])

print(np.sqrt(array))

arr2 = np.array([1.23,2.65,9.9897])

print(np.round(arr2))
print(np.floor(arr2))
print(np.ceil(arr2))

print(np.pi)

#3. Array Operations
array1 = np.array([1,2,3])
array2 = np.array([4,5,6])

print(array1 + array2)
print(array1 - array2)
print(array1 * array2)
print(array1 / array2)
print(array1 ** array2)