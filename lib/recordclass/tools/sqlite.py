# from recordclass import make_dataclass

def make_row_factory(cls):
    def row_factory(cur, row, cls=cls):
        return cls(*row)
    return row_factory
