import unittest
import sys
import gc
import weakref
import pickle, copy

from recordclass import make_arrayclass, datatype
# from recordclass.utils import headgc_size, ref_size, pyobject_size, pyvarobject_size, pyssize

if 'PyPy' in sys.version:
    is_pypy = True
else:
    is_pypy = False
    from recordclass.utils import headgc_size, ref_size, pyobject_size, pyvarobject_size, pyssize


TPickle1 = make_arrayclass("TPickle1", 3)

class arrayobjectTest(unittest.TestCase):

#     def test_create0(self):
#         gc.collect()
#         cnt1 = gc.get_count()
#         A = make_arrayclass("A", 2)
# #         B = make_arrayclass("B", varsize=True)
# #         b = B([], ())
#         a = A({}, b)
#         cnt2 = gc.get_count()
#         self.assertEqual(gc.is_tracked(a), False)
# #         self.assertEqual(gc.is_tracked(b), False)
#         del a
#         gc.collect()
#         cnt3 = gc.get_count()
#         self.assertEqual(cnt1, cnt3)

#     def test_create1(self):
#         gc.collect()
#         cnt1 = gc.get_count()
#         A = make_arrayclass("A", 2)
# #         B = make_arrayclass("B", varsize=True)
# #         C = make_arrayclass("C", 2, varsize=True)
#         b = A([], ())
# #         c = C(1,2,{1:2,3:4},[1,2])
# #         b1 = B(1, b)
#         a = [b1, c]
#         cnt2 = gc.get_count()
#         self.assertEqual(gc.is_tracked(b), False)
# #         self.assertEqual(gc.is_tracked(b1), False)
# #         self.assertEqual(gc.is_tracked(c), False)
#         del a
#         gc.collect()
#         cnt3 = gc.get_count()
#         self.assertEqual(cnt1, cnt3)

#     def test_gc_create0(self):
#         gc.collect()
#         cnt1 = gc.get_count()
#         A = make_arrayclass("A", 2, gc=True)
# #         B = make_arrayclass("B", varsize=True, gc=True)
# #         b = B([], ())
#         a = A({}, b)
#         cnt2 = gc.get_count()
#         self.assertEqual(gc.is_tracked(a), True)
# #         self.assertEqual(gc.is_tracked(b), True)
#         del a
#         gc.collect()
#         cnt3 = gc.get_count()
#         self.assertEqual(cnt1, cnt3)

#     def test_gc_create1(self):
#         gc.collect()
#         cnt1 = gc.get_count()
#         A = make_arrayclass("A", 2, gc=True)
# #         B = make_arrayclass("B", varsize=True, gc=True)
# #         C = make_arrayclass("C", 2, varsize=True, gc=True)
#         b = A([], ())
# #         c = C(1,2,{1:2,3:4},[1,2])
# #         b1 = B(1, b)
#         a = [b1, c]
#         cnt2 = gc.get_count()
#         self.assertEqual(gc.is_tracked(b), True)
# #         self.assertEqual(gc.is_tracked(b1), True)
# #         self.assertEqual(gc.is_tracked(c), True)
#         del a
#         gc.collect()
#         cnt3 = gc.get_count()
#         self.assertEqual(cnt1, cnt3)
        
    def test_fields0(self):
        A = make_arrayclass("A", 0)
        a = A()
        self.assertEqual(len(a), 0)
        self.assertEqual(repr(a), "A()")
        with self.assertRaises(IndexError): 
            a[0]
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        a = None
        with self.assertRaises(TypeError):
            A(1)

    def test_fields1(self):
        A = make_arrayclass("A", 1)
        a = A(100)
        self.assertEqual(repr(a), "A(100)")
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0], 100)
        self.assertEqual(a[-1], 100)
        with self.assertRaises(IndexError): 
            a[1]
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        a = None
        with self.assertRaises(TypeError):
            A(1,2)

    def test_gc_fields0(self):
        A = make_arrayclass("A", 0, gc=True)
        a = A()
        self.assertEqual(repr(a), "A()")
        self.assertEqual(len(a), 0)
        with self.assertRaises(IndexError): 
            a[0]
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        a = None
        with self.assertRaises(TypeError):
            A(1)

    def test_gc_fields1(self):
        A = make_arrayclass("A", 1, gc=True)
        a = A(100)
        self.assertEqual(repr(a), "A(100)")
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0], 100)
        self.assertEqual(a[-1], 100)
        with self.assertRaises(IndexError): 
            a[1]
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        a = None
        with self.assertRaises(TypeError):
            A(1,2)
            

    def test_fields_fixsize1(self):
        A = make_arrayclass("A", 2)
#         print(A.__dict__)
        a = A(100, 200)
        self.assertEqual(repr(a), "A(100, 200)")
        self.assertEqual(len(a), 2)
        self.assertEqual(a[0], 100)
        self.assertEqual(a[1], 200)
        self.assertEqual(a[-1], 200)
        a[0] = -100
        a[1] = -200
        self.assertEqual(a[0], -100)
        self.assertEqual(a[1], -200)
        with self.assertRaises(IndexError): 
            a[2]
        if not is_pypy:
            with self.assertRaises(TypeError):     
                weakref.ref(a)
        with self.assertRaises(AttributeError):     
            a.__dict__
        a = None

    def test_tuple(self):
        A = make_arrayclass("A", 3)
        a=A(1, 2.0, "a")
        self.assertEqual(tuple(a), (1, 2.0, "a"))

    def test_iter(self):
        A = make_arrayclass("A", 3)
        a=A(1, 2.0, "a")
        self.assertEqual(list(iter(a)), [1, 2.0, "a"])

    def test_hash(self):
        A = make_arrayclass("A", 3, hashable=True)
        a=A(1, 2.0, "a")
        hash(a)
        
    def test_arrayclass_asdict(self):
        from recordclass import asdict
        A = make_arrayclass("A", 3)
        a = A()
        with self.assertRaises(TypeError):
            t = asdict(a)        

    def test_missing_args(self):
        A = make_arrayclass("A", 3)
        a=A(1)
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], None)
        self.assertEqual(a[2], None)

    def test_pickle1(self):
        p = TPickle1(10, 20, 30)
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

#     def test_pickle4(self):
#         p = TPickleV1(10, 20, 30)
#         for module in (pickle,):
#             loads = getattr(module, 'loads')
#             dumps = getattr(module, 'dumps')
#             for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
#                 tmp = dumps(p, protocol)
#                 q = loads(tmp)
#                 self.assertEqual(p, q)

def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(arrayobjectTest))
    return suite
        