import numpy as np

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
    ]
])

# layer 1, row 1, column 2
print(array[1,1,2])

# forming a word
word = array[0,2,1] + array[0,2,2]
print(word)