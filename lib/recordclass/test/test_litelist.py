import unittest
from recordclass import litelist, litelist_fromargs

import gc
import pickle
import sys

class litelistTest(unittest.TestCase):

    def test_len(self):
        a = litelist([])
        self.assertEqual(len(a), 0)
        a = litelist([1])
        self.assertEqual(len(a), 1)
        
    def test_items(self):
        a = litelist([1,2,3])
        self.assertEqual(a[0], 1)
        self.assertEqual(a[-1], 3)
        a[1] = 100
        self.assertEqual(a[1], 100)

    def test_remove(self):
        a = litelist([1,2,3])
        a.remove(2)
        self.assertEqual(a[0], 1)
        self.assertEqual(a[-1], 3)
        a = litelist([1,2,3])
        a.remove(1)
        self.assertEqual(a[0], 2)
        self.assertEqual(a[-1], 3)
        a = litelist([1,2,3])
        a.remove(3)
        self.assertEqual(a[0], 1)
        self.assertEqual(a[-1], 2)
        
    def test_gc(self):
        a = litelist([1,2,3])
        # self.assertEqual(sys.getsizeof(a), a.__sizeof__())

    def test_append(self):
        a = litelist([])
        a.append(1)
        self.assertEqual(a[0], 1)
        a.append(2)
        self.assertEqual(a[1], 2)
        a.append(3)
        self.assertEqual(a[2], 3)

    def test_extend1(self):
        a = litelist([])
        a.extend([1,2,3])
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)
        self.assertEqual(a[2], 3)

    def test_extend2(self):
        a = litelist([1,2,3])
        a.extend([4,5,6])
        self.assertEqual(a[3], 4)
        self.assertEqual(a[4], 5)
        self.assertEqual(a[5], 6)
        
    def test_repr(self):
        a = litelist([])
        self.assertEqual(repr(a), "litelist([])")
        a = litelist([1])
        self.assertEqual(repr(a), "litelist([1])")
        a = litelist([1, 2])
        self.assertEqual(repr(a), "litelist([1, 2])")

    def test_iter(self):
        a = litelist([1,2,3])
        self.assertEqual(list(a), [1,2,3])
        self.assertEqual(tuple(a), (1,2,3))

    def test_iter2(self):
        from recordclass._litelist import litelistiter
        a = litelist([1,2,3])
        self.assertTrue(isinstance(iter(a), litelistiter))        

    def test_getslice1(self):
        a = litelist([1,2,3])
        self.assertEqual(len(a[1:1]), 0)
        self.assertEqual(repr(a[1:1]), "litelist([])")
        self.assertEqual(len(a[1:2]), 1)
        self.assertEqual(repr(a[1:2]), "litelist([2])")
        self.assertEqual(len(a[:-1]), 2)
        self.assertEqual(repr(a[:-1]), "litelist([1, 2])")

    def test_getslice2(self):
        a = litelist([1,2,3])
        self.assertEqual(repr(a[:]), "litelist([1, 2, 3])")

    def test_setslice1(self):
        a = litelist([1,2,3])
        a[1:1] = []
        self.assertEqual(repr(a), "litelist([1, 2, 3])")

    def test_setslice2(self):
        a = litelist([1,2,3])
        a[1:2] = [100]
        self.assertEqual(repr(a), "litelist([1, 100, 3])")

    def test_setslice3(self):
        a = litelist([1,2,3])
        a[:-1] = [100,200]
        self.assertEqual(repr(a), "litelist([100, 200, 3])")

    def test_setslice4(self):
        a = litelist([1,2,3])
        a[:] = [100,200,300]
        self.assertEqual(repr(a), "litelist([100, 200, 300])")
        
    def test_delitem1(self):
        a = litelist([1,2,3,4,5])
        del a[1]
        self.assertEqual(repr(a), "litelist([1, 3, 4, 5])")

    def test_delitem2(self):
        a = litelist([1,2,3,4,5])
        del a[0]
        self.assertEqual(repr(a), "litelist([2, 3, 4, 5])")

    def test_delitem3(self):
        a = litelist([1,2,3,4,5])
        del a[4]
        self.assertEqual(repr(a), "litelist([1, 2, 3, 4])")

    def test_delitem4(self):
        a = litelist([1,2,3,4,5])
        del a[-1]
        self.assertEqual(repr(a), "litelist([1, 2, 3, 4])")
        
    def test_iterator_pickle(self):
        # Userlist iterators don't support pickling yet since
        # they are based on generators.
        data = litelist([4, 5, 6, 7])
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            itorg = iter(data)
            d = pickle.dumps(itorg, proto)
            it = pickle.loads(d)
            self.assertEqual(type(itorg), type(it))
            self.assertEqual(list(litelist(it)), list(data))

        it = pickle.loads(d)
        next(it)
        d = pickle.dumps(it)
        self.assertEqual(list(litelist(it)), list(data[1:]))

    def test_refleak_on_assignemnt(self):
        a = 1
        ll = litelist([a,2,3])
        c = sys.getrefcount(a)
        b = ll[0]
        self.assertEqual(sys.getrefcount(a), c+1)
        ll[0] = None        
        self.assertEqual(sys.getrefcount(a), c)
        
    def test_litelist_fromargs1(self):
        a = litelist_fromargs()
        self.assertEqual(len(a), 0)
        self.assertEqual(repr(a), "litelist([])")

    def test_litelist_fromargs2(self):
        a = litelist_fromargs(1,2,3,4,5)
        self.assertEqual(len(a), 5)
        self.assertEqual(repr(a), "litelist([1, 2, 3, 4, 5])")
        
def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(litelistTest))
    return suite

