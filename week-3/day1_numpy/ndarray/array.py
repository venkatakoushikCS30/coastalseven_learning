import numpy as np

# 1D array
array = np.array([1, 2, 3, 4])

print(array)
print(type(array))


array = np.array([
    [
        ['A', 'B', 'C'],
        ['D', 'E', 'F'],
        ['G', 'H', 'I']
    ],
    [
        ['J', 'K', 'L'],
        ['M', 'N', 'O'],
        ['P', 'Q', 'R']
    ],
    [
        ['S', 'T', 'U'],
        ['V', 'W', 'X'],
        ['Y', 'Z', '']
    ]
])

print(array.ndim)
print(array.shape)