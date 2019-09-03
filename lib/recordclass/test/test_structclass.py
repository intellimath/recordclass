"""Unit tests for structclass.py."""
import unittest, doctest, operator
from recordclass import structclass, join_classes
from collections import OrderedDict
import pickle, copy
import keyword
import re
import sys


try:
    from test import support
except:
    from test import test_support as support


TestNT = structclass('TestNT', 'x y z')    # type used for pickle tests
TestNT2 = structclass('TestNT2', 'x y z', usedict=True)    # type used for pickle tests

class structclassTest(unittest.TestCase):

    def test_factory(self):
        Point = structclass('Point', 'x y')
        self.assertEqual(Point.__name__, 'Point')
        self.assertEqual(Point.__doc__, 'Point(x, y)')
        #self.assertEqual(Point.__slots__, ('x','y'))
        self.assertEqual(Point.__module__, __name__)
        self.assertEqual(Point.__fields__, ('x', 'y'))

        self.assertRaises(ValueError, structclass, 'abc%', 'efg ghi')       # type has non-alpha char
        self.assertRaises(ValueError, structclass, 'class', 'efg ghi')      # type has keyword
        self.assertRaises(ValueError, structclass, '9abc', 'efg ghi')       # type starts with digit

        self.assertRaises(ValueError, structclass, 'abc', 'efg g%hi')       # field with non-alpha char
        self.assertRaises(ValueError, structclass, 'abc', 'abc class')      # field has keyword
        self.assertRaises(ValueError, structclass, 'abc', '8efg 9ghi')      # field starts with digit
        self.assertRaises(ValueError, structclass, 'abc', '_efg ghi')       # field with leading underscore
        self.assertRaises(ValueError, structclass, 'abc', 'efg efg ghi')    # duplicate field

        structclass('Point0', 'x1 y2')   # Verify that numbers are allowed in names
        structclass('_', 'a b c')        # Test leading underscores in a typename

        nt = structclass('nt', 'the quick brown fox')                       # check unicode input
        self.assertNotIn("u'", repr(nt.__fields__))
        nt = structclass('nt', ('the', 'quick'))                           # check unicode input
        self.assertNotIn("u'", repr(nt.__fields__))

        self.assertRaises(TypeError, Point._make, [11])                     # catch too few args
        self.assertRaises(TypeError, Point._make, [11, 22, 33])             # catch too many args

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    def test_factory_doc_attr(self):
        Point = structclass('Point', 'x y')
        self.assertEqual(Point.__doc__, 'Point(x, y)')

#     def test_name_fixer(self):
#         for spec, renamed in [
#             [('efg', 'g%hi'),  ('efg', '_1')],                              # field with non-alpha char
#             [('abc', 'class'), ('abc', '_1')],                              # field has keyword
#             [('8efg', '9ghi'), ('_0', '_1')],                               # field starts with digit
#             [('abc', '_efg'), ('abc', '_1')],                               # field with leading underscore
#             [('abc', 'efg', 'efg', 'ghi'), ('abc', 'efg', '_2', 'ghi')],    # duplicate field
#             [('abc', '', 'x'), ('abc', '_1', 'x')],                         # fieldname is a space
#         ]:
#             self.assertEqual(structclass('NT', spec, rename=True).__fields__, renamed)

            
    def test_defaults(self):
        Point = structclass('Point', 'x y', defaults=(10, 20))              # 2 defaults
        self.assertEqual(tuple(Point(1, 2)), (1, 2))
        self.assertEqual(tuple(Point(1)), (1, 20))
        self.assertEqual(tuple(Point()), (10, 20))

        Point = structclass('Point', 'x y', defaults=(20,))                 # 1 default
        self.assertEqual(tuple(Point(1, 2)), (1, 2))
        self.assertEqual(tuple(Point(1)), (1, 20))

        Point = structclass('Point', 'x y', defaults=())                     # 0 defaults
        self.assertEqual(tuple(Point(1, 2)), (1, 2))
        with self.assertRaises(TypeError):
            Point(1)

        with self.assertRaises(TypeError):                                  # catch too few args
            Point()
        with self.assertRaises(TypeError):                                  # catch too many args
            Point(1, 2, 3)
        with self.assertRaises(TypeError):                                  # too many defaults
            Point = structclass('Point', 'x y', defaults=(10, 20, 30))
        with self.assertRaises(TypeError):                                  # non-iterable defaults
            Point = structclass('Point', 'x y', defaults=10)
        with self.assertRaises(TypeError):                                  # another non-iterable default
            Point = structclass('Point', 'x y', defaults=False)

        Point = structclass('Point', 'x y', defaults=None)                   # default is None
        self.assertIsNone(Point.__new__.__defaults__, None)
        self.assertEqual(tuple(Point(10, 20)), (10, 20))
        with self.assertRaises(TypeError):                                  # catch too few args
            Point(10)

        Point = structclass('Point', 'x y', defaults=[10, 20])               # allow non-tuple iterable
        self.assertEqual(Point.__new__.__defaults__, (10, 20))
        self.assertRaises(TypeError, Point(1, 2), (1, 2))
        self.assertEqual(Point(1, 2), Point(1, 2))
        self.assertNotEqual(Point(1, 2), Point(10, 20))
        self.assertEqual(Point(1), Point(1, 20))
        self.assertEqual(Point(), Point(10, 20))

        Point = structclass('Point', 'x y', defaults=iter([10, 20]))         # allow plain iterator
        self.assertEqual(Point.__new__.__defaults__, (10, 20))
        self.assertEqual(tuple(Point(1, 2)), (1, 2))
        self.assertEqual(tuple(Point(1)), (1, 20))
        self.assertEqual(tuple(Point()), (10, 20))
            
    def test_instance(self):
        Point = structclass('Point', 'x y')
        p = Point(11, 22)
        self.assertEqual(p, Point(x=11, y=22))
        self.assertEqual(p, Point(11, y=22))
        self.assertEqual(p, Point(y=22, x=11))
        self.assertEqual(p, Point(*(11, 22)))
        self.assertEqual(p, Point(**dict(x=11, y=22)))
        self.assertRaises(TypeError, eval, 'Point(XXX=1, y=2)', locals())   # wrong keyword argument
        self.assertRaises(TypeError, eval, 'Point(x=1)', locals())          # missing keyword argument
        self.assertEqual(repr(p), 'Point(x=11, y=22)')
        #self.assertNotIn('__weakref__', dir(p))
        #print(p)
        self.assertEqual(p, Point._make([11, 22]))                          # test _make classmethod
        self.assertEqual(p.__fields__, ('x', 'y'))                             # test __fields__ attribute
        self.assertEqual(tuple(p._replace(x=1)), (1, 22))                          # test _replace method
        self.assertEqual(p._asdict(), dict(x=1, y=22))                     # test _asdict method
        #self.assertEqual(vars(p), p._asdict())                              # verify that vars() works

        p.x = -1
        self.assertEqual(p.x, -1)

        # verify that field string can have commas
        Point = structclass('Point', 'x, y')
        p = Point(x=11, y=22)
        self.assertEqual(repr(p), 'Point(x=11, y=22)')

        # verify that fieldspec can be a non-string sequence
        Point = structclass('Point', ('x', 'y'))
        p = Point(x=11, y=22)
        self.assertEqual(repr(p), 'Point(x=11, y=22)')

    def test_tupleness(self):
        Point = structclass('Point', 'x y')
        p = Point(11, 22)

        self.assertEqual(tuple(p), (11, 22))                                # coercable to a real tuple
        self.assertEqual(list(p), [11, 22])                                 # coercable to a list
        self.assertEqual(max(p), 22)                                        # iterable
        self.assertEqual(max(*p), 22)                                       # star-able
        x, y = p
        self.assertEqual(tuple(p), (x, y))                                         # unpacks like a tuple
        
        self.assertEqual(p.x, x)
        self.assertEqual(p.y, y)
        self.assertRaises(AttributeError, eval, 'p.z', locals())
        
        Point2 = structclass('Point', 'x y', assequence=False)
        p2 = Point2(11, 22)
        with self.assertRaises(TypeError):
            p2[3]

    def test_odd_sizes(self):
        Zero = structclass('Zero', '')
        self.assertEqual(tuple(Zero()), ())
        self.assertEqual(tuple(Zero._make([])), ())
        self.assertEqual(repr(Zero()), 'Zero()')
        self.assertEqual(Zero()._asdict(), {})
        self.assertEqual(Zero().__fields__, ())

        Dot = structclass('Dot', 'd')
        self.assertEqual(tuple(Dot(1)), (1,))
        self.assertEqual(tuple(Dot._make([1])), (1,))
        self.assertEqual(Dot(1).d, 1)
        self.assertEqual(repr(Dot(1)), 'Dot(d=1)')
        self.assertEqual(Dot(1)._asdict(), {'d':1})
        self.assertEqual(tuple(Dot(1)._replace(d=999)), (999,))
        self.assertEqual(Dot(1).__fields__, ('d',))

        # n = 5000
        n = 254 # SyntaxError: more than 255 arguments:
        import string, random
        names = list(set(''.join([random.choice(string.ascii_letters)
                                  for j in range(10)]) for i in range(n)))
        n = len(names)
        Big = structclass('Big', names)
        b = Big(*range(n))
        self.assertEqual(tuple(b), tuple(range(n)))
        self.assertEqual(tuple(Big._make(range(n))), tuple(range(n)))
        for pos, name in enumerate(names):
            self.assertEqual(getattr(b, name), pos)
        repr(b)                                 # make sure repr() doesn't blow-up
        d = b._asdict()
        d_expected = dict(zip(names, range(n)))
        self.assertEqual(d, d_expected)
        b2 = b._replace(**dict([(names[1], 999),(names[-5], 42)]))
        b2_expected = list(range(n))
        b2_expected[1] = 999
        b2_expected[-5] = 42
        self.assertEqual(tuple(b2), tuple(b2_expected))
        self.assertEqual(b.__fields__, tuple(names))

    def test_pickle(self):
        p = TestNT(x=10, y=20, z=30)
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)
                self.assertEqual(p.__fields__, q.__fields__)
                self.assertNotIn(b'OrderedDict', dumps(p, protocol))

    def test_pickle2(self):
        p = TestNT2(x=10, y=20, z=30)
        p.a = 100
        p.b = 200
        p.c = 300
        for module in (pickle,):
            loads = getattr(module, 'loads')
            dumps = getattr(module, 'dumps')
            for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                tmp = dumps(p, protocol)
                q = loads(tmp)
                self.assertEqual(p, q)
                self.assertEqual(p.__dict__, q.__dict__)
                self.assertEqual(p.__fields__, q.__fields__)
                self.assertNotIn(b'OrderedDict', dumps(p, protocol))
                
    def test_copy(self):
        p = TestNT(x=10, y=20, z=30)
        for copier in copy.copy, copy.deepcopy:
            q = copier(p)
            self.assertEqual(p, q)
            self.assertEqual(p.__fields__, q.__fields__)

    def test_name_conflicts(self):
        # Some names like "self", "cls", "tuple", "itemgetter", and "property"
        # failed when used as field names.  Test to make sure these now work.
        T = structclass('T', 'itemgetter property self cls tuple')
        t = T(1, 2, 3, 4, 5)
        self.assertEqual(tuple(t), (1,2,3,4,5))
        newt = t._replace(itemgetter=10, property=20, self=30, cls=40, tuple=50)
        self.assertEqual(tuple(newt), (10,20,30,40,50))

        # Broader test of all interesting names in a template
        with support.captured_stdout() as template:
            T = structclass('T', 'x')
        words = set(re.findall('[A-Za-z]+', template.getvalue()))
        words -= set(keyword.kwlist)
        words = list(words)
        if 'None' in words:
            words.remove('None')
        T = structclass('T', words)
        # test __new__
        values = tuple(range(len(words)))
        t = T(*values)
        self.assertEqual(tuple(t), values)
        t = T(**dict(zip(T.__fields__, values)))
        self.assertEqual(tuple(t), values)
        # test _make
        t = T._make(values)
        self.assertEqual(tuple(t), values)
        # exercise __repr__
        repr(t)
        # test _asdict
        self.assertEqual(t._asdict(), dict(zip(T.__fields__, values)))
        # test _replace
        t = T._make(values)
        newvalues = tuple(v*10 for v in values)
        newt = t._replace(**dict(zip(T.__fields__, newvalues)))
        self.assertEqual(tuple(newt), newvalues)
        # test __fields__
        self.assertEqual(T.__fields__, tuple(words))
        # test __getnewargs__
        #self.assertEqual(t.__getnewargs__(), newvalues)

    def test_repr(self):
        with support.captured_stdout() as template:
            A = structclass('A', 'x')
        a = A(1)
        self.assertEqual(repr(a), 'A(x=1)')
        # repr should show the name of the subclass
        class B(A):
            pass
        b = B(1)
        self.assertEqual(repr(b), 'B(x=1)')
        
    def test_join_structclasses(self):
        C1 = structclass('C1', 'a b')
        C2 = structclass('C2', 'c d')
        C = join_classes('C', [C1, C2])
        CC = structclass('C', 'a b c d')
        c = C(1,2,3,4)
        cc = CC(1,2,3,4)
        self.assertEqual(c, cc)

    def test_join_structclasses_intersection(self):
        C1 = structclass('C1', 'a b')
        C2 = structclass('C2', 'b c')
        with self.assertRaises(AttributeError):
            C = join_classes('C', [C1, C2])
        
    def test_dict(self):
        A = structclass('A', 'a b c', usedict=True)
        a=A(a=1, b=2, c=3, d=100, e=200)
        self.assertEqual(a.a, 1)
        self.assertEqual(a.b, 2)
        self.assertEqual(a.c, 3)
        self.assertEqual(a.__dict__, {'d':100, 'e':200})
        self.assertEqual(len(a), 3)
        
    def test_hash(self):
        A = structclass('A', 'x y', readonly=True)
        a = A(1, 2)
        self.assertEqual(hash(a), hash(tuple(a)))
        B = structclass('B', 'x y', hashable=True)
        b = B(1, 2)
        hash_b = hash(b)
        self.assertEqual(hash_b, hash(tuple(b)))
        b.x = -1
        self.assertNotEqual(hash(b), hash_b)
        

#     def test_source(self):
#         # verify that _source can be run through exec()
#         tmp = recordclass('NTColor', 'red green blue')
#         globals().pop('NTColor', None)          # remove artifacts from other tests
#         exec(tmp._source, globals())
#         self.assertIn('NTColor', globals())
#         c = NTColor(10, 20, 30)
#         self.assertEqual((c.red, c.green, c.blue), (10, 20, 30))
#         self.assertEqual(NTColor.__fields__, ('red', 'green', 'blue'))
#         globals().pop('NTColor', None)          # clean-up after this test

def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(structclassTest))
    return suite
