# Accessing Elements in a 3D NumPy Array

## Overview

NumPy arrays can have multiple dimensions. In a 3D array, data is organized as:

```text
Layer → Row → Column
```

To access a specific element, use:

```python
array[layer, row, column]
```

---

# Example Array

```python
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
```

### Structure

```text
Layer 0
-------
[A B C]
[D E F]
[G H I]

Layer 1
-------
[J K L]
[M N O]
[P Q R]
```

---

# Accessing a Single Element

## Syntax

```python
array[layer, row, column]
```

### Example

```python
print(array[1, 1, 2])
```

### Breakdown

```text
Layer 1 → ['M', 'N', 'O']
Row 1   → ['M', 'N', 'O']
Column 2 → 'O'
```

### Output

```text
O
```

---

# Forming a Word Using Array Elements

Multiple elements can be accessed and combined.

### Example

```python
word = array[0, 2, 1] + array[0, 2, 2]
print(word)
```

### Breakdown

```text
array[0, 2, 1] → H
array[0, 2, 2] → I
```

### Result

```text
HI
```

### Output

```text
HI
```

---

# Index Reference

For Layer 0:

```text
[
    ['A', 'B', 'C'],  # Row 0
    ['D', 'E', 'F'],  # Row 1
    ['G', 'H', 'I']   # Row 2
]
```

| Element | Index |
|----------|---------|
| A | [0,0,0] |
| B | [0,0,1] |
| C | [0,0,2] |
| D | [0,1,0] |
| E | [0,1,1] |
| F | [0,1,2] |
| G | [0,2,0] |
| H | [0,2,1] |
| I | [0,2,2] |

---

# Summary

- A 3D NumPy array is accessed using `array[layer, row, column]`.
- Indexing starts from `0`.
- Individual elements can be retrieved directly.
- Multiple elements can be combined to create strings or perform operations.
- Understanding layer, row, and column positions is essential when working with multidimensional arrays.