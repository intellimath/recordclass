# coding: utf-8
 
# The MIT License (MIT)

# Copyright (c) «2015-2020» «Shibzukhov Zaur, szport at gmail dot com»

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

from .utils import dataslot_offset
from .utils import check_name, collect_info_from_bases

import sys as _sys
_PY3 = _sys.version_info[0] >= 3
_PY36 = _PY3 and _sys.version_info[1] >= 6

from keyword import iskeyword as _iskeyword

if _PY3:
    _intern = _sys.intern
    def _isidentifier(s):
        return s.isidentifier()
    if _PY36:
        from typing import _type_check
    else:
        def _type_check(t, msg):
            if isinstance(t, (type, str)):
                return t
            else:
                raise TypeError('invalid type annotation', t)    
else:
    from __builtin__ import intern as _intern
    import re as _re
    def _isidentifier(s):
        return _re.match(r'^[a-z_][a-z0-9_]*$', s, _re.I) is not None
    def _type_check(t, msg):
        return t

def make_dataclass(typename, fields=None, bases=None, namespace=None, 
                   varsize=False,  use_dict=False, use_weakref=False, hashable=True,
                   sequence=False, mapping=False, iterable=False, readonly=False,
                   defaults=None, module=None, argsonly=False, gc=False):
    
    from ._dataobject import _clsconfig, _enable_gc
    from ._dataobject import dataobject, datatuple
    from .datatype import datatype

    annotations = {}
    if isinstance(fields, str):
        fields = fields.replace(',', ' ').split()
        fields = [fn.strip() for fn in fields]
    else:
        msg = "make_dataclass('Name', [(f0, t0), (f1, t1), ...]); each t must be a type"
        field_names = []
        if isinstance(fields, dict):
            for fn, tp in fields.items():
                tp = _type_check(tp, msg)
                check_name(fn)
                fn = _intern(fn)
                annotations[fn] = tp
                field_names.append(fn)
        else:
            for fn in fields:
                if type(fn) is tuple:
                    fn, tp = fn
                    tp = _type_check(tp, msg)
                    annotations[fn] = tp
                check_name(fn)
                fn = _intern(fn)
                field_names.append(fn)
        fields = field_names
    typename = check_name(typename)

    if defaults is not None:
        n_fields = len(fields)
        defaults = tuple(defaults)
        n_defaults = len(defaults)
        if n_defaults > n_fields:
            raise TypeError('Got more default values than fields')
    else:
        defaults = None

    options = {
        'readonly':readonly,
        'defaults':defaults,
        'argsonly':argsonly,
        'sequence':sequence,
        'mapping':mapping,
        'iterable':iterable,
        'use_dict':use_dict,
        'use_weakref':use_weakref,
        'readonly':readonly,
        'hashable':hashable,
        'gc':gc,
    }

    if namespace is None:
        ns = {}
    else:
        ns = namespace.copy()

    if defaults:
        for i in range(-n_defaults, 0):
            fname = fields[i]
            val = defaults[i]
            ns[fname] = val

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
        if varsize:
            if not isinstance(base0, datatuple):
                raise TypeError("First base class should be subclass of datatuple")
        else:
            if not isinstance(base0, dataobject):
                raise TypeError("First base class should be subclass of dataobject")
    else:
        if varsize:
            bases = (datatuple,)
        else:
            bases = (dataobject,)
        
    if varsize:
        _sequence = True
    else:
        _sequence = sequence

        
    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
        
    ns['__module__'] = module

    cls = datatype(typename, bases, ns)

    if gc:
        _enable_gc(cls)

    return cls

make_class = make_dataclass

def asdict(ob):
    _getattr = getattr
    return {fn:_getattr(ob, fn) for fn in ob.__class__.__fields__}

class DataclassStorage:
    #
    def __init__(self):
        self._storage = {}
    #
    def make_dataclass(self, name, fields):
        fields = tuple(fields)
        key = (name, fields)
        cls = self._storage.get(key, None)
        if cls is None:
            cls = make_dataclass(name, fields)
            self._storage[key] = cls
        return cls
    make_class = make_dataclass
