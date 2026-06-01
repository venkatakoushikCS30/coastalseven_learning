# NumPy Array Slicing

## Overview

Slicing allows you to extract specific portions of a NumPy array without modifying the original array.

The general slicing syntax is:

```python
array[start:end:step]
```

Where:

- `start` → starting index (inclusive)
- `end` → ending index (exclusive)
- `step` → interval between elements

---

# Example Array

```python
import numpy as np

array = np.array([
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16]
])
```

### Structure

```text
[
 [ 1,  2,  3,  4],
 [ 5,  6,  7,  8],
 [ 9, 10, 11, 12],
 [13, 14, 15, 16]
]
```

---

# 1. Row Slicing

## Example

```python
print(array[0:4:2])
```

### Explanation

```python
array[start:end:step]
```

```python
array[0:4:2]
```

- Start at row 0
- End before row 4
- Take every 2nd row

Selected rows:

```text
Row 0
Row 2
```

### Output

```text
[[ 1  2  3  4]
 [ 9 10 11 12]]
```

---

# 2. Column Slicing

## Example

```python
print(array[:, ::-2])
```

### Explanation

The first part:

```python
:
```

means:

```text
Select all rows
```

The second part:

```python
::-2
```

means:

```text
Start from the last column
Move backward
Take every 2nd column
```

Selected columns:

```text
Column 3 → 4, 8, 12, 16
Column 1 → 2, 6, 10, 14
```

### Output

```text
[[ 4  2]
 [ 8  6]
 [12 10]
 [16 14]]
```

---

# 3. Slicing Rows and Columns Together

## Example

```python
print(array[2:, 2:])
```

### Explanation

### Rows

```python
2:
```

Select rows from index 2 onward:

```text
Row 2
Row 3
```

### Columns

```python
2:
```

Select columns from index 2 onward:

```text
Column 2
Column 3
```

Selected section:

```text
[
 [11, 12],
 [15, 16]
]
```

### Output

```text
[[11 12]
 [15 16]]
```

---

# Understanding 2D Slicing

A 2D NumPy array uses:

```python
array[row_slice, column_slice]
```

### Examples

```python
array[:, :]
```

All rows and all columns.

---

```python
array[1:3, :]
```

Rows 1 to 2, all columns.

---

```python
array[:, 1:3]
```

All rows, columns 1 to 2.

---

```python
array[1:3, 1:3]
```

Rows 1 to 2 and columns 1 to 2.

---

# Common Slice Patterns

| Slice | Meaning |
|---------|---------|
| `:` | All elements |
| `1:` | From index 1 to end |
| `:3` | From start to index 2 |
| `::2` | Every second element |
| `::-1` | Reverse order |
| `::-2` | Reverse order, every second element |

---

# Summary

- NumPy slicing follows the pattern `start:end:step`.
- For 2D arrays, use `array[row_slice, column_slice]`.
- `:` selects all rows or columns.
- Negative steps allow reverse traversal.
- Slicing creates a subset of the array without manually looping through elements.
- Combining row and column slices makes it easy to extract specific sections of large datasets.