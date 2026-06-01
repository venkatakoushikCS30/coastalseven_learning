# NumPy Stacking & Reshaping

---

## Part 1 — Stacking Arrays

Stacking combines multiple arrays into one by joining them along an axis. The input arrays are passed as a **tuple or list**, not as separate arguments.

### `np.hstack` — Horizontal Stack

Joins arrays **side by side** along the column axis (axis=1 for 2-D; axis=0 for 1-D).

```
[1, 2, 3]  +  [4, 5, 6]  →  [1, 2, 3, 4, 5, 6]
```

For 1-D arrays, hstack simply **concatenates** them into a longer 1-D array. For 2-D arrays, it appends columns:

```
[[1, 2],      [[5, 6],      [[1, 2, 5, 6],
 [3, 4]]  +    [7, 8]]  →    [3, 4, 7, 8]]
```

**Shape rule:** all arrays must have the same number of **rows** (same shape on every axis except the column axis).

---

### `np.vstack` — Vertical Stack

Joins arrays **on top of each other** along the row axis (axis=0).

```
[1, 2, 3]        [[1, 2, 3],
     +        →   [4, 5, 6]]
[4, 5, 6]
```

1-D arrays are treated as **single-row 2-D arrays** before stacking, so the result is always at least 2-D.

**Shape rule:** all arrays must have the same number of **columns** (same shape on every axis except the row axis).

---

### Stacking Comparison

| Function | Direction | Axis used | 1-D result shape |
|---|---|---|---|
| `np.hstack` | Left → Right | axis=0 (1-D) / axis=1 (2-D+) | `(n+m,)` |
| `np.vstack` | Top → Bottom | axis=0 | `(2, n)` for two 1-D arrays |
| `np.stack` | New axis | configurable | adds a new dimension |
| `np.concatenate` | Any axis | configurable | general-purpose |

`hstack` and `vstack` are convenience wrappers around `np.concatenate`. For anything beyond simple horizontal/vertical joining, `np.concatenate(arrays, axis=n)` gives full control.

---

## Part 2 — Reshaping Arrays

Reshaping changes an array's **shape** without changing its **data** or **total number of elements**. The data is never copied or reordered — only the way NumPy interprets the memory layout changes.

### The Fundamental Constraint

```
product of old shape  =  product of new shape
```

An array of 6 elements can become `(2,3)`, `(3,2)`, `(6,1)`, `(1,6)`, or `(6,)` — never `(4,2)` (that would require 8 elements).

---

### `array.reshape(rows, cols)`

Returns a **new view** of the array with the given shape. The original array is unchanged.

```
[1, 2, 3, 4, 5, 6]  →  reshape(3, 2)  →  [[1, 2],
                                            [3, 4],
                                            [5, 6]]
```

Elements are filled **row by row** (C order, left to right, top to bottom) by default.

#### The `-1` shortcut

One dimension can be given as `-1`, telling NumPy to **calculate it automatically**:

```python
a.reshape(3, -1)   # NumPy infers: 6 / 3 = 2 columns → (3, 2)
a.reshape(-1)      # Flatten to 1-D → (6,)
```

#### View vs Copy

`reshape` returns a **view** whenever possible — it points to the same memory as the original. Modifying the reshaped array modifies the original too. Use `.copy()` explicitly if you need independence.

---

### `array.flatten()`

Collapses any N-dimensional array down to a **1-D array**.

```
[[1, 2],
 [3, 4],   →  flatten()  →  [1, 2, 3, 4, 5, 6]
 [5, 6]]
```

Key property: `flatten()` always returns a **copy** — changes to the flattened array never affect the original. This is the main distinction from `ravel()`:

| Method | Returns | Modifying result affects original? |
|---|---|---|
| `.flatten()` | Always a copy | No |
| `.ravel()` | View when possible | Yes (if view) |

Use `flatten()` when you need a safe independent 1-D copy. Use `ravel()` for memory efficiency when you only need to read the values.

---

## Shape Manipulation Summary

| Operation | Method | Changes data? | Returns |
|---|---|---|---|
| Combine side by side | `np.hstack` | No | New array |
| Combine top to bottom | `np.vstack` | No | New array |
| Change shape | `.reshape(s)` | No | View (usually) |
| Collapse to 1-D (copy) | `.flatten()` | No | Copy |
| Collapse to 1-D (view) | `.ravel()` | No | View (usually) |
| Add a new axis | `np.newaxis` / `np.expand_dims` | No | View |
| Remove size-1 axes | `.squeeze()` | No | View |

---

## Key Takeaways

- `hstack` appends columns; `vstack` appends rows — both require compatible shapes on the non-joining axis.
- `reshape` reinterprets memory layout; the total element count must stay the same.
- Use `-1` in `reshape` to let NumPy infer one dimension automatically.
- `flatten()` is safe (copy); `ravel()` is fast (view) — choose based on whether you need independence from the original.
- Reshaping and stacking never reorder or duplicate data in memory; they change how NumPy walks the same underlying buffer.