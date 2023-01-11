import unittest
import pickle, copy
import keyword
import re
import sys
import gc
import weakref

from recordclass import make_dataclass, make_arrayclass, dataobject, make, clone, update
from recordclass import datatype, asdict, astuple, join_dataclasses

if 'PyPy' in sys.version:
    is_pypy = True
else:
    is_pypy = False
    from recordclass.utils import headgc_size, ref_size, pyobject_size, pyvarobject_size, pyssize

TPickle2 = make_dataclass("TPickle2", ('x','y','z'))
TPickle3 = make_dataclass("TPickle3", ('x','y','z'), use_dict=True)

##########################################################################
        
class DataobjectTest(unittest.TestCase):

    def test_bad_makeclass(self):
        with self.assertRaises(TypeError):        
            A = make_dataclass("A", 'x y', defaults=(0,0,0))
            # a = A(x=1, y=2, z=3)
    
    def test_bad_makeclass2(self):
        with self.assertRaises(TypeError):        
            A = make_dataclass("A", 'x y', defaults=(0,0,0), fast_new=False)
            # a = A(x=1, y=2, z=3)

    def test_bad_call(self):
        A = make_dataclass("A", 'x y', defaults=(0,), fast_new=False)
        with self.assertRaises(TypeError):        
            a = A(x=1, y=2, z=3)

    def test_bad_call2(self):
        A = make_dataclass("A", 'x y', defaults=(0,))
        with self.assertRaises(TypeError):        
            a = A(x=1, y=2, z=3)

    def test_caching(self):
        from recordclass.dataclass import DataclassStorage
        ds = DataclassStorage()
        A = ds.make_dataclass('A', ('x', 'y'))
        B = ds.make_dataclass('A', ['x', 'y'])
        self.assertEqual(A, B)

    def test_dataclass_asdict(self):
        A = make_dataclass("A", {'x':int, 'y':int})
        a = A(x=1,y=2)
        d = asdict(a)
        self.assertEqual(d, {'x':1, 'y':2})

    def test_dataclass_empty_astuple(self):
        A = make_dataclass("A", ())
        a = A()
        self.assertEqual(len(a), 0)
        t = astuple(a)
        self.assertEqual(t, ())

    def test_dataclass_empty_astuple(self):
        class A(dataobject):
            pass
        a = A()
        t = astuple(a)
        self.assertEqual(t, ())

    def test_dataclass_astuple(self):
        A = make_dataclass("A", {'x':int, 'y':int})
        a = A(x=1,y=2)
        t = astuple(a)
        self.assertEqual(t, (1, 2))

    def test_dataclass_astuple_iterable(self):
        A = make_dataclass("A", {'x':int, 'y':int}, iterable=True)
        a = A(x=1,y=2)
        t = astuple(a)
        self.assertEqual(t, (1, 2))
        d = asdict(a)
        self.assertEqual(d, {'x':1, 'y':2})

    def test_dataobject_assign(self):
        A = make_dataclass("A", ('x', 'y'), sequence=True)
        a = A(1,2)
        if not is_pypy:
            self.assertEqual(gc.is_tracked(a), False)
        a[0] = 100
        a[1] = 200
        self.assertEqual(a.x, 100)
        self.assertEqual(a.y, 200)
        a.x = -100
        a.y = -200
        self.assertEqual(a[0], -100)
        self.assertEqual(a[1], -200)
        a = None

    def test_dataobject_local_dict(self):
        A = make_dataclass("A", ('x', 'y'), use_dict=True)
        a = A(1,2)
        a.a = 1
        # print(a.__dict__)
        self.assertEqual(a.a, 1)
        self.assertEqual(a.__dict__, {'a':1})

    def test_datatype(self):
        A = make_dataclass("A", ('x', 'y'))
        a = A(1,2)
        # self.assertEqual(repr(a), "A(x=1, y=2)")
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertEqual(asdict(a), {'x':1, 'y':2})
        if not is_pypy:
            self.assertEqual(sys.getsizeof(a), pyobject_size+2*ref_size)
        # with self.assertRaises(TypeError):     
        #     weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        with self.assertRaises(AttributeError):     
            a.z = 3
        with self.assertRaises(AttributeError):     
            a.z            
        a = None

    def test_datatype_nosq_nomp(self):
        A = make_dataclass("A", ('x', 'y'))
        a = A(1,2)
        if not is_pypy:
            self.assertEqual(gc.is_tracked(a), False)
        with self.assertRaises(TypeError):     
            a[0]
        with self.assertRaises(TypeError):     
            a['x']

    def test_datatype_sq_nomp(self):
        A = make_dataclass("A", ('x', 'y'), sequence=True)

        a = A(1,2)
        if not is_pypy:
            self.assertEqual(gc.is_tracked(a), False)
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)
        with self.assertRaises(TypeError):     
            a['x']

    def test_datatype_nosq_mp(self):
        A = make_dataclass("A", ('x', 'y'), mapping=True)

        a = A(1,2)
        if not is_pypy:
            self.assertEqual(gc.is_tracked(a), False)
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)
        with self.assertRaises(TypeError):     
            a[0]

    def test_datatype_sq_mp(self):
        A = make_dataclass("A", ('x', 'y'), sequence=True, mapping=True)

        a = A(1,2)
        if not is_pypy:
            self.assertEqual(gc.is_tracked(a), False)
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)
        a[0] = 100
        self.assertEqual(a[0], 100)

    def test_datatype_copy(self):
        A = make_dataclass("A", ('x', 'y'))
        a = A(1,2)
        b = a.__copy__()
        self.assertEqual(a, b)
        del b

    def test_datatype_copy_dict(self):
        A = make_dataclass("A", ('x', 'y'), use_dict=True)

        a = A(1,2, z=3,w=4)
        if not is_pypy:
            self.assertEqual(gc.is_tracked(a), False)
        b = a.__copy__()
        if not is_pypy:
            self.assertEqual(gc.is_tracked(b), False)
        self.assertEqual(a, b)
        del b

    def test_datatype_subscript(self):
        A = make_dataclass("A", ('x', 'y'), mapping=True)
        a = A(1,2)
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)
        a['x'] = 100
        self.assertEqual(a['x'], 100)
        a = None
        
#     def test_datatype_dict(self):
#         A = make_dataclass("A", ('x', 'y'), use_dict=True, use_weakref=True)

#         a = A(1,2)
#         self.assertEqual(len(a), 2)
#         if not is_pypy:
#             self.assertEqual(gc.is_tracked(a), False)
#         self.assertEqual(repr(a), "A(x=1, y=2)")
#         self.assertEqual(a.x, 1)
#         self.assertEqual(a.y, 2)
#         self.assertEqual(asdict(a), {'x':1, 'y':2})
#         weakref.ref(a)
#         self.assertEqual(a.__dict__, {})
        
#         a.z = 3
#         self.assertEqual(a.z, a.__dict__['z'])
#         a = None

    def test_datatype_dict2(self):
        A = make_dataclass("A", ('x', 'y'), use_dict=True)
        a = A(1,2,v=3,z=4)
        self.assertEqual(a.__dict__, {'v':3, 'z':4})
        self.assertEqual(len(a), 4)
        b = A(1,2,z=3)
        self.assertEqual(b.__dict__, {'z':3})
        self.assertEqual(repr(b), "A(x=1, y=2, **{'z': 3})")
        self.assertEqual(len(b), 3)

    def test_defaults(self):
        A = make_dataclass("A", ('x', 'y', 'z'), defaults=(100, 200, 300))
                
        a1 = A()
        self.assertEqual(repr(a1), "A(x=100, y=200, z=300)")
        self.assertEqual(a1.x, 100)
        self.assertEqual(a1.y, 200)
        self.assertEqual(a1.z, 300)
        self.assertEqual(asdict(a1), {'x':100, 'y':200, 'z':300})
        a2 = A(1,z=400)
        self.assertEqual(repr(a2), "A(x=1, y=200, z=400)")
        self.assertEqual(a2.x, 1)
        self.assertEqual(a2.y, 200)
        self.assertEqual(a2.z, 400)
        self.assertEqual(asdict(a2), {'x':1, 'y':200, 'z':400})
        a3 = A(1,2,z=400)
        self.assertEqual(repr(a3), "A(x=1, y=2, z=400)")
        self.assertEqual(a3.x, 1)
        self.assertEqual(a3.y, 2)
        self.assertEqual(a3.z, 400)
        self.assertEqual(asdict(a3), {'x':1, 'y':2, 'z':400})

    def test_dictlike_1(self):
        A = make_dataclass("A", 'x y', mapping=True)
        a = A(x=1, y=2)
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)
        a['x'] = 100
        a['y'] = 200
        self.assertEqual(a['x'], 100)
        self.assertEqual(a['y'], 200)
        
    def test_empty_fields_asdict(self):
        A = make_dataclass("A", ())
        a = A()
        d = asdict(a)
        self.assertEqual(d, {})

    def test_enable_gc(self):
        A = make_dataclass("A", ('x', 'y', 'z'))
        B = make_dataclass("B", ('x', 'y', 'z'), gc=True)
        a = A(1,2,3)
        b = B(1,2,3)
        self.assertEqual(a.x, b.x)
        self.assertEqual(a.y, b.y)
        self.assertEqual(a.z, b.z)
        if not is_pypy:
            self.assertEqual(sys.getsizeof(b)-sys.getsizeof(a), headgc_size)
                           
    def test_subclass(self):
        A = make_dataclass("A", ('x', 'y'))
                
        class B(A):
            pass

        self.assertEqual(type(A), type(B))
        if not is_pypy:
            self.assertEqual(B.__dictoffset__, 0)
            self.assertEqual(B.__weakrefoffset__, 0)
        b = B(1,2)
        if not is_pypy:
            self.assertEqual(gc.is_tracked(b), False)
        self.assertEqual(repr(b), "B(x=1, y=2)")
        self.assertEqual(b.x, 1)
        self.assertEqual(b.y, 2)
        self.assertEqual(asdict(b), {'x':1, 'y':2})
        # self.assertEqual(sys.getsizeof(b), pyobject_size + 2*ref_size)
        if not is_pypy:
            self.assertEqual(A.__basicsize__, B.__basicsize__)
            with self.assertRaises(TypeError):     
                weakref.ref(b)
        with self.assertRaises(AttributeError):     
            b.__dict__        

    def test_subclass2(self):
        A = make_dataclass("A", ('x', 'y'))

        class B(A):
            __fields__ = ('z',)
                
        class C(B):
            pass

        self.assertEqual(type(A), type(B))
        self.assertEqual(type(C), type(B))
        if not is_pypy:
            self.assertEqual(C.__dictoffset__, 0)
            self.assertEqual(C.__weakrefoffset__, 0)
        c = C(1,2,3)
        if not is_pypy:
            self.assertEqual(gc.is_tracked(c), False)
        self.assertEqual(repr(c), "C(x=1, y=2, z=3)")
        self.assertEqual(c.x, 1)
        self.assertEqual(c.y, 2)
        self.assertEqual(c.z, 3)
        self.assertEqual(asdict(c), {'x':1, 'y':2, 'z':3})
        # self.assertEqual(sys.getsizeof(c), pyobject_size + 3*ref_size)
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(c)
        with self.assertRaises(AttributeError):     
            c.__dict__
        c = None
        
    def test_keyword_args(self):
        A = make_dataclass("A", ('x', 'y', 'z'), defaults=3*(None,))

        a1 = A(x=1)
        self.assertEqual(repr(a1), "A(x=1, y=None, z=None)")
        self.assertEqual(a1.x, 1)
        self.assertEqual(a1.y, None)
        self.assertEqual(a1.z, None)
        a2 = A(x=1,y=2)
        self.assertEqual(repr(a2), "A(x=1, y=2, z=None)")
        self.assertEqual(a2.x, 1)
        self.assertEqual(a2.y, 2)
        self.assertEqual(a2.z, None)
        a3 = A(x=1,y=2,z=3)
        self.assertEqual(repr(a3), "A(x=1, y=2, z=3)")
        self.assertEqual(a3.x, 1)
        self.assertEqual(a3.y, 2)
        self.assertEqual(a3.z, 3)

    def test_keyword_args_defaults(self):
        A = make_dataclass("A", ('x', 'y', 'z'), defaults=(100, 200, 300))

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

    def test_keyword_args_defaults2(self):
        A = make_dataclass("A", ('x', 'y', 'z'), fast_new=True)

        a1 = A(x=1)
        self.assertEqual(repr(a1), "A(x=1, y=None, z=None)")
        self.assertEqual(a1.x, 1)
        self.assertEqual(a1.y, None)
        self.assertEqual(a1.z, None)
        a2 = A(x=1,y=2)
        self.assertEqual(repr(a2), "A(x=1, y=2, z=None)")
        self.assertEqual(a2.x, 1)
        self.assertEqual(a2.y, 2)
        self.assertEqual(a2.z, None)
        a3 = A(x=1,y=2,z=3)
        self.assertEqual(repr(a3), "A(x=1, y=2, z=3)")
        self.assertEqual(a3.x, 1)
        self.assertEqual(a3.y, 2)
        self.assertEqual(a3.z, 3)

    def test_keyword_args_defaults3(self):
        A = make_dataclass("A", ('x', 'y', 'z'), fast_new=True)

        a1 = A(1, y=2,)
        self.assertEqual(repr(a1), "A(x=1, y=2, z=None)")
        self.assertEqual(a1.x, 1)
        self.assertEqual(a1.y, 2)
        self.assertEqual(a1.z, None)
        a2 = A(1, **{'y':2,'z':3})
        self.assertEqual(repr(a2), "A(x=1, y=2, z=3)")
        self.assertEqual(a2.x, 1)
        self.assertEqual(a2.y, 2)
        self.assertEqual(a2.z, 3)
        a3 = A(x=1, **{'y':2,'z':3})
        self.assertEqual(repr(a3), "A(x=1, y=2, z=3)")
        self.assertEqual(a3.x, 1)
        self.assertEqual(a3.y, 2)
        self.assertEqual(a3.z, 3)
        
    def test_missing_args(self):
        A = make_dataclass("A", ("a", "b", "c"), fast_new=True, sequence=True)
        # print(A.__options__)
        a=A(1)
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], None)
        self.assertEqual(a[2], None)

    def test_missing_args2(self):
        A = make_dataclass("A", ('x', 'y', 'z'))
        a=A(1)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, None)
        self.assertEqual(a.z, None)
        
    def test_missing_args3(self):
        A = make_dataclass("A", ('a','b','c'), fast_new=True)
        a=A(1)
        self.assertEqual(a.a, 1)
        self.assertEqual(a.b, None)
        self.assertEqual(a.c, None)
        
    def test_missing_args4(self):
        A = make_dataclass("A", ('a','b','c'), defaults=(-1,), fast_new=True)
        a=A(1)
#         with self.assertRaises(TypeError):     
#             a=A(1)
        self.assertEqual(a.a, 1)
        self.assertEqual(a.b, None)
        self.assertEqual(a.c, -1)

    def test_missing_args5(self):
        A = make_dataclass("A", ('a','b','c'), defaults=(-1,-2), fast_new=True)
#         print(A.__defualts__)
        a=A(1)
        self.assertEqual(a.a, 1)
        self.assertEqual(a.b, -1)
        self.assertEqual(a.c, -2)
        
    def test_tuple2(self):
        A = make_dataclass("A", ('x', 'y', 'z'), iterable=True)
        a=A(1, 2.0, "a")
        self.assertEqual(tuple(a), (1, 2.0, "a"))

    def test_hash(self):
        A = make_dataclass("A", ("a", "b", "c"), hashable=True)
        a = A(-1, -2.0, "b")
        # print(a.__hash__)
        hash(a)

    def test_hash_subcl(self):
        A = make_dataclass("A", ("a", "b", "c"), hashable=True)
        class B(A):
            pass
        b = B(1, 2.0, "a")
        hash(b)
        
    def test_no_hash(self):
        A = make_dataclass("A", ("a", "b", "c"))
        a = A(1, 2.0, "a")
#         print(hash(a))
        with self.assertRaises(TypeError):
            hash(a)

    def test_no_hash2(self):
        A = make_dataclass("A", ("a", "b", "c"), hashable=True)
        class B(A, hashable=False):
            pass
        b = B(1, 2.0, "a")
        hash(b)
#         print(hash(a))
#         with self.assertRaises(TypeError):
#             hash(b)
            
    def test_reduce(self):
        A = make_dataclass("A", ("x","y","z"))
        a = A(1,2,3)
        o,t = a.__reduce__()
        self.assertEqual(o, A)
        self.assertEqual(t, (1,2,3))

    def test_pickle2(self):
        p = TPickle2(10, 20, 30)
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

    def test_pickle3(self):
        p = TPickle3(10, 20, 30)
        p.a = 1
        p.b = 2
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

    def test_pickle4(self):
        p = TPickle3(10, 20, 30)
        p.a = 1
        p.b = 2
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)
        
    def test_iter2(self):
        A = make_dataclass("A", ('x', 'y', 'z'), iterable=True)
        a=A(1, 2.0, "a")
        self.assertEqual(list(iter(a)), [1, 2.0, "a"])

    def test_iter3(self):
        A = make_dataclass("A", ('x', 'y', 'z'))
        a=A(1, 2.0, "a")
        with self.assertRaises(TypeError):
            iter(a)
            
    def test_iterable_base(self):
        class iterable_do(dataobject, iterable=True):
            pass
        
        class A(iterable_do):
            __fields__ = 'x', 'y', 'z'
            
        a=A(1, 2.0, "a")
        self.assertEqual(list(a), [1, 2.0, "a"])

    def test_iterable_base2(self):
        class iterable_do(dataobject, iterable=True):
            pass
        
        class A(iterable_do):
            __fields__ = 'x', 'y', 'z'
            
        a=A(1, 2.0, "a")
        self.assertEqual(list(a), [1, 2.0, "a"])

    def test_fields_dict(self):
        A = make_dataclass("A", {'x':int, 'y':int})
        a = A(x=1,y=2)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)

    if not is_pypy:
        def test_refleak_on_assignemnt_do(self):
            Test = make_dataclass("Test", "x")
            a={}
            c = sys.getrefcount(a)
            b=Test(a)
            self.assertEqual(sys.getrefcount(a), c+1)
            b.x = None
            self.assertEqual(sys.getrefcount(a), c)

    def test_join_dataclasses(self):
        C1 = make_dataclass('C1', 'a b')
        C2 = make_dataclass('C2', 'c d')
        C = join_dataclasses('C', [C1, C2])
        CC = make_dataclass('CC', 'a b c d')
        cc = CC(1,2,3,4)
        c = C(1,2,3,4)
        self.assertNotEqual(c, cc)

    def test_join_dataclasses_intersection(self):
        C1 = make_dataclass('C1', 'a b')
        C2 = make_dataclass('C2', 'b c')
        with self.assertRaises(AttributeError):
            C = join_dataclasses('C', [C1, C2])

    def test_make0(self):
        A = make_dataclass("A", ())
        a = make(A, ())
        self.assertEqual(A.__fields__, ())
        self.assertEqual(len(a), 0)
            
    def test_make1(self):
        A = make_dataclass("A", {'x':int, 'y':int})
        a = make(A, (1,2))
        self.assertEqual(a, A(1, 2))
        
    def test_make2(self):
        A = make_dataclass("A", {'x':int, 'y':int})
        a = make(A, (1,), y=2)
        self.assertEqual(a, A(1, 2))

    def test_make3(self):
        A = make_dataclass("A", {'x':int, 'y':int}, use_dict=True)
        a = make(A, (1,2), **{'z':3})
        self.assertEqual(a, A(1, 2, z=3))
        
    def test_clone1(self):
        A = make_dataclass("A", {'x':int, 'y':int})
        a = A(1,2)
        b = clone(a, x=100, y=200)
        self.assertEqual(b, A(100, 200))

    def test_clone2(self):
        A = make_dataclass("A", {'x':int, 'y':int}, use_dict=True)
        a = A(1, 2, z=3)
        b = clone(a, x=100, y=200, **{'z':300})
        self.assertEqual(b, A(100, 200, z=300))

    def test_update1(self):
        A = make_dataclass("A", {'x':int, 'y':int})
        a = A(1,2)
        update(a, x=100, y=200)
        self.assertEqual(a, A(100, 200))

    def test_update2(self):
        A = make_dataclass("A", {'x':int, 'y':int}, use_dict=True)
        a = A(1, 2, z=3)
        update(a, x=100, y=200, z=300)
        self.assertEqual(a, A(100, 200, z=300))
        
    def test_readonly(self):
        A = make_dataclass("A", {'x':int, 'y':int}, readonly=True)
        a = A(1,2)
        with self.assertRaises(AttributeError):        
            a.x = -1
        with self.assertRaises(AttributeError):        
            a.y = -2

    # def test_del_property(self):
    #     A = make_dataclass("A", 'x y')
    #     with self.assertRaises(AttributeError):        
    #         del A.x
    #     with self.assertRaises(AttributeError):        
    #         delattr(A, 'x')

    # def test_del_value(self):
    #     A = make_dataclass("A", 'x y')
    #     a = A(1, 2)
    #     with self.assertRaises(AttributeError):        
    #         del a.x
    #     with self.assertRaises(AttributeError):        
    #         delattr(a, 'x')
            
    # def test_getitem(self):
    #     A = make_dataclass("A", 'x y')
    #     a = A(x=1, y=2)
    #     with self.assertRaises(TypeError):        
    #         a.__getitem__('x')
    #     with self.assertRaises(TypeError):        
    #         a.__getitem__('y')
    #     with self.assertRaises(TypeError):        
    #         a.__getitem__(0)
    #     with self.assertRaises(TypeError):        
    #         a.__getitem__(1)

    # def test_setitem(self):
    #     A = make_dataclass("A", 'x y')
    #     a = A(x=1, y=2)
    #     with self.assertRaises(TypeError):        
    #         a.__setitem__('x', 100)
    #     with self.assertRaises(TypeError):        
    #         a.__setitem__('y', 200)
    #     with self.assertRaises(TypeError):        
    #         a.__setitem__(0, 100)
    #     with self.assertRaises(TypeError):        
    #         a.__setitem__(1, 200)
            
#     def test_getitem_sq(self):
#         A = make_dataclass("A", 'x y', sequence=True)
#         a = A(x=1, y=2)
#         self.assertEqual(a.__getitem__(0), 1)
#         self.assertEqual(a.__getitem__(1), 2)
#         with self.assertRaises(TypeError):        
#             a.__getitem__('x')
#         with self.assertRaises(TypeError):        
#             a.__getitem__('y')

#     def test_setitem_sq(self):
#         A = make_dataclass("A", 'x y', sequence=True)
#         a = A(x=1, y=2)
#         a.__setitem__(0, 100)
#         a.__setitem__(1, 200)
#         self.assertEqual(a.__getitem__(0), 100)
#         self.assertEqual(a.__getitem__(1), 200)
#         with self.assertRaises(TypeError):        
#             a.__setitem__('x', 100)
#         with self.assertRaises(TypeError):        
#             a.__setitem__('y', 200)
            
#     def test_getitem_sq_ro(self):
#         A = make_dataclass("A", 'x y', sequence=True, readonly=True)
#         a = A(x=1, y=2)
#         self.assertEqual(a.__getitem__(0), 1)
#         self.assertEqual(a.__getitem__(1), 2)
#         with self.assertRaises(TypeError):        
#             a.__getitem__('x')
#         with self.assertRaises(TypeError):        
#             a.__getitem__('y')

#     def test_setitem_sq_ro(self):
#         A = make_dataclass("A", 'x y', sequence=True, readonly=True)
#         a = A(x=1, y=2)
#         with self.assertRaises(TypeError):        
#             a.__setitem__(0, 100)
#         with self.assertRaises(TypeError):        
#             a.__setitem__(1, 200)
#         with self.assertRaises(TypeError):        
#             a.__setitem__('x', 100)
#         with self.assertRaises(TypeError):        
#             a.__setitem__('y', 200)
            
#     def test_getitem_mp(self):
#         A = make_dataclass("A", 'x y', mapping=True)
#         a = A(x=1, y=2)
#         self.assertEqual(a.__getitem__('x'), 1)
#         self.assertEqual(a.__getitem__('y'), 2)
#         with self.assertRaises(TypeError):        
#             a.__getitem__(0)
#         with self.assertRaises(TypeError):        
#             a.__getitem__(1)

#     def test_setitem_mp(self):
#         A = make_dataclass("A", 'x y', mapping=True)
#         a = A(x=1, y=2)
#         a.__setitem__('x', 100)
#         a.__setitem__('y', 200)
#         self.assertEqual(a.__getitem__('x'), 100)
#         self.assertEqual(a.__getitem__('y'), 200)
#         with self.assertRaises(TypeError):        
#             a.__setitem__(0, 100)
#         with self.assertRaises(TypeError):        
#             a.__setitem__(1, 200)
            
#     def test_getitem_mp_ro(self):
#         A = make_dataclass("A", 'x y', mapping=True, readonly=True)
#         a = A(x=1, y=2)
#         self.assertEqual(a.__getitem__('x'), 1)
#         self.assertEqual(a.__getitem__('y'), 2)
#         with self.assertRaises(TypeError):        
#             a.__getitem__(0)
#         with self.assertRaises(TypeError):        
#             a.__getitem__(1)

#     def test_setitem_mp_ro(self):
#         A = make_dataclass("A", 'x y', mapping=True, readonly=True)
#         a = A(x=1, y=2)
#         with self.assertRaises(TypeError):        
#             a.__setitem__(0, 100)
#         with self.assertRaises(TypeError):        
#             a.__setitem__(1, 200)
#         with self.assertRaises(TypeError):        
#             a.__setitem__('x', 100)
#         with self.assertRaises(TypeError):        
#             a.__setitem__('y', 200)

#     def test_getitem_mp_sq(self):
#         A = make_dataclass("A", 'x y', mapping=True, sequence=True)
#         a = A(x=1, y=2)
#         self.assertEqual(a.__getitem__('x'), 1)
#         self.assertEqual(a.__getitem__('y'), 2)
#         self.assertEqual(a.__getitem__(0), 1)
#         self.assertEqual(a.__getitem__(1), 2)

#     def test_setitem_mp_sq(self):
#         A = make_dataclass("A", 'x y', mapping=True, sequence=True)
#         a = A(x=1, y=2)
#         a.__setitem__('x', 100)
#         a.__setitem__('y', 200)
#         self.assertEqual(a.__getitem__('x'), 100)
#         self.assertEqual(a.__getitem__('y'), 200)
#         self.assertEqual(a.__getitem__(0), 100)
#         self.assertEqual(a.__getitem__(1), 200)
#         a.__setitem__(0, -100)
#         a.__setitem__(1, -200)
#         self.assertEqual(a.__getitem__('x'), -100)
#         self.assertEqual(a.__getitem__('y'), -200)
#         self.assertEqual(a.__getitem__(0), -100)
#         self.assertEqual(a.__getitem__(1), -200)

#     def test_setitem_mp_sq_ro(self):
#         A = make_dataclass("A", 'x y', mapping=True, sequence=True, readonly=True)
#         a = A(x=1, y=2)
#         self.assertEqual(a.__getitem__('x'), 1)
#         self.assertEqual(a.__getitem__('y'), 2)
#         self.assertEqual(a.__getitem__(0), 1)
#         self.assertEqual(a.__getitem__(1), 2)
#         with self.assertRaises(TypeError):        
#             a.__setitem__(0, 100)
#         with self.assertRaises(TypeError):        
#             a.__setitem__(1, 200)
#         with self.assertRaises(TypeError):        
#             a.__setitem__('x', 100)
#         with self.assertRaises(TypeError):        
#             a.__setitem__('y', 200)
        
    def test_getkey(self):
        A = make_dataclass("A", 'x y')
        a = A(x=1, y=2)
        with self.assertRaises(TypeError):        
            a['x']
        with self.assertRaises(TypeError):        
            a['y']

    def test_setkey(self):
        A = make_dataclass("A", 'x y')
        a = A(x=1, y=2)
        with self.assertRaises(TypeError):        
            a['x'] = 100
        with self.assertRaises(TypeError):        
            a['y'] = 200
            
    def test_getkey_sq(self):
        A = make_dataclass("A", 'x y', sequence=True)
        a = A(x=1, y=2)
        with self.assertRaises(TypeError):        
            a['x']
        with self.assertRaises(TypeError):        
            a['y']

    def test_setkey_sq(self):
        A = make_dataclass("A", 'x y', sequence=True)
        a = A(x=1, y=2)
        with self.assertRaises(TypeError):        
            a['x'] = 100
        with self.assertRaises(TypeError):        
            a['y'] = 200
            
    def test_getkey_sq_ro(self):
        A = make_dataclass("A", 'x y', sequence=True, readonly=True)
        a = A(x=1, y=2)
        with self.assertRaises(TypeError):        
            a['x']
        with self.assertRaises(TypeError):        
            a['y']

    def test_setkey_sq_ro(self):
        A = make_dataclass("A", 'x y', sequence=True, readonly=True)
        a = A(x=1, y=2)
        with self.assertRaises(TypeError):        
            a['x'] = 100
        with self.assertRaises(TypeError):        
            a['y'] = 200
            
    def test_getkey_mp(self):
        A = make_dataclass("A", 'x y', mapping=True)
        a = A(x=1, y=2)
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)

    def test_setkey_mp(self):
        A = make_dataclass("A", 'x y', mapping=True)
        a = A(x=1, y=2)
        a['x'] = 100
        a['y'] = 200
        self.assertEqual(a['x'], 100)
        self.assertEqual(a['y'], 200)
            
    def test_getkey_mp_ro(self):
        A = make_dataclass("A", 'x y', mapping=True, readonly=True)
        a = A(x=1, y=2)
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)

    def test_setkey_mp_ro(self):
        A = make_dataclass("A", 'x y', mapping=True, readonly=True)
        a = A(x=1, y=2)
        with self.assertRaises(TypeError):        
            a['x'] =  100
        with self.assertRaises(TypeError):        
            a['y'] = 200

    def test_getkey_mp_sq(self):
        A = make_dataclass("A", 'x y', mapping=True, sequence=True)
        a = A(x=1, y=2)
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)

    def test_setkey_mp_sq(self):
        A = make_dataclass("A", 'x y', mapping=True, sequence=True)
        a = A(x=1, y=2)
        a['x'] = 100
        a['y'] = 200
        self.assertEqual(a['x'], 100)
        self.assertEqual(a['y'], 200)
        self.assertEqual(a[0], 100)
        self.assertEqual(a[1], 200)
        a[0] = -100
        a[1] = -200
        self.assertEqual(a['x'], -100)
        self.assertEqual(a['y'], -200)
        self.assertEqual(a[0], -100)
        self.assertEqual(a[1], -200)

    def test_setkey_mp_sq_ro(self):
        A = make_dataclass("A", 'x y', mapping=True, sequence=True, readonly=True)
        a = A(x=1, y=2)
        self.assertEqual(a['x'], 1)
        self.assertEqual(a['y'], 2)
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)
        with self.assertRaises(TypeError):        
            a[0] = 100
        with self.assertRaises(TypeError):        
            a[1] = 200
        with self.assertRaises(TypeError):        
            a['x'] = 100
        with self.assertRaises(TypeError):        
            a['y'] = 200
            
def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DataobjectTest))
    return suite
