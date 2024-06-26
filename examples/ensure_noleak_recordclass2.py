#!/usr/bin/env python

import random
import time
import psutil
import os
import gc

from recordclass import recordclass
from collections import namedtuple

def memory_usage_psutil():
    # return the memory usage in percentage like top
    process = psutil.Process(os.getpid())
    mem = process.memory_percent()
    return mem

#X = recordclass('X', ['a','b','c'])
X = namedtuple('X', ['a','b','c'])

gc.collect()
time.sleep(1.)
print(memory_usage_psutil())

lst = []
for i in range(1000000):
  a = X(1,2,3)
  lst.append(a)
t = tuple(lst)
del lst

gc.collect()
time.sleep(1.)
print(memory_usage_psutil())

del t
gc.collect()
time.sleep(1.)
print(memory_usage_psutil())
