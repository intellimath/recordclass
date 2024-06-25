# {{LICENCE}}

import sys
from recordclass.test.test_recordclass import *
from recordclass.test.test_arrayclass import *
from recordclass.test.test_dataobject import *
from recordclass.test.test_litelist import *
from recordclass.test.test_litetuple import *

from recordclass.test.typing.test_recordclass import *
from recordclass.test.typing.test_dataobject import *
from recordclass.test.typing.test_datastruct import *
pass

if sys.version_info >= (3, 10):
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
