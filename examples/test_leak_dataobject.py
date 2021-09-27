#!/usr/bin/env python

import random
import time
import psutil
import os

from recordclass import make_dataclass, litelist

def memory_usage_psutil():
    # return the memory usage in percentage like top
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss
    return mem

Cls = make_dataclass('Cls', ['a','b','c'])

N = 1000000
while True:
    print(memory_usage_psutil())
    rnd = random.randint
    lst = litelist()
    for i in range(N):
        o = Cls(rnd(1,1024), rnd(1,1024), rnd(1,1024))
        lst.append(o)
    print(memory_usage_psutil())
    del a
    time.sleep(1.)
  
