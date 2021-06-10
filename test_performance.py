from recordclass import recordclass, make_dataclass
from collections import namedtuple
import pyperf as perf
#from sys import getsizeof as sizeof

STest = namedtuple("TEST", "a b c d e f g h i j k")
sa = STest(a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10,k=11)

RTest = recordclass("RTEST", "a b c d e f g h i j k")
ra = RTest(a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10,k=11)

NDTest = make_dataclass("NDTest", "a b c d e f g h i j k", fast_new=True)
nd = NDTest(a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10,k=11)

NDTest2 = make_dataclass("NDTest", "a b c d e f g h i j k", fast_new=True, gc=True)
nd = NDTest2(a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10,k=11)

class Test(object):
    __slots__ = ["a","b","c","d","e","f","g","h","i","j","k"]

    def __init__(self, a, b, c, d, e, f, g, h, i, j, k):
        self.a = a; self.b = b; self.c = c
        self.d = d; self.e = e; self.f = f
        self.g = g; self.h = h; self.i = i
        self.j = j; self.k = k

b = Test(1,2,3,4,5,6,7,8,9,10,11)

c = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8, 'i':9, 'j':10, 'k':11}

d = (1,2,3,4,5,6,7,8,9,10,11)
e = [1,2,3,4,5,6,7,8,9,10,11]
key = 10

runner = perf.Runner()

### new ###
res = runner.timeit(
    "namedtuple.new",
    stmt="R(1,2,3,4,5,6,7,8,9,10,11)",
    setup="""
from collections import namedtuple
R = namedtuple('R', 'a b c d e f g h i j k')
"""
)

res = runner.timeit(
    "Recordclass.new",
    stmt="R(1,2,3,4,5,6,7,8,9,10,11)",
    setup="""
from recordclass import recordclass
R = recordclass('R', 'a b c d e f g h i j k')
"""
)

runner.timeit(
    "__slots__.new",
    stmt="R(1,2,3,4,5,6,7,8,9,10,11)",
    setup="""
class R(object):
    __slots__ = ["a","b","c","d","e","f","g","h","i","j","k"]

    def __init__(self, a, b, c, d, e, f, g, h, i, j, k):
        self.a = a; self.b = b; self.c = c
        self.d = d; self.e = e; self.f = f
        self.g = g; self.h = h; self.i = i
        self.j = j; self.k = k
"""
)

runner.timeit(
    "Dataobject.new",
    stmt="R(1,2,3,4,5,6,7,8,9,10,11)",
    setup="""
from recordclass import make_dataclass
R = make_dataclass('R', 'a b c d e f g h i j k', fast_new=True)
"""
)

### getattr ###

res = runner.timeit(
    "namedtuple.getattr",
    stmt="r.k",
    setup="""
from collections import namedtuple
R = namedtuple('R', 'a b c d e f g h i j k')
r = R(1,2,3,4,5,6,7,8,9,10,11)
"""
)

res = runner.timeit(
    "Recordclass.getattr",
    stmt="r.k",
    setup="""
from recordclass import recordclass
R = recordclass('R', 'a b c d e f g h i j k')
r = R(1,2,3,4,5,6,7,8,9,10,11)
"""
)

runner.timeit(
    "__slots__.getattr",
    stmt="r.k",
    setup="""
class R(object):
    __slots__ = ["a","b","c","d","e","f","g","h","i","j","k"]

    def __init__(self, a, b, c, d, e, f, g, h, i, j, k):
        self.a = a; self.b = b; self.c = c
        self.d = d; self.e = e; self.f = f
        self.g = g; self.h = h; self.i = i
        self.j = j; self.k = k
        
r = R(1,2,3,4,5,6,7,8,9,10,11)
"""
)

runner.timeit(
    "Dataobject.getattr",
    stmt="r.k",
    setup="""
from recordclass import make_dataclass
R = make_dataclass('R', 'a b c d e f g h i j k', fast_new=True)
r = R(1,2,3,4,5,6,7,8,9,10,11)
"""
)

### setattr ###

res = runner.timeit(
    "Recordclass.setattr",
    stmt="r.k=1",
    setup="""
from recordclass import recordclass
R = recordclass('R', 'a b c d e f g h i j k')
r = R(1,2,3,4,5,6,7,8,9,10,11)
"""
)

runner.timeit(
    "__slots__.setattr",
    stmt="r.k=1",
    setup="""
class R(object):
    __slots__ = ["a","b","c","d","e","f","g","h","i","j","k"]

    def __init__(self, a, b, c, d, e, f, g, h, i, j, k):
        self.a = a; self.b = b; self.c = c
        self.d = d; self.e = e; self.f = f
        self.g = g; self.h = h; self.i = i
        self.j = j; self.k = k
        
r = R(1,2,3,4,5,6,7,8,9,10,11)
"""
)


runner.timeit(
    "Dataobject.setattr",
    stmt="r.k=1",
    setup="""
from recordclass import make_dataclass
R = make_dataclass('R', 'a b c d e f g h i j k', fast_new=True)
r = R(1,2,3,4,5,6,7,8,9,10,11)
"""
)
