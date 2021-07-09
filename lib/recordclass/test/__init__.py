# {{LICENCE}}

from recordclass.test.test_recordclass import *
from recordclass.test.test_arrayclass import *
from recordclass.test.test_dataobject import *
from recordclass.test.test_litelist import *
from recordclass.test.test_litetuple import *

import sys
_PY36 = sys.version_info[:2] >= (3, 6)

if _PY36:
    from recordclass.test.typing.test_recordclass import *
    from recordclass.test.typing.test_dataobject import *
    pass

def test_all():
    import unittest
    unittest.main(verbosity=3)
