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

import sys as _sys
_PY36 = _sys.version_info[:2] >= (3, 6)

from keyword import iskeyword

_intern = _sys.intern
if _PY36:
    from typing import _type_check
else:
    def _type_check(t, msg):
        if isinstance(t, (type, str)):
            return t
        else:
            raise TypeError('invalid type annotation', t)    

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
del _sys

#############

def number_of_dataslots(cls):
    basesize = pyobject_size
    n = (cls.__basicsize__ - basesize) // ref_size
    if cls.__dictoffset__:
        n -= 1
    if cls.__weakrefoffset__:
        n -= 1
    return n

def dataslot_offset(i, n_slots):
    if i >= n_slots:
        raise IndexError("invalid index of the slots")
    basesize = pyobject_size
    return basesize + i*ref_size

def dataitem_offset(cls, i):
    tp_basicsize = cls.__basicsize__
    return tp_basicsize + i*ref_size

def process_fields(fields, defaults, rename, invalid_names):
    annotations = {}
    msg = "in iterable (f0, t0), (f1, t1), ... each t must be a type"
    if isinstance(fields, str):
        fields = fields.replace(',', ' ').split()
        fields = [fn.strip() for fn in fields]

    field_names = []
    if isinstance(fields, dict):
        for i, fn in enumerate(fields):
            tp = fields[fn]
            tp = _type_check(tp, msg)
            check_name(fn, i, rename, invalid_names)
            fn = _intern(fn)
            annotations[fn] = tp
            field_names.append(fn)
    else:
        for i, fn in enumerate(fields):
            if type(fn) is tuple:
                fn, tp = fn
                tp = _type_check(tp, msg)
                annotations[fn] = tp
            check_name(fn, i, rename, invalid_names)
            fn = _intern(fn)
            field_names.append(fn)
    fields = field_names
        
    seen = set()
    for fn in fields:
        if fn in seen:
            raise ValueError('duplicate name ' + fn)
        seen.add(fn)

    if defaults is None:
        defaults = {}
    n_defaults = len(defaults)
    n_fields = len(fields)
    if n_defaults > n_fields:
        raise TypeError('Got more default values than fields')

    if isinstance(defaults, (tuple,list)) and n_defaults > 0:
        defaults = {fields[i]:defaults[i] for i in range(-n_defaults,0)}
        
    return fields, annotations, defaults

def check_name(name, i=0, rename=False, invalid_names=()):
    if not isinstance(name, str):
        raise TypeError('Type names and field names must be strings')

    if name.startswith('__') and name.endswith('__'):
        return name

    if rename:
        if not name.isidentifier() or iskeyword(name) or (name in invalid_names):
            name = "_%s" % (i+1)
    else:
        if name in invalid_names:
            raise ValueError('Name %s is invalid' % name)
        if not name.isidentifier():
            raise ValueError('Name must be valid identifiers: %r' % name)
        if iskeyword(name):
            raise ValueError('Name cannot be a keyword: %r' % name)
    
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
            for f in fs:
                if f in fields:
                    raise TypeError('field %s is already defined in the %s' % (f, base))
                else:
                    fields.append(f)
#             fields.extend(f for f in fs if f not in fields)
        else:
            raise TypeError("invalid fields in base class %r" % base)
            
        ds = base.__dict__.get('__defaults__', {})
        defaults.update(ds)                        

        ann = base.__dict__.get('__annotations__', {})
        annotations.update(ann)
        
    return fields, defaults, annotations
