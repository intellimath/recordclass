import unittest
import pickle, copy
import keyword
import re
import sys
import gc
import weakref

from recordclass import make_dataclass, datatype, as_dataclass
from recordclass import dataobject
from recordclass import asdict

# _PY36 = _sys.version_info[:2] >= (3, 6)
_PY37 = sys.version_info[:2] >= (3, 7)

if 'PyPy' in sys.version:
    is_pypy = True
else:
    is_pypy = False
    from recordclass.utils import headgc_size, ref_size, pyobject_size, pyvarobject_size, pyssize

    _t = ()
    _t1 = (1,)
    _o = object()
    headgc_size = sys.getsizeof(_t) - _t.__sizeof__()
    ptr_size = sys.getsizeof(_t1) - sys.getsizeof(_t)
    pyobject_size = _o.__sizeof__()
    pyvarobject_size = _t.__sizeof__()
    del _t, _t1, _o

class TestPickle2(dataobject):
    __fields__ = 'x', 'y', 'z'

class TestPickle3(dataobject):
    __fields__  = 'x', 'y', 'z', '__dict__'

class TestPickle22(dataobject):
    x:int
    y:int
    z:int

class TestPickle33(dataobject):
    x:int
    y:int
    z:int
    __dict__:dict

class DataObjectTest3(unittest.TestCase):

    def test_dataobject_lists(self):
        class A(dataobject):
            x:object
            y:object

        print(A.__fields__)
        a = A([1,2,3],[3,4,5])
        print(a)

    def test_datatype_tp(self):
        class A(dataobject):
            __fields__ = 'x', 'y'
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(asdict(a), {'x':1, 'y':2})
        self.assertEqual(A.__annotations__, {'x':int, 'y':int})
        # self.assertEqual(sys.getsizeof(a), pyobject_size+2*ptr_size)
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        with self.assertRaises(AttributeError):     
            a.z = 3
        with self.assertRaises(AttributeError):     
            a.z
        a = None

    def test_datatype2_tp(self):
        class A(dataobject):
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(asdict(a), {'x':1, 'y':2})
        self.assertEqual(A.__annotations__, {'x':int, 'y':int})
        self.assertEqual(A.__fields__, ('x', 'y'))
        # self.assertEqual(sys.getsizeof(a), pyobject_size+2*ptr_size)
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        with self.assertRaises(AttributeError):     
            a.z = 3
        with self.assertRaises(AttributeError):     
            a.z
        a = None

    def test_datatype2_tp2(self):
        @as_dataclass()
        class A:
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(asdict(a), {'x':1, 'y':2})
        self.assertEqual(A.__annotations__, {'x':int, 'y':int})
        self.assertEqual(A.__fields__, ('x', 'y'))
        if not is_pypy:
            self.assertEqual(sys.getsizeof(a), pyobject_size+2*ptr_size)
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(a)
        # print('*')
        with self.assertRaises(TypeError):     
            a.__dict__
        with self.assertRaises(AttributeError):     
            a.z = 3
        with self.assertRaises(AttributeError):     
            a.z
        a = None

    def test_datatype3_tp(self):
        class A(dataobject):
            x:int
            y:int

            def dummy(self):
                pass

        self.assertEqual(A.__fields__, ('x','y'))

    def test_datatype4_tp(self):
        class A(dataobject, sequence=True):
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)

    def test_datatype5_tp(self):
        class A(dataobject, mapping=True):
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)

    def test_datatype6_tp(self):
        class A(dataobject, sequence=True, mapping=True):
            x:int
            y:int

        a = A(1,2)
        if not is_pypy:
            self.assertEqual(A.__weakrefoffset__, 0)
            self.assertEqual(A.__dictoffset__, 0)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)

    def test_datatype7_tp(self):
        class A(dataobject):
            __fields__ = 'x', 'y'

        a = A(1,2)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
#         self.assertEqual(sys.getsizeof(a), 32)
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        with self.assertRaises(AttributeError):     
            a.z = 3
        with self.assertRaises(AttributeError):     
            a.z
        a = None

    def test_datatype_dict_tp(self):
        class A(dataobject):
            __fields__ = 'x', 'y', '__dict__', '__weakref__'
            x:int
            y:int

        a = A(1,2)
        self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(asdict(a), {'x':1, 'y':2})
        self.assertEqual(A.__annotations__, {'x':int, 'y':int})
        # self.assertEqual(sys.getsizeof(a), pyobject_size+(2+2)*ptr_size)
        if not is_pypy:
            self.assertNotEqual(A.__dictoffset__, 0)
            self.assertNotEqual(A.__weakrefoffset__, 0)
            weakref.ref(a)
        self.assertEqual(a.__dict__, {})

        a.z = 3
        print(repr(a))
        self.assertEqual(a.z, a.__dict__['z'])
        self.assertEqual(repr(a), "A(x=1, y=2, **{'z': 3})")
        #a = None

    def test_subclass_tp(self):
        class A(dataobject):
            x:int
            y:int

        class B(A):
            pass

        self.assertEqual(type(A), type(B))
        self.assertEqual(B.__dictoffset__, 0)
        self.assertEqual(B.__weakrefoffset__, 0)
        b = B(1,2)
        self.assertEqual(repr(b), "B(x=1, y=2)")
        self.assertEqual(b.x, 1)
        self.assertEqual(b.y, 2)
        self.assertEqual(asdict(b), {'x':1, 'y':2})
        self.assertEqual(B.__annotations__, {'x':int, 'y':int})
#         self.assertEqual(sys.getsizeof(a), 32)
        self.assertEqual(A.__basicsize__, B.__basicsize__)
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(b)
        with self.assertRaises(AttributeError):     
            b.__dict__        
        #a = None

    def test_subclass2_tp(self):
        class A(dataobject):
            x:int
            y:int

        class B(A):
            z:int

        class C(B):
            pass

        self.assertEqual(type(A), type(B))
        self.assertEqual(type(C), type(B))
        self.assertEqual(C.__dictoffset__, 0)
        self.assertEqual(C.__weakrefoffset__, 0)
        c = C(1,2,3)
        self.assertEqual(repr(c), "C(x=1, y=2, z=3)")
        self.assertEqual(c.x, 1)
        self.assertEqual(c.y, 2)
        self.assertEqual(c.z, 3)
        self.assertEqual(asdict(c), {'x':1, 'y':2, 'z':3})
        self.assertEqual(C.__annotations__, {'x':int, 'y':int, 'z':int})
        # self.assertEqual(sys.getsizeof(c), pyobject_size+3*ptr_size)
        with self.assertRaises(TypeError):     
            weakref.ref(c)
        with self.assertRaises(AttributeError):     
            c.__dict__

    def test_subclass3_tp(self):
        class A(dataobject):
            x:int
            y:int

        class B:
            def norm_1(self):
                return abs(self.x) + abs(self.y)

        class C(A, B):
            pass

        self.assertEqual(type(C), type(A))
        self.assertEqual(C.__dictoffset__, 0)
        self.assertEqual(C.__weakrefoffset__, 0)
        c = C(1,2)
        self.assertEqual(repr(c), "C(x=1, y=2)")
        self.assertEqual(c.x, 1)
        self.assertEqual(c.y, 2)
        self.assertEqual(c.norm_1(), 3)
        self.assertEqual(asdict(c), {'x':1, 'y':2})
        self.assertEqual(C.__annotations__, {'x':int, 'y':int})
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(c)
        with self.assertRaises(AttributeError):     
            c.__dict__

    def test_subclass4_tp(self):
        class A(dataobject):
            x:int
            y:int

        class B(A):
            z:int

        class N:
            def norm_1(self):
                return abs(self.x) + abs(self.y) + abs(self.z)

        class C(B, N):
            pass

        self.assertEqual(type(A), type(B))
        self.assertEqual(type(C), type(B))
        self.assertEqual(C.__dictoffset__, 0)
        self.assertEqual(C.__weakrefoffset__, 0)
        c = C(1,2,3)
        self.assertEqual(repr(c), "C(x=1, y=2, z=3)")
        self.assertEqual(c.x, 1)
        self.assertEqual(c.y, 2)
        self.assertEqual(c.z, 3)
        self.assertEqual(c.norm_1(), 6)
        self.assertEqual(asdict(c), {'x':1, 'y':2, 'z':3})
        self.assertEqual(C.__annotations__, {'x':int, 'y':int, 'z':int})
#         self.assertEqual(sys.getsizeof(c), 40)
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(c)
        with self.assertRaises(AttributeError):     
            c.__dict__

    def test_defaults_tp(self):
        class A(dataobject):
            x:int = 100
            y:int = 200
            z:int = 300

        # a1 = A()
        # self.assertEqual(repr(a1), "A(x=100, y=200, z=300)")
        # self.assertEqual(a1.x, 100)
        # self.assertEqual(a1.y, 200)
        # self.assertEqual(a1.z, 300)
        # a2 = A(1)
        # self.assertEqual(repr(a2), "A(x=1, y=200, z=300)")
        # self.assertEqual(a2.x, 1)
        # self.assertEqual(a2.y, 200)
        # self.assertEqual(a2.z, 300)
        # a3 = A(1,2)
        # self.assertEqual(repr(a3), "A(x=1, y=2, z=300)")
        # self.assertEqual(a3.x, 1)
        # self.assertEqual(a3.y, 2)
        # self.assertEqual(a3.z, 300)

    def test_subclass_defaults_tp(self):
        class A(dataobject):
            x:int
            y:int

        class B(A):
            y:int=0

        self.assertEqual(A.__fields__, ('x', 'y'))
        self.assertEqual(A.__defaults__, (None,None))

        self.assertEqual(B.__fields__, ('x', 'y'))
        self.assertEqual(B.__defaults__, (None, 0))
        b = B(1)
        self.assertEqual(b.x, 1)
        self.assertEqual(b.y, 0)
        self.assertEqual(repr(b), "B(x=1, y=0)")        

    def test_keyword_args_tp(self):
        class A(dataobject):
            x:int
            y:int
            z:int

        class B(dataobject):
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
        class A(dataobject):
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
        class A(dataobject):
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
        class A(dataobject):
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

    def test_datatype_dict2_tp(self):
        class A(dataobject, use_dict=True, use_weakref=True):
            __fields__ = 'x', 'y'

        a = A(1,2)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
#         self.assertEqual(sys.getsizeof(a), 48)
#         self.assertEqual(A.__dictoffset__, 32)
#         self.assertEqual(A.__weakrefoffset__, 40)
        weakref.ref(a)
        self.assertEqual(a.__dict__, {})

        a.z = 3
        self.assertEqual(a.z, a.__dict__['z'])
        a = None        

    def test_defaults2_tp(self):
        class A(dataobject):
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

    def test_defaults3_tp(self):
        class A(dataobject):
            __fields__ = ('x', 'y', 'z')
            x = 100
            y = 200
            z = 300

    def test_iter2_tp(self):
        class A(dataobject):
            __fields__ = 3

        a=A(1, 2.0, "a")
        self.assertEqual(list(iter(a)), [1, 2.0, "a"])

    def test_iter3_tp(self):
        class A(dataobject, iterable=True):
            __fields__ = ('x', 'y', 'z')

        a=A(1, 2.0, "a")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2.0)
        self.assertEqual(a.z, "a")        
        self.assertEqual(list(iter(a)), [1, 2.0, "a"])

    def test_iter3_tp2(self):
        class A(dataobject, iterable=True):
            __fields__ = ('x', 'y', 'z')

        a=A(1, 2.0, "a")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2.0)
        self.assertEqual(a.z, "a")        
        self.assertEqual(list(iter(a)), [1, 2.0, "a"])

    def test_iter4_tp(self):
        class A(dataobject):
            __fields__ = 'x', 'y', 'z'

        a=A(1, 2.0, "a")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2.0)
        self.assertEqual(a.z, "a")        
        with self.assertRaises(TypeError):
            iter(a)

    def test_enable_gc_tp(self):

        class A(dataobject):
            __fields__ = 'x', 'y', 'z'

#         @clsconfig(gc=True)
        class B(dataobject, gc=True):
            __fields__ = 'x', 'y', 'z'

        a = A(1,2,3)
        b = B(1,2,3)
        self.assertEqual(a.x, b.x)
        self.assertEqual(a.y, b.y)
        self.assertEqual(a.z, b.z)
        # self.assertEqual(sys.getsizeof(b)-sys.getsizeof(a), headgc_size)        

    def test_pickle2_tp(self):
        p = TestPickle2(10, 20, 30)
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

    def test_pickle3_tp(self):
        p = TestPickle3(10, 20, 30)
        p.a = 1
        p.b = 2
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

    def test_pickle22_tp(self):
        p = TestPickle22(10, 20, 30)
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

    def test_pickle33_tp(self):
        p = TestPickle33(10, 20, 30)
        p.a = 1
        p.b = 2
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

    def test_invalid_defaults_tp(self):
        import copy

        with self.assertRaises(TypeError):        
            class A(dataobject):
                x:int=0
                y:int

    def test_copy_tp(self):
        import copy

        class A(dataobject):
            x:int
            y:int

        a=A(x=1,y=2)
        b = copy.copy(a)
        self.assertEqual(a, b)
        c = copy.deepcopy(a)
        self.assertEqual(a, c)

#     def test_signature_tp(self):
#         class A(dataobject):
#             x:int
#             y:int=2

#         import inspect
#         s = inspect.signature(A)
#         px = s.parameters['x']
#         self.assertEqual(px.name, 'x')
#         self.assertEqual(px.annotation, int)
#         self.assertEqual(px.default, px.empty)
#         py = s.parameters['y']
#         self.assertEqual(py.name, 'y')
#         self.assertEqual(py.annotation, int)
#         self.assertEqual(py.default, 2)

    def test_fast_new_tp(self):
        class A(dataobject, fast_new=True):
            __fields__ = 'x', 'y'

        self.assertTrue('__new__' not in A.__dict__)
        a = A(1,2)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        a = A(1,y=2)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        a = A(1,**{'y':2})
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        a = A(x=1,y=2)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        a = A(**{'x':1, 'y':2})
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)

    def test_missing_args1_tp(self):
        class A(dataobject, fast_new=True):
            __fields__ = 'a','b','c'

        a=A(1)
        self.assertEqual(a.a, 1)
        self.assertEqual(a.b, None)
        self.assertEqual(a.c, None)

    def test_missing_args2_tp(self):
        class A(dataobject, fast_new=True):
            __fields__ = 'a','b','c'
            b = 2
            c = 3

        a=A(1)
        self.assertEqual(a.a, 1)
        self.assertEqual(a.b, 2)
        self.assertEqual(a.c, 3)

    if not is_pypy:
        def test_do_finalizer_tp(self):
            count = 0
            class A(dataobject):
                x:int
                y:int

                def __del__(self):
                    nonlocal count
                    count += 1

            for i in range(100):
                a = A(1,2)
                del a

            self.assertEqual(count, 100)

        def test_deep_dealloc(self):
            class LinkedItem(dataobject, fast_new=True):
                val: object
                next: 'LinkedItem'

            class LinkedList(dataobject, deep_dealloc=True):
                start: LinkedItem = None
                end: LinkedItem = None

                def append(self, val):
                    link = LinkedItem(val, None)
                    if self.start is None:
                        self.start = link
                    else:
                        self.end.next = link
                    self.end = link

            self.assertEqual(LinkedItem.__base__, dataobject)

            ll = LinkedList()
            for i in range(10):
                ll.append(i)

            del ll

    def test_readonly(self):
        class A(dataobject, readonly=True):
            x:int
            y:int

        a = A(1,2)
        with self.assertRaises(AttributeError):        
            a.x = -1
        with self.assertRaises(AttributeError):        
            a.y = -2

    def test_readonly_2(self):
        class A(dataobject, readonly=True, use_dict=True):
            x:int
            y:int

        a = A(1,2, z=3)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(a.z, 3)

    def test_readonly_3(self):
        class A(dataobject, readonly=True):
            x:int
            y:int
            z:int

        a = A(1,2, z=3)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(a.z, 3)

    def test_default_arg_enum(self):
        from enum import Enum, auto

        class Color(Enum):
            RED = auto()

        class Point(dataobject):
            x: float
            y: float
            color: Color = Color.RED        

        pt = Point(1,2)
        self.assertEqual(pt.color, Color.RED)

    if _PY37:
        def test_classvar_1(self):
            from typing import ClassVar
            class Point(dataobject):
                color:ClassVar[int]
                x: float
                y: float

            print(ClassVar[int])
            self.assertEqual(Point.__fields__, ('x','y'))
            self.assertEqual(Point.__annotations__, {'x':float,'y':float})   
            pt = Point(1,2)
            self.assertEqual((pt.x, pt.y), (1, 2))

        def test_classvar_2(self):
            from typing import ClassVar
            class Point(dataobject):
                x: float
                y: float
                color:ClassVar[int] = 1

            self.assertEqual(Point.color, 1)
            self.assertEqual(Point.__fields__, ('x','y'))
            self.assertEqual(Point.__annotations__, {'x':float,'y':float})            
            pt = Point(1,2)
            self.assertEqual((pt.x, pt.y), (1, 2))

    def test_initialize_in_init(self):
        class A(dataobject):
            x:int
            y:int

            def __init__(self, x, y):
                print("__init__")
                self.x = 2*x
                self.y = 3*y

        a = A(1,2)
        self.assertEqual(a.x, 2)
        self.assertEqual(a.y, 6)

    def test_initialize_in_init2(self):
        class A(dataobject):
            x:int
            y:int

            def __init__(self, *args, **kwds):
                print("__init__")
                self.x = 2*kwds['x']
                self.y = 3*kwds['y']

        a = A(x=1,y=2)
        self.assertEqual(a.x, 2)
        self.assertEqual(a.y, 6)

    def test_initialize_in_init3(self):
        class A(dataobject):
            x:int
            y:int

            def __init__(self, x, y=0):
                print("__init__")
                self.x = 2*x
                self.y = 3*y

        a = A(1,y=2)
        self.assertEqual(a.x, 2)
        self.assertEqual(a.y, 6)
        b = A(1)
        self.assertEqual(b.x, 2)
        self.assertEqual(b.y, 0)

    def test_initialize_in_init4(self):
        class A(dataobject):
            x:int
            y:int

            def __init__(self, x):
                print("__init__")
                self.x = 2*x
                self.y = self.x + 2

        b = A(1)
        self.assertEqual(b.x, 2)
        self.assertEqual(b.y, 4)

    def test_initialize_in_init5(self):
        class A0(dataobject):
            x:int
            y:int

            def __init__(self, x, y):
                self.x = x
                self.y = y

        class A(A0):
            def __init__(self, x, y):
                print("__init__")
                pass

        a = A(1,2)
        self.assertEqual(a.x, None)
        self.assertEqual(a.y, None)

#     def test_post_init_1(self):
#         class A(dataobject):
#             x:int
#             y:int

#             def __post_init__(self):
#                 print("__post_init__")
#                 self.x *= 2
#                 self.y *= 3

#         a = A(2,3)
#         self.assertEqual(a.x, 4)
#         self.assertEqual(a.y, 9)

#     def test_post_init_2(self):
#         class A(dataobject):
#             x:int
#             y:int

#             def __post_init__(self):
#                 print("__post_init__")
#                 raise AttributeError("")

#         with self.assertRaises(AttributeError):        
#             a = A(1,2)

#     def test_post_init_3(self):
#         class A(dataobject):
#             x:int
#             y:int

#             def __init__(self, x, y):
#                 print("__init__")
#                 self.x = x
#                 self.y = y
#             #
#             def __post_init__(self):
#                 print("__post_init__")
#                 self.x *= 2
#                 self.y *= 3

#         a = A(2,3)
#         self.assertEqual(a.x, 4)
#         self.assertEqual(a.y, 9)

#     def test_post_init_4(self):
#         class A(dataobject):
#             x:int
#             y:int

#             def __init__(self, x, y):
#                 print("__init__")
#                 self.x = x
#                 self.y = y
#             #
#             def __post_init__(self):
#                 print("__post_init__")
#                 raise AttributeError("")

#         with self.assertRaises(AttributeError):        
#             a = A(1,2)

def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DataObjectTest3))
    return suite
