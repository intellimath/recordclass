from collections import namedtuple
from recordclass import dataobject, clsconfig
from timeit import timeit
import sys

PointNT = namedtuple("PointNT", "x y")

class PointSlots:
    __slots__ = 'x', 'y'
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
class Point(dataobject):
    x:int
    y:int

class PointGC(dataobject, gc=True):
    x:int
    y:int

class FastPoint(dataobject, fast_new=True):
    x:int
    y:int
    
class FastPointGC(dataobject, fast_new=True, gc=True):
    x:int
    y:int

results = {'id':[], 'new':[], 'read':[], 'write':[], 'size':[]}

results['id'].extend(
    ['namedtuple', 'class+slots', 'dataobject', 'dataobject+fast_new',  
     'dataobject+gc', 'dataobject+fast_new+gc'])

classes = (PointNT, PointSlots, Point, FastPoint, PointGC, FastPointGC)

N = 1000000

# ns = {'PointNT':PointNT, 'PointSlots':PointSlots, 'Point':Point,
#       'FastPoint':FastPoint, 'PointGC':PointGC, 'FastPointGC':FastPointGC}

numbers = 10

def test_new():
    def test(cls):
        lst = [cls(0,0) for i in range(N)]
        return cls
        
    for cls in classes:
        res = timeit("test(cls)", number=numbers, globals={'cls':cls, 'test':test})
        results['new'].append(res)

def test_read():
    def test(cls):
        p = cls(0,0)
        for i in range(N):
            x = p.x
            y = p.y

    for cls in classes:
        res = timeit("test(cls)", number=numbers, globals={'cls':cls, 'test':test})
        results['read'].append(res)

def test_write():
    def test(cls):
        p = cls(0,0)
        for i in range(N):
            p.x = 1
            p.y = 2
    
    for cls in classes:
        if cls is PointNT:
            res = ' '
        else:
            res = timeit("test(cls)", number=numbers, globals={'cls':cls, 'test':test, 'PointNT':PointNT})
        results['write'].append(res)

import pandas as pd

test_new()
test_read()
test_write()

results['size'].extend([
  sys.getsizeof(PointNT(0,0)),   
  sys.getsizeof(PointSlots(0,0)),   
  sys.getsizeof(Point(0,0)),   
  sys.getsizeof(FastPoint(0,0)),   
  sys.getsizeof(PointGC(0,0)),   
  sys.getsizeof(FastPointGC(0,0)),   
])

df = pd.DataFrame.from_dict(results)
print(df.to_markdown())