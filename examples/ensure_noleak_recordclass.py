#!/usr/bin/env python

import random
import time
import psutil
import os

from recordclass import recordclass

def memory_usage_psutil():
    # return the memory usage in percentage like top
    process = psutil.Process(os.getpid())
    mem = process.memory_percent()
    return mem

X = recordclass('x', ['a','b','c'])

while True:
  a = X(str(random.randint(1000000,10000000)), random.randint(1,1000),
            'a' * random.randint(1,1024))
  del a
  time.sleep(.01)
  print(memory_usage_psutil())
  
