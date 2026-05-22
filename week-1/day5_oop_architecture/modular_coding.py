# #created a separate math_utils.py file and imported the functions here. - this is modular coding.
#modular coding - code is divided into modules
import utils
'''
different importing styles:
1. import math_utils
2. from math_utils import add, subtract
3. from math_utils import *

'''

print(utils.add(10, 5))
print(utils.subtract(10, 5))