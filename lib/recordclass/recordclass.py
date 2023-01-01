# coding: utf-8
 
# The MIT License (MIT)

# Copyright (c) «2015-2021» «Shibzukhov Zaur, szport at gmail dot com»

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software - recordclass library - and associated documentation files 
# (the "Software"), to deal in the Software without restriction, including 
# without limitation the rights to use, copy, modify, merge, publish, distribute, 
# sublicense, and/or sell copies of the Software, and to permit persons to whom 
# the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__all__ = 'recordclass', 'RecordclassStorage'

from .datatype import datatype
from ._dataobject import dataobject

def _add_namedtuple_api(typename, readonly):
    from ._dataobject import astuple, asdict

    def _make(_cls, iterable):
        ob = _cls(*iterable)
        return ob

    _make.__doc__ = f'Make a new {typename} object from a sequence or iterable'

    if readonly:
        def _replace(_self, **kwds):
            result = _self._make(map(kwds.pop, _self.__fields__, _self))
            if kwds:
                kwnames = tuple(kwds)
                raise AttributeError(f'Got unexpected field names: {kwnames}')
            return result
    else:
        def _replace(_self, **kwds):
            for name, val in kwds.items():
                setattr(_self, name, val)
            return _self

    _replace.__doc__ = f'Return a new {typename} object replacing specified fields with new values'

    def _asdict(self):
        'Return a new dict which maps field names to their values.'
        return asdict(self)

    for method in (_make, _replace, _asdict,):
        method.__qualname__ = typename + "." + method.__name__        

    _make = classmethod(_make)

    ns = { '_make': _make, 
           '_replace': _replace, 
           '_asdict': _asdict
         }
    return ns

def recordclass(typename, fields, defaults=None, *,
                rename=False, readonly=False, hashable=False, gc=False,
                use_dict=False, use_weakref=False, fast_new=True, mapping=False, module=None):
    """Returns a new class with named fields, small memory footprint and namedtuple-lie API.

    >>> Point = recordclass('Point', 'x y')
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(1,2)                  # instantiate with positional args or keywords
    >>> print(p)
    Point(x=1, y=2)
    >>> p[0] + p[1]                     # indexable like a plain tuple
    3
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (1, 2)
    >>> p.x + p.y                       # fields also accessable by name
    3
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['y'] =-1                      # assign new value
    >>> Point(**d)                      # convert from a dictionary
    Point(x=1, y=-1)
    """
    from .dataclass import make_dataclass
    import sys as _sys
    
    ns = _add_namedtuple_api(typename, readonly)
    if readonly:
        hashable = True
    
    if module is None:
        try:
            _module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
    else:
        _module = module

    invalid_names = ('_make', '_replace', '_asdict')

    return make_dataclass(typename, fields, defaults=defaults, namespace=ns,
                use_dict=use_dict, use_weakref=use_weakref, hashable=hashable, 
                sequence=True, mapping=mapping, iterable=True, rename=rename, 
                readonly=readonly, module=_module, invalid_names = invalid_names,
                fast_new=fast_new, gc=False)

class RecordclassStorage:
    #
    def __init__(self):
        self._storage = {}
    #
    def clear_storage(self):
        self._storage.clear()
    #
    def recordclass(self, name, fields, defaults=None, **kw):
        if type(fields) is str:
            fields = fields.replace(',', ' ').split()
            fields = ' '.join(fn.strip() for fn in fields)
        else:
            fields = ' '.join(fields)
        key = (name, fields)
        cls = self._storage.get(key, None)
        if cls is None:
            cls = recordclass(name, fields, defaults, **kw)
            self._storage[key] = cls
        return cls

