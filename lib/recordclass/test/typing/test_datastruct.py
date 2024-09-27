import unittest
import pickle, copy
import keyword
import re
import sys
import gc
import weakref

from recordclass import make_dataclass, datatype, as_record
from recordclass import datastruct, datatype
from recordclass import asdict, make

from typing import ClassVar

_PY311 = sys.version_info[:2] >= (3, 11)

from recordclass.utils import headgc_size, ref_size, pyobject_size, pyvarobject_size, pyssize

_t = ()
_t1 = (1,)
_o = object()
headgc_size = sys.getsizeof(_t) - _t.__sizeof__()
ptr_size = sys.getsizeof(_t1) - sys.getsizeof(_t)
pyobject_size = _o.__sizeof__()
pyvarobject_size = _t.__sizeof__()
del _t, _t1, _o

class TestPickle2(datastruct):
    __fields__ = 'x', 'y', 'z'

class TestPickle22(datastruct):
    x:int
    y:int
    z:int

class datastructTest3(unittest.TestCase):

    def test_datastruct_lists(self):
        class A(datastruct):
            x:object
            y:object

        # print(A.__fields__)
        a = A([1,2,3],[3,4,5])
        # print(a)

    def test_datastruct_tp(self):
        class A(datastruct):
            __fields__ = 'x', 'y'
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(asdict(a), {'x':1, 'y':2})
        self.assertEqual(A.__annotations__, {'x':int, 'y':int})
        self.assertEqual(sys.getsizeof(a), pyobject_size+2*ptr_size)
        with self.assertRaises(TypeError):     
            weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        with self.assertRaises(AttributeError):     
            a.z = 3
        with self.assertRaises(AttributeError):     
            a.z
        a = None

    def test_datastruct2_tp(self):
        class A(datastruct):
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(asdict(a), {'x':1, 'y':2})
        self.assertEqual(A.__annotations__, {'x':int, 'y':int})
        self.assertEqual(A.__fields__, ('x', 'y'))
        self.assertEqual(sys.getsizeof(a), pyobject_size+2*ptr_size)
        with self.assertRaises(TypeError):     
            weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        with self.assertRaises(AttributeError):     
            a.z = 3
        with self.assertRaises(AttributeError):     
            a.z
        a = None

    def test_datastruct2_tp2(self):
        @as_record()
        def A(x:int, y:int): pass

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(asdict(a), {'x':1, 'y':2})
        self.assertEqual(A.__annotations__, {'x':int, 'y':int})
        self.assertEqual(A.__fields__, ('x', 'y'))
        self.assertEqual(sys.getsizeof(a), pyobject_size+2*ptr_size)
        with self.assertRaises(TypeError):     
            weakref.ref(a)
        # print('*')
        with self.assertRaises(AttributeError):     
            a.__dict__
        with self.assertRaises(AttributeError):     
            a.z = 3
        with self.assertRaises(AttributeError):     
            a.z
        a = None

    def test_datastruct4_tp(self):
        class A(datastruct, sequence=True):
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)

    def test_datastruct5_tp(self):
        class A(datastruct, mapping=True):
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)

    def test_datastruct6_tp(self):
        class A(datastruct, sequence=True, mapping=True):
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(A.__weakrefoffset__, 0)
        self.assertEqual(A.__dictoffset__, 0)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)

    def test_datastruct7_tp(self):
        class A(datastruct):
            __fields__ = 'x', 'y'

        a = A(1,2)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(sys.getsizeof(a), 32)
        with self.assertRaises(TypeError):     
            weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        with self.assertRaises(AttributeError):     
            a.z = 3
        with self.assertRaises(AttributeError):     
            a.z
        a = None


    def test_datastruct_defaults_tp(self):
        class A(datastruct):
            x:int = 100
            y:int = 200
            z:int = 300

        a1 = A()
        self.assertEqual(repr(a1), "A(x=100, y=200, z=300)")
        self.assertEqual(a1.x, 100)
        self.assertEqual(a1.y, 200)
        self.assertEqual(a1.z, 300)
        a2 = A(1)
        self.assertEqual(repr(a2), "A(x=1, y=200, z=300)")
        self.assertEqual(a2.x, 1)
        self.assertEqual(a2.y, 200)
        self.assertEqual(a2.z, 300)
        a3 = A(1,2)
        self.assertEqual(repr(a3), "A(x=1, y=2, z=300)")
        self.assertEqual(a3.x, 1)
        self.assertEqual(a3.y, 2)
        self.assertEqual(a3.z, 300)
        
    def test_keyword_args_tp(self):
        class A(datastruct):
            x:int
            y:int
            z:int

        class B(datastruct):
            x:int
            y:int
            z:int

        a = A(1,2,3)
        self.assertEqual(repr(a), "A(x=1, y=2, z=3)")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(a.z, 3)
        b = B(1,2,3)
        self.assertEqual(repr(b), "B(x=1, y=2, z=3)")
        self.assertEqual(b.x, 1)
        self.assertEqual(b.y, 2)
        self.assertEqual(b.z, 3)
        c = B(1,2,3)
        self.assertEqual(repr(c), "B(x=1, y=2, z=3)")
        self.assertEqual(c.x, 1)
        self.assertEqual(c.y, 2)
        self.assertEqual(c.z, 3)

    def test_keyword_args2_tp(self):
        class A(datastruct):
            __fields__ = 'x', 'y', 'z'

        a1 = A(x=1, y=2, z=3)
        self.assertEqual(a1.x, 1)
        self.assertEqual(a1.y, 2)
        self.assertEqual(a1.z, 3)
        a3 = A(1,"a",3)
        self.assertEqual(a3.x, 1)
        self.assertEqual(a3.y, "a")
        self.assertEqual(a3.z, 3)            

    def test_keyword_args_defaults2_tp(self):
        class A(datastruct):
            __fields__ = ('x', 'y', 'z')
            x = 100
            y = 200
            z = 300

        a1 = A(x=1)
        self.assertEqual(a1.x, 1)
        self.assertEqual(a1.y, 200)
        self.assertEqual(a1.z, 300)
        a2 = A(x=1,y=2.0)
        self.assertEqual(a2.x, 1)
        self.assertEqual(a2.y, 2.0)
        self.assertEqual(a2.z, 300)
        a3 = A(x=1,y=2.0,z="a")
        self.assertEqual(a3.x, 1)
        self.assertEqual(a3.y, 2.0)
        self.assertEqual(a3.z, "a")

    def test_keyword_args_defaults_tp(self):
        class A(datastruct):
            x:int = 100
            y:int = 200
            z:int = 300

        a1 = A(x=1)
        self.assertEqual(repr(a1), "A(x=1, y=200, z=300)")
        self.assertEqual(a1.x, 1)
        self.assertEqual(a1.y, 200)
        self.assertEqual(a1.z, 300)
        a2 = A(x=1,y=2)
        self.assertEqual(repr(a2), "A(x=1, y=2, z=300)")
        self.assertEqual(a2.x, 1)
        self.assertEqual(a2.y, 2)
        self.assertEqual(a2.z, 300)
        a3 = A(x=1,y=2,z=3)
        self.assertEqual(repr(a3), "A(x=1, y=2, z=3)")
        self.assertEqual(a3.x, 1)
        self.assertEqual(a3.y, 2)
        self.assertEqual(a3.z, 3)

    def test_datastruct_defaults2_tp(self):
        class A(datastruct):
            __fields__ = ('x', 'y', 'z')
            x = 100
            y = 200
            z = 300

        a1 = A()
        self.assertEqual(a1.x, 100)
        self.assertEqual(a1.y, 200)
        self.assertEqual(a1.z, 300)
        a2 = A(1)
        self.assertEqual(a2.x, 1)
        self.assertEqual(a2.y, 200)
        self.assertEqual(a2.z, 300)
        a3 = A(1,2)
        self.assertEqual(a3.x, 1)
        self.assertEqual(a3.y, 2)
        self.assertEqual(a3.z, 300)

    def test_datastruct_defaults3_tp(self):
        class A(datastruct):
            __fields__ = ('x', 'y', 'z')
            x = 100
            y = 200
            z = 300

    def test_datastruct_iter3_tp(self):
        class A(datastruct, iterable=True):
            __fields__ = ('x', 'y', 'z')

        a=A(1, 2.0, "a")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2.0)
        self.assertEqual(a.z, "a")        
        self.assertEqual(list(iter(a)), [1, 2.0, "a"])

    def test_datastruct_iter3_tp2(self):
        class A(datastruct, iterable=True):
            __fields__ = ('x', 'y', 'z')

        a=A(1, 2.0, "a")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2.0)
        self.assertEqual(a.z, "a")        
        self.assertEqual(list(iter(a)), [1, 2.0, "a"])

    def test_datastruct_iter4_tp(self):
        class A(datastruct):
            __fields__ = 'x', 'y', 'z'

        a=A(1, 2.0, "a")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2.0)
        self.assertEqual(a.z, "a")        
        with self.assertRaises(TypeError):
            iter(a)

    def test_datastruct_enable_gc_tp(self):

        class A(datastruct):
            __fields__ = 'x', 'y', 'z'

        class B(datastruct, gc=True):
            __fields__ = 'x', 'y', 'z'

        a = A(1,2,3)
        b = B(1,2,3)
        self.assertEqual(a.x, b.x)
        self.assertEqual(a.y, b.y)
        self.assertEqual(a.z, b.z)
        self.assertEqual(sys.getsizeof(b)-sys.getsizeof(a), headgc_size)        

    def test_datastruct_pickle2_tp(self):
        p = TestPickle2(10, 20, 30)
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

    def test_datastruct_pickle22_tp(self):
        p = TestPickle22(10, 20, 30)
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)
                
    def test_datastruct_invalid_defaults_tp(self):
        import copy

        with self.assertRaises(TypeError):        
            class A(datastruct):
                x:int=0
                y:int

    def test_datastruct_copy_tp(self):
        import copy

        class A(datastruct):
            x:int
            y:int

        a=A(x=1,y=2)
        b = copy.copy(a)
        self.assertEqual(a, b)
        c = copy.deepcopy(a)
        self.assertEqual(a, c)
        
    def test_datastruct_vcall_1(self):
        class A(datastruct):
            x:int
            y:int
            
        for i in range(1000):
            a = A(1,2)
            self.assertEqual(a.x, 1)
            self.assertEqual(a.y, 2)

    def test_datastruct_vcall_2(self):
        class A(datastruct):
            x:int
            y:int
            
        for i in range(1000):
            a = A(1,y=2)
            self.assertEqual(a.x, 1)
            self.assertEqual(a.y, 2)
            
    def test_datastruct_vcall_3(self):
        class A(datastruct):
            x:int
            y:int
            
        for i in range(1000):
            a = A(x=1,y=2)
            self.assertEqual(a.x, 1)
            self.assertEqual(a.y, 2)

    def test_datastruct_missing_args1_tp(self):
        class A(datastruct):
            __fields__ = 'a','b','c'

        a=A(1)
        self.assertEqual(a.a, 1)
        self.assertEqual(a.b, None)
        self.assertEqual(a.c, None)

    def test_datastruct_missing_args2_tp(self):
        class A(datastruct):
            __fields__ = 'a','b','c'
            b = 2
            c = 3

        a=A(1)
        self.assertEqual(a.a, 1)
        self.assertEqual(a.b, 2)
        self.assertEqual(a.c, 3)

    def test_datastruct_readonly(self):
        class A(datastruct, readonly=True):
            x:int
            y:int

        a = A(1,2)
        with self.assertRaises(AttributeError):        
            a.x = -1
        with self.assertRaises(AttributeError):        
            a.y = -2

    def test_datastruct_readonly_3(self):
        class A(datastruct, readonly=True):
            x:int
            y:int
            z:int

        a = A(1,2, z=3)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(a.z, 3)

    def test_datastruct_default_arg_enum(self):
        from enum import Enum, auto

        class Color(Enum):
            RED = auto()

        class Point(datastruct):
            x: float
            y: float
            color: Color = Color.RED        

        pt = Point(1,2)
        self.assertEqual(pt.color, Color.RED)

    def test_datastruct_copy_default_1(self):
        class A(datastruct):
            l: list = []

        a = A()
        b = A()
        # print(id(a.l), id(b.l))
        self.assertEqual(a.l, b.l)
        self.assertEqual(id(a.l), id(b.l))

    def test_datastruct_copy_default_2(self):
        class A(datastruct):
            d: dict = {}

        a = A()
        b = A()
        # print(id(a.d), id(b.d))
        self.assertEqual(a.d, b.d)
        self.assertEqual(id(a.d), id(b.d))

    def test_datastruct_copy_default_3(self):
        class A(datastruct):
            d: set = set()

        a = A()
        b = A()
        # print(id(a.d), id(b.d))
        self.assertEqual(a.d, b.d)
        self.assertEqual(id(a.d), id(b.d))
    
    def test_datastruct_copy_default_4(self):
        class A(datastruct, copy_default=True):
            l: list = []

        a = A()
        b = A()
        # print(id(a.l), id(b.l))
        self.assertEqual(a.l, b.l)
        self.assertNotEqual(id(a.l), id(b.l))

    
    def test_datastruct_copy_default_5(self):
        class A(datastruct, copy_default=True):
            d: dict = {}

        a = A()
        b = A()
        # print(id(a.d), id(b.d))
        self.assertEqual(a.d, b.d)
        self.assertNotEqual(id(a.d), id(b.d))

    def test_datastruct_copy_default_6(self):
        class A(datastruct, copy_default=True):
            d: set = set()

        a = A()
        b = A()
        # print(id(a.d), id(b.d))
        self.assertEqual(a.d, b.d)
        self.assertNotEqual(id(a.d), id(b.d))
    
    
    def test_datastruct_copy_default_classvar(self):

        class A(datastruct, copy_default=True):
            x : list = []
            y : ClassVar[list] = [1] # attribute y in A.__dict__

        a = A()
        print(type(A.x), type(A.y))
        self.assertTrue(type(A.y) is list)
        self.assertTrue(a.y is A.y)

        b = A()
        self.assertTrue(b.y is A.y)
        self.assertEqual(a.x, b.x)
        self.assertNotEqual(id(a.x), id(b.x))
        self.assertEqual(a.y, b.y)
        self.assertEqual(id(a.y), id(b.y))

    def test_datastruct_Factory_1(self):
        from recordclass import Factory
        class A(datastruct):
            x: tuple = Factory(lambda: (list(), dict()))

        a = A()
        b = A()
        self.assertEqual(a.x, ([],{}))
        self.assertNotEqual(id(a.x), id(b.x))
        self.assertNotEqual(id(a.x[0]), id(b.x[0]))
        self.assertNotEqual(id(a.x[1]), id(b.x[1]))

    def test_datastruct_Factory_2(self):
        from recordclass import Factory
        class A(datastruct, copy_default=True):
            l: list = []
            x: tuple = Factory(lambda: (list(), dict()))

        a = A()
        b = A()
        self.assertEqual(a.x, ([],{}))
        self.assertNotEqual(id(a.x), id(b.x))
        self.assertEqual(a.l, [])
        self.assertNotEqual(id(a.l), id(b.l))


def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(datastructTest3))
    return suite
