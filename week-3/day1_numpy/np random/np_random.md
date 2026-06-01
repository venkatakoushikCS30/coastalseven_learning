# NumPy Random — `np.random`

## Overview

NumPy provides two layers of random number generation:

| Layer | API | Status |
|---|---|---|
| Legacy | `np.random.function()` | Still works; not recommended for new code |
| Modern | `np.random.default_rng()` → Generator object | Recommended; statistically superior |

The modern API separates the **random number generator** from the functions that use it, giving you full control over reproducibility and state.

---

## Random Number Generators (RNGs)

### What is an RNG?

Computers cannot produce truly random numbers. Instead, they use a **pseudo-random number generator (PRNG)** — a deterministic algorithm that produces a sequence of numbers that *appears* random. Given the same starting point, it always produces the same sequence.

### Seeds

A **seed** is the starting value fed into the PRNG algorithm. It fully determines the entire output sequence.

```
same seed → same sequence (reproducible)
no seed   → uses system entropy → different each run
```

Seeds are essential for:
- Reproducible experiments and research
- Debugging randomized code
- Sharing results others can replicate

### `np.random.default_rng(seed)`

Creates a **Generator** object backed by the **PCG64 algorithm** (Permuted Congruential Generator). PCG64 is statistically stronger than NumPy's legacy Mersenne Twister — it passes more randomness tests and has better performance.

```python
rng = np.random.default_rng(seed=1)
```

All random calls are made **on this object**, not on `np.random` globally. Each Generator maintains its own internal state independently.

---

## Generating Random Integers

### `rng.integers(low, high, size=None)`

Generates random integers from `low` (inclusive) to `high` (**exclusive**).

| Parameter | Role |
|---|---|
| `low` | Minimum value (included) |
| `high` | Upper bound (excluded) |
| `size` | Output shape — omit for scalar, int for 1-D, tuple for N-D |

### Shape control via `size`

| `size` value | Output |
|---|---|
| omitted / `None` | Single integer (scalar) |
| `5` | 1-D array of 5 integers |
| `(3, 4)` | 2-D array, 3 rows × 4 columns |
| `(2, 3, 4)` | 3-D array |

> **Off-by-one gotcha:** `rng.integers(1, 7)` simulates a die roll — it returns 1 through 6, never 7. To include `high`, pass `endpoint=True`.

---

## Generating Random Floats

### `np.random.uniform(low, high, size)`

Draws samples from a **uniform distribution** — every value in `[low, high)` is equally likely.

- Belongs to the **legacy API** (`np.random.uniform`, not called on a Generator object)
- Returns `float64` values
- `size` follows the same shape rules as `rng.integers`

### Uniform vs other distributions

`uniform` is just one distribution. NumPy supports many others on the Generator object:

| Method | Distribution |
|---|---|
| `rng.uniform(low, high)` | Flat — all values equally likely |
| `rng.normal(loc, scale)` | Bell curve (Gaussian) |
| `rng.exponential(scale)` | Exponential decay |
| `rng.binomial(n, p)` | Count of successes in `n` trials |
| `rng.poisson(lam)` | Count of rare events |

---

## Shuffling Arrays

### `np.random.shuffle(array)`

Randomly reorders the elements of an array **in-place** — the original array is mutated, nothing is returned.

- Operates on the **first axis** for multi-dimensional arrays (shuffles rows, not individual elements)
- Uses the **legacy global state**, not a Generator object
- Because it's in-place, the original variable reflects the shuffled order immediately

### In-place vs out-of-place

| Function | Modifies original | Returns new array |
|---|---|---|
| `np.random.shuffle(a)` | Yes | No (`None`) |
| `rng.permutation(a)` | No | Yes (new shuffled copy) |

Use `rng.permutation()` when you need to preserve the original array.

---

## Sampling from an Array

### `rng.choice(array, size, replace=True)`

Randomly picks elements from an existing array.

| Parameter | Default | Meaning |
|---|---|---|
| `array` | — | Source array (or int `n`, treated as `arange(n)`) |
| `size` | `None` | Number of samples / output shape |
| `replace` | `True` | Whether the same element can be picked more than once |

### With vs without replacement

- **With replacement** (`replace=True`): like drawing a card, putting it back, drawing again — duplicates possible.
- **Without replacement** (`replace=False`): like dealing cards — each element appears at most once. Requires `size ≤ len(array)`.

`rng.choice` also accepts a `p=` parameter — an array of probabilities summing to 1 — to make some elements more likely to be chosen than others.

---

## Legacy API vs Modern Generator API

| Feature | Legacy `np.random.*` | Modern `rng.*` |
|---|---|---|
| Algorithm | Mersenne Twister (MT19937) | PCG64 (default) |
| State | Single global state | Per-object state |
| Thread safety | No | Yes (independent objects) |
| Reproducibility | `np.random.seed(n)` affects all | Seed per Generator |
| Statistical quality | Good | Better |
| Recommended | No (new code) | Yes |

The legacy API still works and is widely seen in older code and tutorials. The key difference is that `np.random.seed()` sets a **global** state — any call anywhere in the program can disturb it. Generator objects are isolated.

---

## Key Takeaways

- Use `np.random.default_rng(seed)` to create a reproducible, isolated Generator.
- `rng.integers(low, high)` — high is **exclusive** by default.
- `size` controls output shape uniformly across all random functions.
- `np.random.shuffle` mutates **in-place**; use `rng.permutation` for a copy.
- `rng.choice` samples from an existing array, with or without replacement.
- The modern Generator API is statistically stronger and safer than the legacy `np.random.*` functions.