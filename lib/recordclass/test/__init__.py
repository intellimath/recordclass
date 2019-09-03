# {{LICENCE}}

from recordclass.test.test_mutabletuple import *
from recordclass.test.test_recordclass import *
from recordclass.test.test_structclass import *
from recordclass.test.test_arrayclass import *
from recordclass.test.test_dataobject import *
from recordclass.test.test_litelist import *

import sys
_PY36 = sys.version_info[:2] >= (3, 6)

if _PY36:
    from recordclass.test.typing.test_recordclass import *
    from recordclass.test.typing.test_structclass import *
    from recordclass.test.typing.test_dataobject import *

def test_all():
    import unittest
    unittest.main(verbosity=2)
