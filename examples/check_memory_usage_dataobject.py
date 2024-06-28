#!/usr/bin/env python

import random
import time
import psutil
import os

from recordclass import make_dataclass, litelist

def memory_usage_psutil():
    # return the memory usage in percentage like top
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024**2
    return mem

Cls = make_dataclass('Cls', ['a','b','c','d','e','f','g','h'])

class Cls2:
    __slots__ = 'a','b','c','d','e','f','g','h'
    def __init__(self, a, b, c, d, e, f, g, h):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.g = g
        self.h = h

N = 100000
while True:
    print(memory_usage_psutil())
    rnd = random.randint
    # lst = litelist([])
    lst = []
    for i in range(N):
        # o = Cls(rnd(1,1024), rnd(1,1024), rnd(1,1024), 
        #         rnd(1,1024), rnd(1,1024), rnd(1,1024),
        #         rnd(1,1024), rnd(1,1024))
        o = Cls2(rnd(1,1024), rnd(1,1024), rnd(1,1024), 
                rnd(1,1024), rnd(1,1024), rnd(1,1024),
                rnd(1,1024), rnd(1,1024))
        lst.append(o)
    print(memory_usage_psutil())
    del lst
    time.sleep(0.2)
  
