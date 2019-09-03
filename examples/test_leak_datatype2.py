#!/usr/bin/env python

from random import randint
import time
import psutil
import os
import gc

from recordclass import make_dataclass, make_arrayclass

def memory_usage_psutil():
    # return the memory usage in percentage like top
    process = psutil.Process(os.getpid())
    mem = process.memory_percent()
    return mem

N = 1000000
X = make_dataclass('X', fields=['a','b','c'])
Y = make_arrayclass('Y', fields=N)

gc.collect()
time.sleep(1.)
print(memory_usage_psutil())

lst = Y()
for i in range(N):
  lst[i] = X(1,2,3)

gc.collect()
time.sleep(1.)
print(memory_usage_psutil())

del lst
del Y
del X
gc.collect()
time.sleep(1.)
print(memory_usage_psutil())

