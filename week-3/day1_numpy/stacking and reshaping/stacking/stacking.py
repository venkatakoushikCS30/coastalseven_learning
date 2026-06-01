import numpy as np

arr = np.array([1,2,3])

arr2 = np.array([4,5,6])

# horizontal stack
arr3 = np.hstack((arr,arr2))
print(arr3)

# vertical stack
arr4 = np.vstack((arr,arr2))
print(arr4)