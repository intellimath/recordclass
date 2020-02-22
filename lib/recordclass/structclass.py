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

from keyword import iskeyword as _iskeyword
from collections import namedtuple, OrderedDict
from .utils import check_name

import sys as _sys
_PY3 = _sys.version_info[0] >= 3

if _PY3:
    _intern = _sys.intern
    def _isidentifier(s):
        return s.isidentifier()
    if _sys.version_info[1] >= 6:
        from typing import _type_check
    else:
        _type_check = None
else:
    from __builtin__ import intern as _intern
    import re as _re
    def _isidentifier(s):
        return _re.match(r'^[a-z_][a-z0-9_]*$', s, _re.I) is not None
    _type_check = None

def structclass(typename, fields=None, use_dict=False, use_weakref=False, hashable=True,
                   sequence=True, mapping=False, readonly=False,
                   defaults=None, module=None, gc=False):
    
    from ._dataobject import _clsconfig, _enable_gc
    from ._dataobject import dataobject
    from .datatype import datatype

    annotations = {}
    if isinstance(fields, str):
        field_names = fields.replace(',', ' ').split()
        field_names = [fn.strip() for fn in field_names]
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
        
    n_fields = len(field_names)
    typename = check_name(typename)

    if defaults is not None:
        n_fields = len(field_names)
        defaults = tuple(defaults)
        n_defaults = len(defaults)
        if n_defaults > n_fields:
            raise TypeError('Got more default values than fields')
    else:
        defaults = None
        
    def _make(_cls, iterable):
        ob = _cls(*iterable)
        if len(ob) != n_fields:
            raise TypeError('Expected %s arguments, got %s' % (n_fields, len(ob)))
        return ob
    
    _make.__doc__ = 'Make a new %s object from a sequence or iterable' % typename

    def _replace(_self, **kwds):
        for name, val in kwds.items():
            setattr(_self, name, val)
        return _self
    
    _replace.__doc__ = 'Return a new %s object replacing specified fields with new values' % typename
    
    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values.'
        return OrderedDict(zip(self.__fields__, self))
        
    for method in (_make, _replace, _asdict,):
        method.__qualname__ = typename + "." + method.__name__        
        
    _make = classmethod(_make)        

    options = {
        'readonly':readonly,
        'defaults':defaults,
        'argsonly':False,
        'sequence':sequence,
        'mapping':mapping,
#         'iterable':sequence,
        'use_dict':use_dict,
        'use_weakref':use_weakref,
        'readonly':readonly,
        'hashable':hashable,
        'gc':gc,
    }
        
    ns = {'_make': _make, '_replace': _replace, '_asdict': _asdict,
          '__doc__': typename+'('+ ', '.join(field_names) +')',
         '__module__':module}

    if defaults:
        for i in range(-n_defaults, 0):
            fname = field_names[i]
            val = defaults[i]
            ns[fname] = val

    if use_dict and '__dict__' not in field_names:
        field_names.append('__dict__')
    if use_weakref and '__weakref__' not in field_names:
        field_names.append('__weakref__')

    ns['__options__'] = options
    ns['__fields__'] = field_names
    if annotations:
        ns['__annotations__'] = annotations

    bases = (dataobject,)

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

def join_classes(name, classes, readonly=False, use_dict=False, gc=False, 
                 use_weakref=False, hashable=True, sequence=True, module=None):
    
    from ._dataobject import dataobject, datatuple
    
    if not all(issubclass(cls, dataobject) for cls in classes):
        raise TypeError('All arguments should be child of dataobject')
    for cls in classes:
        if isinstance(cls, datatuple):
            raise TypeError('The class', cls, 'should not be a subclass of datatuple')
    if not all(hasattr(cls, '__fields__') for cls in classes):
        raise TypeError('Some of the base classes has not __fields__')

    _attrs = []
    for cls in classes:
        for a in cls.__fields__:
            if a in _attrs:
                raise AttributeError('Duplicate attribute in the base classes')
            _attrs.append(a)

    return structclass(name, _attrs, 
                       readonly=readonly, use_dict=use_dict, gc=gc, use_weakref=use_weakref, 
                       hashable=False, sequence=True, module=module)
