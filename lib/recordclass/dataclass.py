# coding: utf-8

# The MIT License (MIT)

# Copyright (c) «2017-2023» «Shibzukhov Zaur, szport at gmail dot com»

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

from .utils import process_fields
from .utils import check_name, collect_info_from_bases
from ._dataobject import dataobject

__all__ = 'make_dataclass', 'join_dataclasses', 'DataclassStorage'

def make_dataclass(typename, fields, defaults=None, *, bases=None, namespace=None,
                   use_dict=False, use_weakref=False, hashable=False,
                   sequence=False, mapping=False, iterable=False, readonly=False, invalid_names=(),
                   deep_dealloc=False, module=None, fast_new=True, rename=False, gc=False, 
                   immutable_type=False, copy_default=False):

    """Returns a new class with named fields and small memory footprint.

    >>> from recordclass import make_dataclass, asdict
    >>> Point = make_dataclass('Point', 'x y')
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(1, 2)                 # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    3
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (1, 2)
    >>> p.x + p.y                       # fields also accessable by name
    3
    >>> d = asdict()                    # convert to a dictionary
    >>> d['y'] = 3                         # assign new value
    >>> Point(**d)                      # convert from a dictionary
    Point(x=1, y=-1)
    """
    from ._dataobject import dataobject
    from .datatype import datatype
    import sys as _sys

    fields, annotations, defaults = process_fields(fields, defaults, rename, invalid_names)
    typename = check_name(typename)
    
    if namespace is None:
        ns = {}
    else:
        ns = namespace.copy()

    n_fields = len(fields)
    n_defaults = len(defaults) if defaults else 0

    ns['__fields__'] = fields
    ns['__annotations__'] = annotations
    ns['__defaults__'] = defaults

    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass

    ns['__module__'] = module

    cls = datatype(typename, bases, ns, 
                   readonly=readonly, iterable=iterable,
                   mapping=mapping, sequence=sequence,
                   use_dict=use_dict, use_weakref=use_weakref,
                   gc=gc, fast_new=fast_new,
                   hashable=hashable, immutable_type=immutable_type, 
                   copy_default=copy_default)

    return cls

make_class = make_dataclass

class DataclassStorage:
    #
    def __init__(self):
        self._storage = {}
    #
    def clear_storage(self):
        self._storage.clear()
    #
    def make_dataclass(self, name, fields, defaults=None, **kw):
        if type(fields) is str:
            fields = fields.replace(',', ' ').split()
            fields = ' '.join(fn.strip() for fn in fields)
        else:
            fields = ' '.join(fields)
        key = (name, fields)
        cls = self._storage.get(key, None)
        if cls is None:
            cls = make_dataclass(name, fields, defaults, **kw)
            self._storage[key] = cls
        return cls
    make_class = make_dataclass

def join_dataclasses(name, classes, *, readonly=False, use_dict=False, gc=False,
                 use_weakref=False, hashable=True, sequence=False, fast_new=False, iterable=True, module=None):

    from ._dataobject import dataobject

    if not all(issubclass(cls, dataobject) for cls in classes):
        raise TypeError('All arguments should be children of dataobject')
    if not all(hasattr(cls, '__fields__') for cls in classes):
        raise TypeError('Some of the base classes has not __fields__')

    _attrs = []
    for cls in classes:
        for a in cls.__fields__:
            if a in _attrs:
                raise AttributeError(f'Duplicate attribute %s in the base classes {a}')
            _attrs.append(a)

    return make_dataclass(name, _attrs,
                          readonly=readonly, use_dict=use_dict, gc=gc, use_weakref=use_weakref,
                          hashable=hashable, sequence=sequence, iterable=iterable, module=module)
    