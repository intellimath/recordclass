from recordclass import make_dataclass

def make_row_factory(name, fields):
    cls = make_dataclass(name, fields)
    def row_factory(cur, row, cls=cls):
        return cls(*row)
    return row_factory