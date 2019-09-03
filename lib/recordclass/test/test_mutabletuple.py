import unittest
from recordclass import mutabletuple
try:
    from test import support
except:
    from test import test_support as support

import gc
import pickle

class mutabletupleTest(unittest.TestCase):
    type2test = mutabletuple

    def test_constructors(self):
        #super().test_constructors()
        # calling built-in types without argument must return empty
        self.assertEqual(mutabletuple(), ())
        self.assertEqual(mutabletuple([]), mutabletuple([]))
        self.assertEqual(mutabletuple(0, 1, 2, 3), mutabletuple(0, 1, 2, 3))
        self.assertEqual(mutabletuple(''), mutabletuple(''))

    def test_truth(self):
        #super().test_truth()
        self.assertTrue(not mutabletuple())
        self.assertTrue(mutabletuple(42))

    def test_len(self):
        #super().test_len()
        self.assertEqual(len(mutabletuple()), 0)
        self.assertEqual(len(mutabletuple(0)), 1)
        self.assertEqual(len(mutabletuple(0, 1, 2)), 3)

    def test_concat(self):
        t1 = mutabletuple(1,2)
        t2 = mutabletuple(3,4)
        t3 = t1 + t2
        t4 = t1 + (3,4)
        t = mutabletuple(1,2,3,4)
        self.assertEqual(t3, t)
        self.assertEqual(t4, t)
        
    def test_slice1(self):
        t = mutabletuple()
        self.assertEqual(t, t[:])
        self.assertEqual(t, t[:1])
        self.assertEqual(t, t[:2])
        
    def test_slice2(self):
        t = mutabletuple(1)
        self.assertEqual(t, t[:])
        self.assertEqual(t, t[:1])
        self.assertEqual(t, t[:2])

    def test_slice3(self):
        t = mutabletuple(1,2,3)
        self.assertEqual(t, t[:])
        self.assertEqual(t[:1], mutabletuple(1))
        self.assertEqual(t[:2], mutabletuple(1,2))
        
    def test_mutabletupleresizebug(self):
        # Check that a specific bug in _PyTuple_Resize() is squashed.
        def f():
            for i in range(1000):
                yield i
        self.assertEqual(list(mutabletuple(*f())), list(range(1000)))
 
    def test_repr(self):
        l0 = mutabletuple()
        l2 = mutabletuple(0, 1, 2)
        a0 = self.type2test(*l0)
        a2 = self.type2test(*l2)

        self.assertEqual(str(a0), repr(l0))
        self.assertEqual(str(a2), repr(l2))
        self.assertEqual(repr(a0), "mutabletuple()")
        self.assertEqual(repr(a2), "mutabletuple(0, 1, 2)")

    def test_not_tracked(self):
        t = mutabletuple(1,2,3)
        gc.collect()
        gc.collect()
        self.assertFalse(gc.is_tracked(t))

    def test_repr_large(self):
        # Check the repr of large list objects
        def check(n):
            l = (0,) * n
            s = repr(l)
            self.assertEqual(s,
                '(' + ', '.join(['0'] * n) + ')')
        check(10)       # check our checking code
        check(1000000)
    
    def test_iterator_pickle(self):
        # Userlist iterators don't support pickling yet since
        # they are based on generators.
        data = self.type2test([4, 5, 6, 7])
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            itorg = iter(data)
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            self.assertEqual(type(itorg), type(it))
            self.assertEqual(self.type2test(*it), self.type2test(data))

        it = pickle.loads(d)
        next(it)
        d = pickle.dumps(it)
        self.assertEqual(self.type2test(*it), self.type2test(data)[1:])
        
    def test_reversed(self):
        t = mutabletuple(1,2,3)
        tr = mutabletuple(*reversed(t))
        self.assertEqual(tr, mutabletuple(3,2,1))

#     def test_reversed_pickle(self):
#         data = self.type2test(4, 5, 6, 7)
#         for proto in range(pickle.HIGHEST_PROTOCOL + 1):
#             itorg = reversed(data)
#             d = pickle.dumps(itorg, proto)
#             it = pickle.loads(d)
#             self.assertEqual(type(itorg), type(it))
#             self.assertEqual(self.type2test(*it), self.type2test(*reversed(data)))
    
#             it = pickle.loads(d)
#             next(it)
#             d = pickle.dumps(it, proto)
#             self.assertEqual(self.type2test(*it), self.type2test(*reversed(data))[1:])

    def test_no_comdat_folding(self):
        # Issue 8847: In the PGO build, the MSVC linker's COMDAT folding
        # optimization causes failures in code that relies on distinct
        # function addresses.
        class T(mutabletuple): pass
        with self.assertRaises(TypeError):
            [3,] + T(1,2)

def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(mutabletupleTest))
    return suite

