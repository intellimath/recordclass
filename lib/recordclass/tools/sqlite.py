from recordclass import make_dataclass

def make_row_factory(cls_factory, **kw):
    def row_factory(cursor, row, cls=[None]):
        rf = cls[0]
        if rf is None:
            fields = [col[0] for col in cursor.description]
            cls[0] = cls_factory("Row", fields, **kw)
            print(cls[0])
            return cls[0](*row)
        return rf(*row)
    return row_factory

def dataclass_row_factory(cls=None):
    if cls is None:
        return make_row_factory(make_dataclass, fast_new=True)
    else:
        def row_factory(cursor, row):
            return cls(*row)
        return row_factory
