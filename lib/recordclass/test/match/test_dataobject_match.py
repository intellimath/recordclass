import unittest

from recordclass import make_dataclass, make_arrayclass, dataobject

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
                    

def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(dataobjectmatchTest))
    return suite
