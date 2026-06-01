import numpy as np

rng = np.random.default_rng(seed=1)

# random integer
print(rng.integers(1,7))

# multiple random integers
print(rng.integers(1,101,size=5))

# 2D random integers
print(rng.integers(1,101,size=(3,4)))

# random floating values
print(np.random.uniform(1,10,size=(3,4)))


rng = np.random.default_rng(seed=1)

array = np.array([1,2,3,4,5])

np.random.shuffle(array)
print(array)

print(rng.choice(array,size=3))