# NumPy Vectorized Math

## What is Vectorization?

Vectorization means applying an operation **to every element of an array at once**, without writing an explicit Python loop. NumPy pushes these loops down into pre-compiled C code, making vectorized operations orders of magnitude faster than equivalent Python `for` loops.

The core idea: **operate on the whole array as if it were a single value.**

---

## 1. Scalar Arithmetic

A scalar (single number) combined with an array applies the operation **to every element independently**. This is a special case of broadcasting — the scalar is conceptually stretched to match the array's shape.

| Operation | Meaning | Example `[1,2,3]` |
|---|---|---|
| `array + s` | Add `s` to each element | `[2, 3, 4]` |
| `array - s` | Subtract `s` from each element | `[-1, 0, 1]` |
| `array * s` | Multiply each element by `s` | `[2, 4, 6]` |
| `array / s` | Divide each element by `s` | `[0.5, 1.0, 1.5]` |
| `array ** s` | Raise each element to power `s` | `[1, 4, 9]` |

### How it works internally

NumPy wraps the scalar into a 0-dimensional array and broadcasts it. The arithmetic is executed in a single C-level loop with no Python overhead per element. The output dtype follows **type promotion rules** — e.g., integer array divided by an integer scalar produces a `float64` array.

---

## 2. Vectorized Universal Functions (ufuncs)

A **ufunc** (universal function) is a function that operates element-wise on an array and returns a new array of the same shape. NumPy's math functions are all ufuncs.

### What makes a ufunc special

- Operates on **entire arrays** in one call
- Implemented in compiled C — no Python loop
- Supports **broadcasting**, **type casting**, and **output arrays** (`out=` parameter)
- Can operate on scalars, 1-D, 2-D, or N-D arrays uniformly

### Common mathematical ufuncs

| Function | Description |
|---|---|
| `np.sqrt(x)` | Element-wise square root — equivalent to `x ** 0.5` |
| `np.round(x)` | Round each element to the nearest integer (banker's rounding) |
| `np.floor(x)` | Round down to the nearest integer (toward −∞) |
| `np.ceil(x)` | Round up to the nearest integer (toward +∞) |
| `np.abs(x)` | Absolute value of each element |
| `np.exp(x)` | Euler's number raised to each element: eˣ |
| `np.log(x)` | Natural logarithm of each element |
| `np.sin(x)` / `np.cos(x)` | Trigonometric functions element-wise |

### Rounding distinctions

Given `[1.23, 2.65, 9.9897]`:

| Function | Result | Rule |
|---|---|---|
| `np.round` | `[1., 3., 10.]` | Nearest integer; ties go to nearest even |
| `np.floor` | `[1., 2., 9.]` | Always toward −∞ |
| `np.ceil` | `[2., 3., 10.]` | Always toward +∞ |

`floor` and `ceil` are **not symmetric around zero** for negative numbers:
- `floor(-1.5)` → `-2` (more negative)
- `ceil(-1.5)` → `-1` (less negative)

### Constants

`np.pi` is not a function — it is a **floating-point constant** (`3.141592653589793`) stored in NumPy's namespace. Similarly useful constants: `np.e`, `np.inf`, `np.nan`.

---

## 3. Element-wise Array Operations

When two arrays have the **same shape**, arithmetic operators apply **element-by-element**, pairing elements at matching indices.

```
array1 = [1, 2, 3]
array2 = [4, 5, 6]
         ↕  ↕  ↕   ← each position is paired
```

| Operation | Formula per element | Result |
|---|---|---|
| `array1 + array2` | `aᵢ + bᵢ` | `[5, 7, 9]` |
| `array1 - array2` | `aᵢ - bᵢ` | `[-3, -3, -3]` |
| `array1 * array2` | `aᵢ × bᵢ` | `[4, 10, 18]` |
| `array1 / array2` | `aᵢ ÷ bᵢ` | `[0.25, 0.4, 0.5]` |
| `array1 ** array2` | `aᵢ ^ bᵢ` | `[1, 32, 729]` |

> **Note:** `array1 * array2` is element-wise multiplication, **not** matrix multiplication. For the dot product or matrix product, use `np.dot()` or the `@` operator.

---

## Operator Overloading

Python's arithmetic operators (`+`, `-`, `*`, `/`, `**`) are **overloaded** on NumPy arrays. They map to underlying ufuncs:

| Operator | Equivalent ufunc |
|---|---|
| `a + b` | `np.add(a, b)` |
| `a - b` | `np.subtract(a, b)` |
| `a * b` | `np.multiply(a, b)` |
| `a / b` | `np.true_divide(a, b)` |
| `a ** b` | `np.power(a, b)` |

Calling the ufunc directly gives access to extra parameters (like `out=`, `where=`, `casting=`), but the operator syntax is preferred for readability.

---

## Why Vectorization is Fast

| Approach | Per-element cost |
|---|---|
| Python `for` loop | Interpreter overhead + dynamic type checking each iteration |
| NumPy vectorized op | Single C loop over a contiguous memory block, SIMD-optimized |

NumPy arrays store data in **contiguous, typed memory** (unlike Python lists, which store pointers to objects). This layout allows the CPU to use **SIMD instructions** (Single Instruction, Multiple Data) — processing multiple elements per CPU clock cycle.

---

## Key Takeaways

- Scalar operations broadcast the scalar across all elements — no loop needed.
- Ufuncs are the engine behind NumPy's math: compiled, broadcasting-aware, and shape-preserving.
- `floor`, `ceil`, and `round` are distinct rounding strategies — not interchangeable.
- Element-wise array operations require matching shapes (or broadcastable shapes).
- Operators like `+` and `*` are syntactic sugar over ufuncs.
- Vectorization is fast because computation moves from the Python interpreter into optimized C/SIMD routines operating on contiguous typed memory.