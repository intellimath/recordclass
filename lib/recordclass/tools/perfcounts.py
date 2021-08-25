from collections import namedtuple
from recordclass import dataobject, clsconfig
from timeit import timeit
import sys

PointNT = namedtuple("PointNT", "x y")
nan = float('nan')

class PointSlots:
    __slots__ = 'x', 'y'
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
class Point(dataobject, sequence=True):
    x:int
    y:int

class PointGC(dataobject, sequence=True, gc=True):
    x:int
    y:int

class FastPoint(dataobject, sequence=True, fast_new=True):
    x:int
    y:int
    
class FastPointGC(dataobject, sequence=True, fast_new=True, gc=True):
    x:int
    y:int
    
results = {'id':[], 'new':[], 
           'getattr':[], 'setattr':[], 
           'getitem':[], 'setitem':[],
           'size':[]}

results['id'].extend(
    ['dict', 'tuple', 'namedtuple', 'class+slots', 'dataobject',  
     'dataobject+fast_new', 'dataobject+gc', 'dataobject+fast_new+gc'])

classes = (dict, tuple, PointNT, PointSlots, Point, FastPoint, PointGC, FastPointGC)

N = 1_000_000

numbers = 10

def test_new():
    print("new")
    def test(cls):
        lst = [cls(i,i) for i in range(N)]
        return lst
        
    def test_tuple():
        lst = [(i,i) for i in range(N)]
        return lst

    def test_dict():
        lst = [{'x':i, 'y':i} for i in range(N)]
        return lst
    
    for cls in classes:
        if cls is dict:
            res = timeit("test_dict()", number=numbers, globals={'test':test, 'test_dict':test_dict})
        elif cls is tuple:
            res = timeit("test_tuple()", number=numbers, globals={'test':test, 'test_tuple':test_tuple})
        else:
            res = timeit("test(cls)", number=numbers, globals={'cls':cls, 'test':test})
        results['new'].append(res)

def test_getattr():
    print("getattr")
    def test(cls):
        p = cls(0,0)
        for i in range(N):
            x = p.x
            y = p.y

    def test_dict():
        p = {'x':0, 'y':0}
        for i in range(N):
            x = p['x']
            y = p['y']
            
    for cls in classes:
        if cls in (tuple,):
            res = nan
        elif cls is dict:
            res = timeit("test_dict()", number=numbers, globals={'test':test, 'test_dict':test_dict})
        else:
            res = timeit("test(cls)", number=numbers, globals={'cls':cls, 'test':test})
        results['getattr'].append(res)

def test_getitem():
    print("getitem")
    def test(cls):
        p = cls(0,0)
        for i in range(N):
            x = p[0]
            y = p[1]

    def test_tuple():
        p = (0,0)
        for i in range(N):
            x = p[0]
            y = p[1]

    for cls in classes:
        if cls in (dict, PointSlots):
            res = nan
        elif cls is tuple:
            res = timeit("test_tuple()", number=numbers, globals={'test':test, 'test_tuple':test_tuple})
        else:
            res = timeit("test(cls)", number=numbers, globals={'cls':cls, 'test':test})
        results['getitem'].append(res)
        
def test_setattr():
    print("setattr")
    def test(cls):
        p = cls(0,0)
        for i in range(N):
            p.x = 1
            p.y = 2

    def test_dict():
        p = {'x':0, 'y':0}
        for i in range(N):
            p['x'] = 1
            p['y'] = 2
            
    for cls in classes:
        if cls in (tuple, PointNT):
            res = nan
        elif cls is dict:
            res = timeit("test_dict()", number=numbers, globals={'cls':cls, 'test_dict':test_dict})
        else:
            res = timeit("test(cls)", number=numbers, globals={'cls':cls, 'test':test, 'tuple':tuple, 'PointNT':PointNT})
        results['setattr'].append(res)

def test_setitem():
    print("setitem")
    def test(cls):
        p = cls(0,0)
        for i in range(N):
            p[0] = 1
            p[1] = 2
            
    for cls in classes:
        if cls in (dict, tuple, PointNT, PointSlots):
            res = nan
        else:
            res = timeit("test(cls)", number=numbers, globals={'cls':cls, 'test':test})
        results['setitem'].append(res)
        
import pandas as pd

test_new()
test_getattr()
test_setattr()
test_getitem()
test_setitem()

results['size'].extend([
  sys.getsizeof({'x':0,'y':0}),   
  sys.getsizeof((0,0)),   
  sys.getsizeof(PointNT(0,0)),   
  sys.getsizeof(PointSlots(0,0)),   
  sys.getsizeof(Point(0,0)),   
  sys.getsizeof(FastPoint(0,0)),   
  sys.getsizeof(PointGC(0,0)),   
  sys.getsizeof(FastPointGC(0,0)),   
])

pd.options.mode.use_inf_as_na = True
df = pd.DataFrame.from_dict(results)
# pd.set_option('precision', 2)
print(df.to_markdown(floatfmt='.2f'))