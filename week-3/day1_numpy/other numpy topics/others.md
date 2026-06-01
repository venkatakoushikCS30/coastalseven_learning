# NumPy: Comparison, Aggregation, Filtering & `np.where`

---

## 1. Comparison Operators

NumPy's comparison operators work **element-wise**, just like arithmetic operators. Comparing an array against a scalar (or another array) produces a **boolean array** of the same shape — one `True`/`False` per element.

### Supported operators

| Operator | Meaning |
|---|---|
| `==` | Equal to |
| `!=` | Not equal to |
| `>` | Greater than |
| `>=` | Greater than or equal to |
| `<` | Less than |
| `<=` | Less than or equal to |

```
scores = [91, 55, 100, 73, 82, 64]

scores == 100  →  [False, False,  True, False, False, False]
scores >= 60   →  [ True, False,  True,  True,  True,  True]
```

The result is a `dtype=bool` array. It can be used immediately for filtering, counting, or logical operations.

### Boolean arrays as masks

A boolean array can be used directly to **index** into the original array. This is called **boolean indexing** or **masking**. Only elements where the mask is `True` are selected or modified.

```
scores[scores < 60] = 0
```

This reads as: *"in-place, set every element of `scores` where the value is less than 60 to 0."* The original array is mutated — no copy is made.

---

## 2. Aggregate Functions

Aggregate functions **reduce** an array to a smaller result — collapsing elements across rows, columns, or the entire array into summary statistics.

### The `axis` parameter

`axis` controls **which dimension gets collapsed**:

| `axis` value | Meaning | For a 2-D array |
|---|---|---|
| `None` (default) | Collapse everything | Single scalar result |
| `0` | Collapse along rows (down) | One result per **column** |
| `1` | Collapse along columns (across) | One result per **row** |

```
array = [[1, 2, 3, 4,  5],
         [6, 7, 8, 9, 10]]

np.sum(axis=0) → [7, 9, 11, 13, 15]   ← column totals
np.sum(axis=1) → [15, 40]              ← row totals
```

A useful mental model: `axis=0` collapses **rows** (you move downward); `axis=1` collapses **columns** (you move rightward).

### Common aggregate functions

| Function | Description |
|---|---|
| `np.sum(a)` | Total of all elements |
| `np.mean(a)` | Arithmetic mean (average) |
| `np.std(a)` | Standard deviation — spread of values around the mean |
| `np.var(a)` | Variance — standard deviation squared |
| `np.min(a)` / `np.max(a)` | Smallest / largest value |
| `np.argmin(a)` / `np.argmax(a)` | **Index** of the smallest / largest value |
| `np.median(a)` | Middle value when sorted |
| `np.cumsum(a)` | Running total (cumulative sum) |
| `np.prod(a)` | Product of all elements |

### `np.argmin` and `np.argmax`

These return the **flat index** of the minimum/maximum element. For a 2-D array, the index treats the array as if it were flattened to 1-D first:

```
array = [[1, 2, 3, 4,  5],
         [6, 7, 8, 9, 10]]

np.argmax(array) → 9   ← index 9 in the flattened array is value 10
np.argmin(array) → 0   ← index 0 is value 1
```

To get row/column indices directly, pass `axis=0` or `axis=1`, or use `np.unravel_index`.

### `np.negative`

Not an aggregate — it returns a new array where every element is negated (sign flipped). Equivalent to `array * -1`. The original array is unchanged.

### `std` vs `var`

- **Variance** (`var`) measures average squared deviation from the mean — in squared units.
- **Standard deviation** (`std`) is the square root of variance — in the same units as the data.
- `std` is more interpretable; `var` is more convenient mathematically.

By default, both compute **population** statistics (dividing by N). Pass `ddof=1` for sample statistics (dividing by N−1).

---

## 3. Filtering Data

Filtering extracts elements that satisfy a condition. NumPy uses **boolean indexing**: a boolean array (the mask) is passed inside square brackets, and only `True`-position elements are returned.

### How boolean indexing works

```
ages = [[21, 17, 19, 20, 30, 16, 18, 65],
        [39, 22, 15, 99, 18, 19, 20, 21]]

ages < 18  →  a boolean array of the same shape
ages[ages < 18]  →  a 1-D array of only the matching values
```

Regardless of the original shape, the result of boolean indexing is always **1-D** — it's a flat list of matching values, not a sub-array preserving shape.

### Combining conditions

Multiple conditions are combined with **bitwise operators** (not Python's `and`/`or`):

| Operator | Meaning |
|---|---|
| `&` | AND — both conditions must be True |
| `\|` | OR — at least one condition must be True |
| `~` | NOT — inverts the boolean array |

Each condition **must be wrapped in parentheses** due to Python's operator precedence:

```python
adults = ages[(ages >= 18) & (ages < 65)]
```

Without parentheses, `>=` and `<` would bind after `&`, causing a TypeError.

### Modulo filtering

```python
evens = ages[ages % 2 == 0]
```

`%` is the modulo (remainder) operator, applied element-wise. Elements where `value % 2 == 0` are even.

---

## 4. `np.where()`

`np.where` is a vectorized **if-else** — it applies a condition to every element and returns one value if `True`, another if `False`, all without a Python loop.

### Signature

```python
np.where(condition, value_if_true, value_if_false)
```

All three arguments are broadcast against each other. The result has the same shape as `condition`.

```
ages = [[21, 17, 19, 20],
        [39, 22, 15, 99]]

np.where(ages >= 18, ages, 'Minor')
→ [['21', '17' → 'Minor', '19', '20'],
   ['39', '22', '15' → 'Minor', '99']]
```

### dtype coercion

When the two output values are of different types (e.g., integers and strings), NumPy must produce a single array with one dtype. It promotes to the most general type that fits both — in this case, `dtype='<U21'` (Unicode string), converting the integers to their string representations.

This is often surprising. If you want to preserve numeric values, use a numeric sentinel instead:

```python
np.where(ages >= 18, ages, -1)   # returns int array, -1 for minors
```

### `np.where` with one argument

Called with only a condition (`np.where(condition)`), it behaves like `np.nonzero` — returning the **indices** where the condition is `True`, as a tuple of arrays (one per axis):

```python
np.where(ages >= 65)   # → (array of row indices, array of col indices)
```

### Comparison: boolean indexing vs `np.where`

| Feature | Boolean indexing | `np.where` |
|---|---|---|
| Returns values | Yes — filtered 1-D array | Yes — full-shape array |
| Preserves shape | No | Yes |
| Supports else value | No | Yes |
| In-place assignment | Yes (`arr[mask] = val`) | No |

Use boolean indexing when you want to **extract** a subset. Use `np.where` when you want to **transform** the full array conditionally.

---

## Key Takeaways

- Comparison operators produce boolean arrays element-wise — the foundation of all filtering.
- Aggregate functions reduce arrays along a chosen `axis`; omitting `axis` collapses everything to a scalar.
- `argmax`/`argmin` return **indices**, not values — and use flat indexing for N-D arrays by default.
- Boolean indexing always returns a **1-D** result regardless of input shape.
- Combine conditions with `&`, `|`, `~` — never `and`/`or` — and always wrap each condition in parentheses.
- `np.where(cond, a, b)` is a vectorized ternary that preserves shape; mismatched types trigger dtype promotion.