# NumPy Broadcasting

## What is Broadcasting?

Broadcasting is NumPy's mechanism for performing arithmetic operations on arrays of **different shapes**. Instead of requiring arrays to have identical shapes, NumPy "stretches" (broadcasts) the smaller array across the larger one so the operation makes sense element-wise — without actually copying any data in memory.

---

## The Broadcasting Rules

NumPy compares the shapes of two arrays **dimension by dimension, starting from the trailing (rightmost) dimension**, and works leftward. Two dimensions are compatible when:

1. They are **equal**, or
2. One of them is **1**

If neither condition holds, a `ValueError` is raised. If one array has fewer dimensions than the other, its shape is **padded with 1s on the left** before comparison.

### Rule Summary

| Condition | Result |
|---|---|
| Dimensions are equal | Used as-is |
| One dimension is `1` | Stretched to match the other |
| Neither equal nor `1` | Error — shapes are incompatible |

---

## Shape Compatibility Examples

### Example 1 — Scalar and Array
```
Array : (3, 4)
Scalar: ()        → padded to (1, 1) → broadcast to (3, 4)
Result: (3, 4)
```

### Example 2 — 1-D array with 2-D array
```
A: (5, 4)
B: (4,)   → padded to (1, 4) → broadcast to (5, 4)
Result: (5, 4)
```

### Example 3 — Row vector × Column vector (your code example)
```
arr1: (1, 10)
arr2: (10, 1)
Result: (10, 10)   ← outer product via broadcasting
```
Both dimensions satisfy the rule (one of them is `1` in each case), so each array is virtually stretched to `(10, 10)`.

### Example 4 — Incompatible shapes
```
A: (3, 4)
B: (3, 3)   ← trailing dims 4 and 3 are neither equal nor 1 → Error
```

---

## How Stretching Works (Conceptually)

Broadcasting **never physically duplicates data**. Internally, NumPy uses a stride of `0` for broadcast dimensions, so the same memory location is read repeatedly. This makes broadcasting:

- **Memory-efficient** — no extra allocation
- **Fast** — avoids Python-level loops entirely
- **Equivalent** to `np.tile` or `np.repeat` in result, but not in cost

---

## Visual Intuition

```
arr1 (1×10):   [1  2  3  4  5  6  7  8  9  10]

arr2 (10×1):   [1]         arr2 "spreads" right →    [1  1  1 ... 1 ]
               [2]                                    [2  2  2 ... 2 ]
               [3]                                    [3  3  3 ... 3 ]
               ...                                    ...
               [10]                                   [10 10 10 ... 10]

arr1 "spreads" down ↓:
               [1  2  3 ... 10]
               [1  2  3 ... 10]
               ...

Result (10×10) = element-wise product = multiplication table
```

---

## General Shape Inference Rule

Given two shapes, the output shape is determined by taking the **element-wise maximum** of the two shapes after left-padding the shorter shape with `1`s:

```
A: (      8, 1, 6, 1)
B: (7, 1, 6, 6, 1)   ← B has more dims; A is padded
A: (1, 8, 1, 6, 1)

Output: (7, 8, 6, 6, 1)
```

Each output dimension = `max(a_dim, b_dim)` when they are compatible.

---

## Common Use Cases

| Task | Shapes involved |
|---|---|
| Subtract row mean from each row | `(m, n) - (m, 1)` |
| Normalize columns | `(m, n) / (1, n)` or `(m, n) / (n,)` |
| Outer product | `(n, 1) * (1, m)` → `(n, m)` |
| Adding a bias to a batch | `(batch, features) + (features,)` |
| Distance matrix computation | `(n, 1, d) - (1, m, d)` → `(n, m, d)` |

---

## Key Takeaways

- Broadcasting operates on **shapes**, not values.
- Dimensions of size `1` are the "wildcard" — they match anything.
- Missing leading dimensions are implicitly `1`.
- The output shape is the **broadcast shape**: element-wise max of aligned dimensions.
- No data is copied — strides handle the illusion of expansion.