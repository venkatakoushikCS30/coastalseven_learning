import numpy as np

a = np.array([1,2,3,4,5,6])

print(a.shape)

b = a.reshape(3,2)
print(b)

c = b.flatten()
print(c)