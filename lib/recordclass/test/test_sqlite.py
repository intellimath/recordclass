import unittest

import sqlite3 as sql
from recordclass.tools.sqlite import make_row_factory

class DataobjectSqliteTest(unittest.TestCase):

    def test_row_factory(self):
        con = sql.connect(":memory:")
        cur = con.execute("SELECT 'Earth' AS name, 6378 AS radius")
        cur.row_factory = make_row_factory("Planet", "name radius")
        row = cur.fetchone()
        # print(type(row), row)
        self.assertEqual(row.name, 'Earth')
        self.assertEqual(row.radius, 6378)
        self.assertEqual(type(row).__name__, 'Planet')
        
        
def main():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DataobjectSqliteTest))
    return suite
        