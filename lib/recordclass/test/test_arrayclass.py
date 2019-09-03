import unittest
from recordclass import arrayclass
try:
    from test import support, seq_tests
except:
    from test import test_support as support

import gc
import pickle

Array0 = arrayclass('Array0', 0)
Array1 = arrayclass('Array1', 1)
Array2 = arrayclass('Array2', 2)
Array3 = arrayclass('Array3', 3)
Array4 = arrayclass('Array4', 4)

Array1RO = arrayclass('Array1RO', 1, readonly=True)

class ArrayClassTest(unittest.TestCase):

    def test_constructors(self):
        self.assertEqual(Array0(), Array0())
        self.assertEqual(Array3(1, 2, 3), Array3(1, 2, 3))
        self.assertEqual(Array1(''), Array1(''))

    def test_truth(self):
        self.assertTrue(not Array0())
        self.assertTrue(Array1(42))

    def test_readonly(self):
        a1 = Array1RO(100)
        self.assertEqual(a1[0], 100)
        with self.assertRaises(TypeError):
            a1[0] = -100
        
    def test_len(self):
        self.assertEqual(len(Array0()), 0)
        self.assertEqual(len(Array1(0)), 1)
        self.assertEqual(len(Array3(0, 1, 2)), 3)

    def test_memoryslotsresizebug(self):
        # Check that a specific bug in _PyTuple_Resize() is squashed.
        Array1000 = arrayclass('Array1000', 1000)
        def f():
            for i in range(1000):
                yield i
        self.assertEqual(list(Array1000(*f())), list(Array1000(*range(1000))))
 
    def test_repr(self):
        l0 = Array0()
        l2 = Array3(0, 1, 2)

        self.assertEqual(repr(l0), "Array0()")
        self.assertEqual(repr(l2), "Array3(0, 1, 2)")

    def _not_tracked(self, t):
        # Nested memoryslotss can take several collections to untrack
        gc.collect()
        gc.collect()
        self.assertFalse(gc.is_tracked(t), t)

    def _tracked(self, t):
        self.assertTrue(gc.is_tracked(t), t)
        gc.collect()
        gc.collect()
        self.assertTrue(gc.is_tracked(t), t)

    def test_hash(self):
        A = arrayclass('A', 2, readonly=True)
        a = A(1, 2)
        self.assertEqual(hash(a), hash(tuple(a)))
        B = arrayclass('B', 2, hashable=True)
        b = B(1, 2)
        hash_b = hash(b)
        self.assertEqual(hash_b, hash(tuple(b)))
        b[0] = -1
        self.assertNotEqual(hash(b), hash_b)
        
    def test_pickle(self):
        data = Array4(4, 5, 6, 7)
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            d = pickle.dumps(data, proto)
            d2 = pickle.loads(d)
            self.assertEqual(type(d2), type(data))
            self.assertEqual(Array4(*d2), Array4(*data))


def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ArrayClassTest))
    return suite

