"""Unit tests for recordclass.py."""
import unittest, doctest, operator
from recordclass import structclass

try:
    from test import support
except:
    from test import test_support as support

import pickle
import typing
from recordclass import StructClass, recordobject

class CoolEmployee(StructClass):
    name: str
    cool: int

class CoolEmployeeWithDefault(StructClass):
    name: str
    cool: int = 0

class XMeth(StructClass):
    x: int
    def double(self):
        return 2 * self.x

class XRepr(StructClass):
    x: int
    y: int = 1
    def __str__(self):
        return f'{self.x} -> {self.y}'
    def __add__(self, other):
        return 0

class H(StructClass):
    x: int
    y: int
    __options__ = {'hashable': True}

class HR(StructClass):
    x: int
    y: int
    __options__ = {'readonly': True}
    
class StructClassTypingTest(unittest.TestCase):
    def test_typing(self):
        class A(StructClass):
            a: int
            b: str
            c: typing.List[int]

        tmp = A(a=1, b='1', c=[1, 2, 3])
        self.assertEqual(repr(tmp), "A(a=1, b='1', c=[1, 2, 3])")
        self.assertEqual(A.__annotations__, {'a': int, 'b': str, 'c': typing.List[int]})

    def test_recordclass_basics(self):
        Emp = StructClass('Emp', [('name', str), ('id', int)])
        #self.assertIsSubclass(Emp, recordobject)
        joe = Emp('Joe', 42)
        jim = Emp(name='Jim', id=1)
        self.assertIsInstance(joe, Emp)
        self.assertIsInstance(joe, recordobject)
        self.assertEqual(joe.name, 'Joe')
        self.assertEqual(joe.id, 42)
        self.assertEqual(jim.name, 'Jim')
        self.assertEqual(jim.id, 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__fields__, ('name', 'id'))
        self.assertEqual(Emp.__annotations__,
                         dict([('name', str), ('id', int)]))

    # def test_namedtuple_pyversion(self):
    #     if sys.version_info[:2] < (3, 6):
    #         with self.assertRaises(TypeError):
    #             StructClass('Name', one=int, other=str)
    #         with self.assertRaises(TypeError):
    #             class NotYet(NamedTuple):
    #                 whatever = 0

    #@skipUnless(PY36, 'Python 3.6 required')
    def test_annotation_usage(self):
        tim = CoolEmployee('Tim', 9000)
        self.assertIsInstance(tim, CoolEmployee)
        self.assertIsInstance(tim, recordobject)
        self.assertEqual(tim.name, 'Tim')
        self.assertEqual(tim.cool, 9000)
        self.assertEqual(CoolEmployee.__name__, 'CoolEmployee')
        self.assertEqual(CoolEmployee.__fields__, ('name', 'cool'))
        self.assertEqual(CoolEmployee.__annotations__,
                         dict(name=str, cool=int))

    #@skipUnless(PY36, 'Python 3.6 required')
    def test_annotation_usage_with_default(self):
        jelle = CoolEmployeeWithDefault('Jelle')
        self.assertIsInstance(jelle, CoolEmployeeWithDefault)
        self.assertIsInstance(jelle, recordobject)
        self.assertEqual(jelle.name, 'Jelle')
        self.assertEqual(jelle.cool, 0)
        cooler_employee = CoolEmployeeWithDefault('Sjoerd', 1)
        self.assertEqual(cooler_employee.cool, 1)

        self.assertEqual(CoolEmployeeWithDefault.__name__, 'CoolEmployeeWithDefault')
        self.assertEqual(CoolEmployeeWithDefault.__fields__, ('name', 'cool'))

        with self.assertRaises(TypeError):
            exec("""
class NonDefaultAfterDefault(StructClass):
    x: int = 3
    y: int
""")

    #@skipUnless(PY36, 'Python 3.6 required')
    def test_annotation_usage_with_methods(self):
        self.assertEqual(XMeth(1).double(), 2)
        self.assertEqual(XMeth(42).x, 42)
        self.assertEqual(str(XRepr(42)), '42 -> 1')
        self.assertEqual(XRepr(1, 2) + XRepr(3), 0)

        with self.assertRaises(AttributeError):
            exec("""
class XMethBad(StructClass):
    x: int
    def __fields__(self):
        return 'no chance for this'
""")

        with self.assertRaises(AttributeError):
            exec("""
class XMethBad2(StructClass):
    x: int
    def _source(self):
        return 'no chance for this as well'
""")

    #@skipUnless(PY36, 'Python 3.6 required')
    def test_recordclass_keyword_usage(self):
        LocalEmployee = StructClass("LocalEmployee", name=str, age=int)
        nick = LocalEmployee('Nick', 25)
        self.assertIsInstance(nick, recordobject)
        self.assertEqual(nick.name, 'Nick')
        self.assertEqual(LocalEmployee.__name__, 'LocalEmployee')
        self.assertEqual(LocalEmployee.__fields__, ('name', 'age'))
        self.assertEqual(LocalEmployee.__annotations__, dict(name=str, age=int))
        with self.assertRaises(TypeError):
            StructClass('Name', [('x', int)], y=str)
        with self.assertRaises(TypeError):
            StructClass('Name', x=1, y='a')
            
    def test_hash(self):
        a = HR(1, 2)
        self.assertEqual(hash(a), hash(tuple(a)))
        b = H(1, 2)
        hash_b = hash(b)
        self.assertEqual(hash_b, hash(tuple(b)))
        b.x = -1
        self.assertNotEqual(hash(b), hash_b)            

    def test_pickle(self):
        global Emp  # pickle wants to reference the class by name
        Emp = StructClass('Emp', [('name', str), ('id', int)])
        jane = Emp('jane', 37)
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(jane, proto)
            jane2 = pickle.loads(z)
            self.assertEqual(jane2, jane)

    def test_pickle2(self):
        global Emp2
        class Emp2(StructClass):
            name:str
            id:int
        
        jane = Emp2('jane', 37)
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(jane, proto)
            jane2 = pickle.loads(z)
            self.assertEqual(jane2, jane)

    def test_pickle3(self):
        jane = CoolEmployee('jane', 37)
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(jane, proto)
            jane2 = pickle.loads(z)
            self.assertEqual(jane2, jane)

def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StructClassTypingTest))
    return suite
