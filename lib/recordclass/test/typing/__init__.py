# {{LICENCE}}

from recordclass.test.typing.test_recordclass import *
from recordclass.test.typing.test_structclass import *
from recordclass.test.typing.test_dataobject import *

def test_all():
    import unittest
    unittest.main(verbosity=2)
