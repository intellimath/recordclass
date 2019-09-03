#!/usr/bin/env python

from random import randint
import time
import psutil
import os

from recordclass import make_dataclass

def memory_usage_psutil():
    # return the memory usage in percentage like top
    process = psutil.Process(os.getpid())
    mem = process.memory_percent()
    return mem

X = make_dataclass('X', fields=['a','b','c'])
#X = new_datatype('X', fields=3)

while True:
  a = X(randint(1,100), randint(1,100), randint(1,100))
  x = a.a
  a.a = 1
  y = a.b
  a.b = 2
  z = a.c
  a.c = 2
  r = repr(a)
  del a
  time.sleep(.01)
  print(memory_usage_psutil())
  
