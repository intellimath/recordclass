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

from collections import namedtuple, OrderedDict
from .utils import check_name
from keyword import iskeyword as _iskeyword

import sys as _sys

_intern = _sys.intern
if _sys.version_info[:2] >= (3, 6):
    from typing import _type_check
else:
    def _type_check(t, msg):
        if isinstance(t, (type, str)):
            return t
        else:
            raise TypeError('invalid type annotation', t)

def recordclass(typename, fields, 
                rename=False, defaults=None, readonly=False, hashable=False, gc=False,
                module=None):
    """Returns a new subclass of array with named fields.

    >>> Point = recordclass('Point', 'x y')
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessable by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d.x
    11
    >>> d.x = 33                        # assign new value
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)
    """
    
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
                
    if rename:
        seen = set()
        for index, name in enumerate(field_names):
            if (not name.isidentifier()
                or _iskeyword(name)
                or name.startswith('_')
                or name in seen):
                    field_names[index] = '_%d' % index
            seen.add(name)
                
    for name in [typename] + field_names:
        if type(name) != str:
            raise TypeError('Type names and field names must be strings')
        if not name.isidentifier():
            raise ValueError('Type names and field names must be valid '
                             'identifiers: %r' % name)
        if _iskeyword(name):
            raise ValueError('Type names and field names cannot be a '
                             'keyword: %r' % name)
    seen = set()
    for name in field_names:
        if name.startswith('_') and not rename:
            raise ValueError('Field names cannot start with an underscore: '
                             '%r' % name)
        if name in seen:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen.add(name)
        
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

    if readonly:
        def _replace(_self, **kwds):
            result = _self._make((kwds.pop(name) for name in field_names))
            if kwds:
                raise ValueError('Got unexpected field names: %r' % list(kwds))
            return result
    else:
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
        'sequence':True,
        'mapping':False,
        'iterable':True,
#         'use_dict':use_dict,
#         'use_weakref':use_weakref,
        'hashable':hashable,
        'gc':gc,
    }
    
    if readonly:
        options['hashable'] = True
        
    ns = {'_make': _make, '_replace': _replace, '_asdict': _asdict,
          '__doc__': typename+'('+ ', '.join(field_names) +')',
         '__module__':module}

    if defaults:
        for i in range(-n_defaults, 0):
            fname = field_names[i]
            val = defaults[i]
            ns[fname] = val

#     if use_dict and '__dict__' not in field_names:
#         field_names.append('__dict__')
#     if use_weakref and '__weakref__' not in field_names:
#         field_names.append('__weakref__')

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

