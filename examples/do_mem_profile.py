import sys
from memory_profiler import profile
from recordclass import dataobject
from random import random

class NodeSlots:
    __slots__ = 'ob', 'left', 'right'
    def __init__(self, ob, left, right):
        self.ob = ob
        self.left = left
        self.right = right

class NodeDO(dataobject):
    __fields__ = 'ob', 'left', 'right'
    
count = 0

def add_nodes_do(level):
    global count
    if level > 0:
        o = random()
        left = add_nodes_do(level-1)
        right = add_nodes_do(level-1)
        node = NodeDO(o, left, right)
        count += 1
    else:
        node = None
    return node

def add_nodes_slots(level):
    global count
    if level > 0:
        o = random()
        left = add_nodes_slots(level-1)
        right = add_nodes_slots(level-1)
        node = NodeSlots(o, left, right)
        count += 1
    else:
        node = None
    return node

@profile
def test_do():
    global count
    count = 0
    root = add_nodes_do(22)
    print(count, "nodes")
    del root
    return

@profile
def test_slots():
    global count
    count = 0
    root = add_nodes_slots(22)
    print(count, "nodes")
    del root
    return

if __name__ == '__main__':
    tag = sys.argv[1]
#     print(tag)
    if tag == 'do':
        test_do()
    elif tag == 'slots':
        test_slots()
    else:
        print("Unknown tag")
    print("done")
