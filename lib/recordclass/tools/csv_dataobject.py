from csv import writer, reader

__all__ = 'GeneralReader', 'GeneralWriter'

_type_conv = {
    'str':str,
    'int':int,
    'float':float
}

class GeneralReader:
    def __init__(self, f, fieldnames=None, dialect="excel", fieldtypes=None, *args, **kwds):
        self._fieldnames = fieldnames   # list of keys for the dict
        self.restkey = restkey          # key to catch long rows
        self.restval = restval          # default value for short rows
        self.reader = reader(f, dialect, *args, **kwds)
        self.dialect = dialect
        self.factory = None
        self.row_factory = None
        self.field_conv = None
        if fieldtypes:
            conv_dict = {}
            for name, ftype in fieldtypes:
                conv_dict[name] = _type_conv[ftype]
            self.field_conv = conv_dict

    def __iter__(self):
        return self

    @property
    def fieldnames(self):
        if self._fieldnames is None:
            try:
                self._fieldnames = next(self.reader)
            except StopIteration:
                pass
        self.line_num = self.reader.line_num
        return self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value
        
    @property
    def line_num(self):
        return self.reader.line_num
    
    def __default_row_factory(self, *row):
        return row

    def __next__(self):
        row = next(self.reader)
        while row == []:
            row = next(self.reader)
        
        if self.row_factory is None:
            if self.fieldnames is None:
                # Remove trailing spaces.
                fieldnames = (f.strip() for f in row)
                # Remove spaces.
                fieldnames = (f.replace(' ', '_') for f in fieldnames)

                for fname in fieldnames:
                    if not fname.isidentifier():
                        raise TypeError(f"field name {fname} should be an identifiers")

                self._fieldnames = tuple(fieldnames)

            if self.factory is None:
                self.row_factory = self.__default_row_factory
            else:                   
                self.row_factory = self.factory(self._fieldnames)

        row = self.row_factory(*row)
        if self.field_conv:
            for name, func in self.field_conv.items():
                v = getattr(row, name)
                if type(v) is str:
                    setattr(row, name, func(v))

class GeneralWriter:
    def __init__(self, f, fieldnames, dialect="excel", *args, **kwds):
        self.fieldnames = fieldnames
        self.restval = restval
        self.writer = writer(f, dialect, *args, **kwds)

    def writeheader(self):
        return self.writerow(self.fieldnames)

    def writerow(self, row):
        return self.writer.writerow(list(row))

    def writerows(self, rows):
        return self.writer.writerows(map(list, rows))
