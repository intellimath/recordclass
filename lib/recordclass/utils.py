# coding: utf-8
 
# The MIT License (MIT)

# Copyright (c) «2015-2019» «Shibzukhov Zaur, szport at gmail dot com»

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

### sizes

_t = ()
_t1 = (1,)
_o = object()
headgc_size = _sys.getsizeof(_t) - _t.__sizeof__()
ref_size = _sys.getsizeof(_t1) - _sys.getsizeof(_t)
pyobject_size = _o.__sizeof__()
pyvarobject_size = _t.__sizeof__()
pyssize = pyvarobject_size - pyobject_size
del _t, _t1, _o

#############

def number_of_dataslots(cls):
    basicsize = cls.__basicsize__
    if cls.__itemsize__:
        basesize = pyvarobject_size
    else:
        basesize = pyobject_size
    n = (cls.__basicsize__ - basesize) // ref_size
    if cls.__dictoffset__:
        n -= 1
    if cls.__weakrefoffset__:
        n -= 1
    return n

def dataslot_offset(cls, i):
    n_slots = number_of_dataslots(cls)
    if i >= n_slots:
        raise IndexError("invalid index of the slots")
    if cls.__itemsize__:
        basesize = pyvarobject_size
    else:
        basesize = pyobject_size
    return basesize + i*ref_size

def dataitem_offset(cls, i):
    tp_basicsize = cls.__basicsize__
    return basicsize + i*ref_size

def check_name(name):
    if not isinstance(name, str):
        raise TypeError('Type names and field names must be strings')
    if not _isidentifier(name):
        raise ValueError('Type names and field names must be valid '
                         'identifiers: %r' % name)
    if _iskeyword(name):
        raise ValueError('Type names and field names cannot be a '
                         'keyword: %r' % name)
    return name

def collect_info_from_bases(bases):
    fields = []
    defaults = {}
    annotations = {}
    use_dict = False
    for base in bases:
        fs = base.__dict__.get('__fields__', ())
        n = number_of_dataslots(base)
        if type(fs) is tuple and len(fs) == n:
            fields.extend(f for f in fs if f not in fields)
        else:
            raise TypeError("invalid fields in base class %r" % base)
            
        ds = base.__dict__.get('__defaults__', {})
        defaults.update(ds)                        

        ann = base.__dict__.get('__annotations__', {})
        annotations.update(ann)
        
    return fields, defaults, annotations
