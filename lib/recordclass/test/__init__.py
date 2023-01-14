# {{LICENCE}}

from recordclass.test.test_recordclass import *
from recordclass.test.test_arrayclass import *
from recordclass.test.test_dataobject import *
from recordclass.test.test_litelist import *
from recordclass.test.test_litetuple import *

import sys
_PY36 = sys.version_info[:2] >= (3, 6)
_PY310 = sys.version_info[:2] >= (3, 10)

if _PY36:
    from recordclass.test.typing.test_recordclass import *
    from recordclass.test.typing.test_dataobject import *
    pass

if _PY310:
    from recordclass.test.match.test_dataobject_match import *

try:
    import sqlite3 as sql
except:
    sql = None
    
if sql is not None:
    from recordclass.test.test_sqlite import *
    
def test_all():
    import unittest
    unittest.main(verbosity=3)
