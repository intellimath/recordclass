# coding: utf-8

# The MIT License (MIT)

# Copyright (c) «2021-2023» «Shibzukhov Zaur, szport at gmail dot com»

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

__all__ = 'make_dictclass', 'DictclassStorage'

def make_dictclass(typename, keys, defaults=None, *, bases=None, namespace=None,
                   readonly=False, module=None, fast_new=True):

    """Returns a new dict-like class with keys and small memory footprint.

    >>> from recordclass import make_dataclass, asdict
    >>> Point = make_dictclass('Point', 'x y')
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(1, 2)                 # instantiate with positional args or keywords
    """
    from ._dataobject import dataobject, astuple, asdict
    from .datatype import datatype
    import sys as _sys

    keys, annotations, defaults = process_fields(keys, defaults, False, ())
    typename = check_name(typename)
    
    if namespace is None:
        ns = {}
    else:
        ns = namespace.copy()
        
    n_keys = len(keys)
    n_defaults = len(defaults) if defaults else 0

#     if use_dict and '__dict__' not in keys:
#         keys.append('__dict__')
#     if use_weakref and '__weakref__' not in keys:
#         keys.append('__weakref__')

    ns['__fields__'] = keys
    ns['__annotations__'] = annotations
    ns['__defaults__'] = defaults
    
    if readonly:
        raise TypeError('Immutable type can not support dict-like interface')

    def keys(self):
        return iter(self.__fields__)

    def values(self):
        return iter(self)

    def items(self):
        for key in self.__fields__:
            yield key, self[key]

    def update(self, d):
        return update(self, d)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        return (key in self.__fields__)

    ns.update({
        'keys': keys, 
        'items': items, 
        'values': values, 
        'get': get,
        'update': update,
    })

    if bases:
        base0 = bases[0]
        if not isinstance(base0, dataobject):
            raise TypeError("First base class should be subclass of dataobject")
    else:
        bases = (dataobject,)

    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass

    ns['__module__'] = module

    cls = datatype(typename, bases, ns, 
                   gc=False, fast_new=fast_new,
                   readonly=readonly, iterable=True,
                   mapping=True, sequence=False,
                   use_dict=False, use_weakref=False,
                   hashable=False)

    return cls

class DictclassStorage:
    #
    def __init__(self):
        self._storage = {}
    #
    def clear_storage(self):
        self._storage.clear()
    #
    def make_dictclass(self, name, keys, defaults=None, **kw):
        if type(keys) is str:
            keys = keys.replace(',', ' ').split()
            keys = ' '.join(fn.strip() for fn in keys)
        else:
            keys = ' '.join(keys)
        key = (name, keys)
        cls = self._storage.get(key, None)
        if cls is None:
            cls = make_datadict(name, keys, defaults, **kw)
            self._storage[key] = cls
        return cls
