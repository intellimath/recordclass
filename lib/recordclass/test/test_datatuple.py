import unittest
import pickle, copy
import keyword
import re
import sys
import gc
import weakref

from recordclass import make_dataclass, make_arrayclass, datatype, asdict
from recordclass.utils import headgc_size, ref_size, pyobject_size, pyvarobject_size, pyssize
from recordclass import DataclassStorage

TPickleV5 = make_dataclass("TPickleV5", ('x','y','z'), varsize=True)
TPickleV6 = make_dataclass("TPickleV6", ('x','y','z'), varsize=True, use_dict=True)
TPickleV7 = make_dataclass("TPickleV7", ('x','y','z'), varsize=True)
TPickleV8 = make_dataclass("TPickleV8", ('x','y','z'), varsize=True, use_dict=True)

class datatupleTest(unittest.TestCase):
    
    def test_datatype_copy1(self):
        A = make_dataclass("A", ('x', 'y'), varsize=True)
        a = A(1,2,3,4,5)
        self.assertEqual(gc.is_tracked(a), False)
        b = a.__copy__()
        self.assertEqual(gc.is_tracked(b), False)
        self.assertEqual(a, b)

    def test_datatype_copy2(self):
        A = make_dataclass("A", ('x', 'y'), varsize=True, use_dict=True)
        a = A(1,2,3,4,5)
        a.a=1
        a.b=2
        self.assertEqual(gc.is_tracked(a), False)
        b = a.__copy__()
        self.assertEqual(gc.is_tracked(b), False)
        self.assertEqual(a, b)

    def test_pickle5(self):
        p = TPickleV5(10, 20, 30)
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

    def test_pickle6(self):
        p = TPickleV6(10, 20, 30)
        p.a = 1
        p.b = 2
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)
                
    def test_pickle7(self):
        p = TPickleV7(10, 20, 30, 100, 200, 300)
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

    def test_pickle8(self):
        p = TPickleV8(10, 20, 30, 100, 200, 300)
        p.a = 1
        p.b = 2
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)

    def test_refleak_on_assignemnt_dt(self):
        Test = make_dataclass("Test", "x", varsize=True)
        a={}
        c = sys.getrefcount(a)
        b=Test(a)
        self.assertEqual(sys.getrefcount(a), c+1)
        b.x = None
        self.assertEqual(sys.getrefcount(a), c)

def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(datatupleTest))
    return suite
