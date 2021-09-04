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

from .utils import dataslot_offset, process_fields
from .utils import check_name, collect_info_from_bases

__all__ = 'make_dataclass', 'join_dataclasses', 'DataclassStorage'

def make_dataclass(typename, fields=None, defaults=None, bases=None, namespace=None, *,
                   use_dict=False, use_weakref=False, hashable=False,
                   sequence=False, mapping=False, iterable=False, readonly=False, api='',
                   module=None, fast_new=False, rename=False, gc=False, mapping_only=False):

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
    from ._dataobject import dataobject, astuple, asdict
    from .datatype import datatype
    import sys as _sys

    if api == 'namedtuple':
        invalid_names = ('_make', '_replace', '_asdict')
    elif api == 'dict':
        invalid_names = ('keys', 'values', 'items', 'get')
    else: 
        invalid_names = ()

    fields, annotations, defaults = process_fields(fields, defaults, rename, invalid_names)
    typename = check_name(typename)
    
    if namespace is None:
        ns = {}
    else:
        ns = namespace.copy()
        
    n_fields = len(fields)
    n_defaults = len(defaults) if defaults else 0

    if use_dict and '__dict__' not in fields:
        fields.append('__dict__')
    if use_weakref and '__weakref__' not in fields:
        fields.append('__weakref__')

    ns['__fields__'] = fields
    ns['__annotations__'] = annotations
    ns['__defaults__'] = defaults
    
    if api == 'namedtuple':
        sequence = True

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

        ns.update({ '_make': _make, 
                    '_replace': _replace, 
                    '_asdict': _asdict,
                  })
        
    elif api == 'dict':
        if readonly:
            raise TypeError('Immutable type can not support dict-like interface')

        iterable = True
        if not mapping_only:
            mapping = True
        
        def keys(self):
            return iter(self.__fields__)
        
        def values(self):
            return iter(self)
        
        def items(self):
            for key in self.__fields__:
                yield key, getattr(self, key)
                
        def update(self, d):
            return update(self, d)
        
        def get(self, key, default=None):
            if key in self.__fields__:
                return getattr(self, key)
            else:
                return default

        def __contains__(self, key):
            return (key in self.__fields__)
        
        ns.update({
            'keys': keys,
            'items': items,
            'values': values,
            'update': update,
            'get': get
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
                   gc=gc, fast_new=fast_new,
                   readonly=readonly, iterable=iterable,
                   mapping=mapping, sequence=sequence,
                   use_dict=use_dict, use_weakref=use_weakref,
                   hashable=hashable, mapping_only=mapping_only,
                   )

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
