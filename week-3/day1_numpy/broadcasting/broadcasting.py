import numpy as np

arr1 = np.array([[1,2,3,4,5,6,7,8,9,10]])

arr2 = np.array([
    [1],
    [2],
    [3],
    [4],
    [5],
    [6],
    [7],
    [8],
    [9],
    [10]
])

print(arr1.shape)
print(arr2.shape)

print(arr1 * arr2)