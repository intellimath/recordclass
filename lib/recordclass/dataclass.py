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

__all__ = 'make_dataclass', 'join_dataclasses'

import sys as _sys
_PY36 = _sys.version_info[:2] >= (3, 6)

_intern = _sys.intern
if _PY36:
    from typing import _type_check
else:
    def _type_check(t, msg):
        if isinstance(t, (type, str)):
            return t
        else:
            raise TypeError('invalid type annotation', t)

def make_dataclass(typename, fields=None, defaults=None, bases=None, namespace=None,
                   use_dict=False, use_weakref=False, hashable=True,
                   sequence=False, mapping=False, iterable=False, readonly=False,
                   module=None, fast_new=False, rename=False, invalid_names=(), gc=False):

    from ._dataobject import dataobject
    from .datatype import datatype

    fields, annotations, defaults = process_fields(fields, defaults, rename, invalid_names)
    typename = check_name(typename)

    options = {
        'readonly':readonly,
        'defaults':defaults,
        'sequence':sequence,
        'mapping':mapping,
        'iterable':iterable,
        'use_dict':use_dict,
        'use_weakref':use_weakref,
        'readonly':readonly,
        'hashable':hashable,
        'fast_new':fast_new,
        'gc':gc,
    }

    if namespace is None:
        ns = {}
    else:
        ns = namespace.copy()
        
    n_fields = len(fields)
    n_defaults = len(defaults) if defaults else 0

    if defaults:
        for i in range(-n_defaults, 0):
            fname = fields[i]
            ns[fname] = defaults[i]

    if use_dict and '__dict__' not in fields:
        fields.append('__dict__')
    if use_weakref and '__weakref__' not in fields:
        fields.append('__weakref__')

    ns['__options__'] = options
    ns['__fields__'] = fields
    if annotations:
        ns['__annotations__'] = annotations

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

    cls = datatype(typename, bases, ns)

    return cls

make_class = make_dataclass

def asdict(ob):
    _getattr = getattr
    return {fn:_getattr(ob, fn) for fn in ob.__class__.__fields__}

def astuple(ob):
    from ._dataobject import _astuple
    return _astuple(ob)

# class DataclassStorage:
#     #
#     def __init__(self):
#         self._storage = {}
#     #
#     def clear_storage(self):
#         self._storage.clear()
#     #
#     def make_dataclass(self, name, fields):
#         if type(fields) is str:
#             fields = fields.replace(',', ' ').split()
#             fields = [fn.strip() for fn in fields]
#         fields = tuple(fields)
#         key = (name, fields)
#         cls = self._storage.get(key, None)
#         if cls is None:
#             cls = make_dataclass(name, fields)
#             self._storage[key] = cls
#         return cls
#     make_class = make_dataclass

def join_dataclasses(name, classes, readonly=False, use_dict=False, gc=False,
                 use_weakref=False, hashable=True, sequence=False, fast_new=False, iterable=False, module=None):

    from ._dataobject import dataobject

    if not all(issubclass(cls, dataobject) for cls in classes):
        raise TypeError('All arguments should be child of dataobject')
    if not all(hasattr(cls, '__fields__') for cls in classes):
        raise TypeError('Some of the base classes has not __fields__')

    _attrs = []
    for cls in classes:
        for a in cls.__fields__:
            if a in _attrs:
                raise AttributeError('Duplicate attribute %s in the base classes' % a)
            _attrs.append(a)

    return make_dataclass(name, _attrs,
                          readonly=readonly, use_dict=use_dict, gc=gc, use_weakref=use_weakref,
                          hashable=hashable, sequence=sequence, iterable=iterable, module=module)

