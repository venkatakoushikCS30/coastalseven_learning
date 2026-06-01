# NumPy Array Creation

## What is a NumPy Array?

A NumPy array is a data structure used to store multiple values in a single variable. Arrays can have one or more dimensions and allow efficient numerical computations.

Import NumPy before creating arrays:

```python
import numpy as np
```

---

# 1. Creating a One-Dimensional (1D) Array

A 1D array is a simple list of elements arranged in a single row.

### Syntax

```python
np.array([element1, element2, element3])
```

### Example

```python
import numpy as np

array = np.array([1, 2, 3, 4])

print(array)
print(type(array))
```

### Output

```text
[1 2 3 4]
<class 'numpy.ndarray'>
```

---

# 2. Creating a Two-Dimensional (2D) Array

A 2D array consists of rows and columns.

### Syntax

```python
np.array([
    [row1_elements],
    [row2_elements]
])
```

### Example

```python
import numpy as np

array = np.array([
    [1, 2, 3],
    [4, 5, 6]
])

print(array)
```

### Output

```text
[[1 2 3]
 [4 5 6]]
```

---

# 3. Creating a Three-Dimensional (3D) Array

A 3D array contains multiple 2D arrays stacked together.

### Syntax

```python
np.array([
    [
        [elements],
        [elements]
    ],
    [
        [elements],
        [elements]
    ]
])
```

### Example

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
    ],
    [
        ['S', 'T', 'U'],
        ['V', 'W', 'X'],
        ['Y', 'Z', '']
    ]
])

print(array)
```

---

# Checking Array Dimensions

Use `.ndim` to find the number of dimensions.

```python
print(array.ndim)
```

### Output

```text
3
```

---

# Checking Array Shape

Use `.shape` to find the size of each dimension.

```python
print(array.shape)
```

### Output

```text
(3, 3, 3)
```

Meaning:

- 3 blocks (depth)
- 3 rows per block
- 3 columns per row

---

# Summary

| Array Type | Example Shape | Dimensions (`ndim`) |
|------------|---------------|---------------------|
| 1D Array | `(4,)` | 1 |
| 2D Array | `(2, 3)` | 2 |
| 3D Array | `(3, 3, 3)` | 3 |

NumPy arrays are created using the `np.array()` function, and the number of nested lists determines the array's dimensions.