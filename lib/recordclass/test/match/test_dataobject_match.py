import unittest

from recordclass import make_dataclass, make_arrayclass, dataobject, MATCH

class dataobjectmatchTest(unittest.TestCase):

    def test_match_1(self):
        Point = make_dataclass("Point", "x y")
        p = Point(1,2)
        x = Point(1,2)
        match x:
            case Point(1,2):
                pass
            case _:
                raise TypeError(f"{p} does not match {x}")

    def test_match_2(self):
        Point = make_dataclass("Point", "x y")
        x = Point(1,2)
        with self.assertRaises(TypeError):
            match x:
                case Point(1, 3):
                    pass
                case _:
                    raise TypeError(f"(1, 2) does not match {x}")

    def test_match_3(self):
        Point = make_dataclass("Point", "x y")
        Point2 = make_dataclass("Point2", "x y")
        x = Point(1,2)
        p = Point2(1, 2)
        with self.assertRaises(TypeError):
            match x:
                case Point2(1, 2):
                    pass
                case _:
                    raise TypeError(f"{x} does not match {p}")

    def test_match_3(self):
        Point = make_dataclass("Point", "x y")
        Point2 = make_dataclass("Point2", "x y")
        x = Point(1,2)
        p = Point2(1, 2)
        with self.assertRaises(TypeError):
            match x:
                case Point2(1, 2):
                    pass
                case _:
                    raise TypeError(f"{x} does not match {p}")

    def test_match_4(self):
        Point = make_dataclass("Point", "x y z", match=('x','y'))
        Point2 = make_dataclass("Point2", "x y z", match=('x','y'))
        x = Point(1,2)
        p = Point2(1, 2)
        with self.assertRaises(TypeError):
            match x:
                case Point2(1, 2, 3):
                    pass
                case _:
                    raise TypeError(f"{x} does not match {p}")

    def test_match_5(self):
        Point = make_dataclass("Point", "x y * z")
        Point2 = make_dataclass("Point2", "x y * z")
        x = Point(1,2)
        p = Point2(1, 2)
        with self.assertRaises(TypeError):
            match x:
                case Point2(1, 2, 3):
                    pass
                case _:
                    raise TypeError(f"{x} does not match {p}")

    def test_match_6(self):
        class Point(dataobject):
            x: int
            y: int
            _: MATCH
            z: int

        class Point2(dataobject):
            x: int
            y: int
            _: MATCH
            z: int

        x = Point(1,2)
        p = Point2(1, 2)
        with self.assertRaises(TypeError):
            match x:
                case Point2(1, 2, 3):
                    pass
                case _:
                    raise TypeError(f"{x} does not match {p}")

def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(dataobjectmatchTest))
    return suite
