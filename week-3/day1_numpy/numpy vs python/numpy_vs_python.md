# Performance: NumPy vs Pure Python

---

## Why the Comparison Matters

Python is a high-level, dynamically-typed language — convenient to write, but not built for raw numerical throughput. NumPy exists specifically to close that gap. Understanding *why* NumPy is faster (not just *that* it is) helps you write better numerical code.

---

## How Pure Python Stores Data

A Python list like `[1, 2, 3, 4, 5]` does **not** store integers directly. It stores an array of **pointers**, each pointing to a separate Python object on the heap.

```
list → [ ptr → PyObject(1),
         ptr → PyObject(2),
         ptr → PyObject(3), ... ]
```

Every Python object carries overhead:
- **Reference count** (for garbage collection)
- **Type tag** (so Python knows it's an `int`)
- **The actual value**

A single Python integer occupies ~28 bytes. A list of one million integers consumes roughly **28 MB** just for the values, plus pointer array overhead.

---

## How NumPy Stores Data

A NumPy array stores values in a **contiguous block of typed memory** — a flat C array.

```
ndarray → [ 1 | 2 | 3 | 4 | 5 ]   ← raw int64 values, back to back
```

- Each `int64` value takes exactly **8 bytes**
- No per-element type tags or reference counts
- One million `int64` values = **8 MB** (vs ~28 MB in a Python list)
- The dtype is fixed for the whole array, checked once at creation

---

## The Interpreter Overhead Problem

When you write a Python loop:

```python
result = []
for x in data:
    result.append(x * 2)
```

For **every single iteration**, Python must:

1. Fetch the next element (dereference a pointer)
2. Check the type of the object
3. Look up the `__mul__` method for that type
4. Call the method (function call overhead)
5. Allocate a new Python integer object for the result
6. Append it to the list (possibly triggering a resize)

This sequence happens **millions of times** for large arrays. The cost is not the multiplication — it is all the surrounding machinery.

---

## What NumPy Does Instead

NumPy's operations are implemented in **compiled C** (and sometimes Fortran). When you call `array * 2`:

1. Python calls the C function once
2. The C function loops over raw memory at full CPU speed
3. A single new array is returned

The type check and method dispatch happen **once**, not per element. The inner loop is pure C — no Python objects, no dynamic dispatch, no allocations per step.

---

## SIMD: Doing Multiple Operations per Clock Cycle

Modern CPUs support **SIMD** (Single Instruction, Multiple Data) — hardware instructions that process several values simultaneously in one CPU cycle.

```
Normal:  multiply a₁, multiply a₂, multiply a₃, multiply a₄  (4 cycles)
SIMD:    multiply [a₁, a₂, a₃, a₄] in one instruction         (1 cycle)
```

NumPy's C code is compiled to take advantage of SIMD (SSE2, AVX, AVX-512 depending on hardware). A Python loop cannot benefit from SIMD because the interpreter processes one Python object at a time, and those objects are not laid out contiguously in memory.

---

## Cache Locality

Modern CPUs are far faster than RAM. They use small, ultra-fast **cache memory** (L1/L2/L3) to keep recently used data close to the processor.

Cache works best when data is **contiguous** — reading one value pre-loads neighboring values automatically (cache line prefetching).

| Data structure | Memory layout | Cache behavior |
|---|---|---|
| Python list | Scattered pointers → scattered objects | Poor — each dereference is a potential cache miss |
| NumPy array | Contiguous block | Excellent — sequential access maps perfectly to prefetching |

For large arrays, cache misses dominate runtime. NumPy's layout minimizes them; Python lists maximize them.

---

## Measuring Performance: `timeit`

The standard way to benchmark Python code is the `timeit` module. It runs a snippet many times and returns the best (or average) elapsed time, minimizing noise from OS scheduling.

```python
import timeit

# Pure Python
python_time = timeit.timeit(
    "result = [x**2 for x in data]",
    setup="data = list(range(1_000_000))",
    number=10
)

# NumPy
numpy_time = timeit.timeit(
    "result = arr**2",
    setup="import numpy as np; arr = np.arange(1_000_000)",
    number=10
)
```

The `number` parameter controls how many repetitions are averaged. For micro-benchmarks, use large values (100–1000). For slow operations, even 10 is enough.

In Jupyter notebooks, the `%%timeit` cell magic does the same thing more conveniently.

---

## Typical Speedup Ranges

The speedup depends on operation type and array size. Rough real-world ranges:

| Operation | Typical NumPy speedup over Python |
|---|---|
| Element-wise arithmetic (`+`, `*`, `**`) | 50× – 200× |
| Math functions (`sqrt`, `exp`, `log`) | 50× – 300× |
| Aggregations (`sum`, `mean`, `max`) | 50× – 150× |
| Sorting | 5× – 30× |
| Boolean masking / filtering | 10× – 100× |

Speedup grows with array size. For very small arrays (< ~100 elements), Python can actually be faster because NumPy has a fixed overhead for each call (memory allocation, dtype checking, function dispatch into C).

---

## When NumPy is NOT Faster

NumPy has overhead per operation, not per element. This creates situations where it underperforms:

| Situation | Why Python can win |
|---|---|
| Tiny arrays (< ~50 elements) | NumPy's fixed call overhead exceeds loop cost |
| Non-numerical data | NumPy works on fixed-type numbers; Python lists handle anything |
| Operations NumPy doesn't support | Custom logic may require Python loops anyway |
| Chained operations with large intermediates | Each NumPy op allocates a new array; can stress memory |

---

## Memory Usage Comparison

| Collection | 1M integers | Notes |
|---|---|---|
| Python list | ~28 MB (values) + ~8 MB (pointers) | Each int is a full object |
| NumPy `int64` array | ~8 MB | Raw 8-byte values, no overhead |
| NumPy `int32` array | ~4 MB | Half the size — choose dtype wisely |

Memory matters for performance because less data means fewer cache misses and faster transfers between RAM and CPU.

---

## Summary: Why NumPy Wins

| Factor | Pure Python | NumPy |
|---|---|---|
| Memory layout | Scattered pointers | Contiguous typed buffer |
| Per-element overhead | Type check + dispatch every iteration | None — checked once |
| Execution | Python interpreter loop | Compiled C loop |
| SIMD utilization | None | Automatic via compiler |
| Cache efficiency | Poor (pointer chasing) | Excellent (sequential access) |
| Memory per element | ~28 bytes | 4–8 bytes |

NumPy's performance advantage is not a single trick — it is the compounded effect of better memory layout, compiled execution, hardware SIMD, and cache efficiency all working together.

---

## Key Takeaways

- Python lists store pointers to objects; NumPy arrays store raw typed values contiguously.
- The Python interpreter's per-iteration overhead (type checks, method dispatch, allocations) is the primary cost of loops — not the arithmetic itself.
- NumPy executes loops in compiled C, dispatching into the loop **once** per operation.
- SIMD and cache locality multiply the advantage further on modern hardware.
- Use `timeit` to measure; never guess at performance.
- For small arrays, NumPy's fixed call overhead can make it slower than a Python loop.