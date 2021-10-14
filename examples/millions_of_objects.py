#!/usr/bin/env python3
# coding: utf-8


from recordclass import dataobject
from time import time
from random import randrange
import sys
import gc

ijw = [(randrange(100), randrange(100), randrange(1000)) for _ in range(10000000)]

class EdgeDO(dataobject, fast_new=True):
    __fields__ = 'node1', 'node2', 'weight'

class EdgeSlots:
    __slots__ = 'node1', 'node2', 'weight'

    def __init__(self, node1, node2, weight):
         self.node1 = node1
         self.node2 = node2
         self.weight = weight
            
    def __str__(self):
        return f'EdgeSlots(node1={self.node1}, node2={self.node2}, weight={self.weight})'
            
def list_size(lst):
    return sum(sys.getsizeof(o) for o in lst)

def test(C):
    for args in ijw:
        obj = C(*args)
        prev = obj

        
print('__slots__ timinig:')
t0 = time()
list_slots = [EdgeSlots(*args) for args in ijw]
t1 = time()
print(t1 - t0)
print(list_slots[0])
size_list_slots = list_size(list_slots) / 1000000
print('size (__slots__): ', size_list_slots)

del list_slots[:]
del list_slots

print('dataobject timinig:')
t0 = time()
list_do = [EdgeDO(*args) for args in ijw]
t1 = time()
print(list_do[0])
print(t1 - t0)
size_list_do = list_size(list_do) / 1000000
print('size (dataobject):', size_list_do)

del list_do[:]
del list_do

print((size_list_do/size_list_slots)*100, "%")

t0 = time()
test(EdgeDO)
t1 = time()
print(t1-t0)

t0 = time()
test(EdgeSlots)
t1 = time()
print(t1-t0)





