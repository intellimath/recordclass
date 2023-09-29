# coding: utf-8
 
# The MIT License (MIT)

# Copyright (c) «2015-2023» «Shibzukhov Zaur, szport at gmail dot com»

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
from recordclass import dataobject
from .datatype import Field

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

if 'PyPy' in _sys.version:
    is_pypy = True
else:
    is_pypy = False

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

# def get_option(options, name, default=False):
#     if name in options:
#         val = options[name]
#         if not val:
#             del options[name]
#     else:
#         val = default
#         if val:
#             options[name] = val
#     return val

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

def check_name(name, rename=False, i=0, invalid_names=()):
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

def number_of_dataitems(cls):
    fields = cls.__fields__
    if type(fields) is int:
        return fields
    else:
        return len(fields)

def collect_info_from_bases(bases, fields, fields_dict, options):
    from ._dataobject import _is_readonly_member
    _fields = []
    use_dict = options.get('use_dict', False)
    use_weakref = options.get('use_weakref', False)
    copy_default = options.get('copy_default', False)
    gc = options.get('gc', False)
    iterable = options.get('iterable', False)
    # readonly = True
    # hashable = None
    for base in bases:
        if base is dataobject:
            continue
        elif issubclass(base, dataobject):
            use_dict = use_dict or base.__options__.get('use_dict', False)
            if use_dict:
                options['use_dict'] = True
            use_weakref = use_weakref or base.__options__.get('use_weakref', False)
            if use_weakref:
                options['use_weakref'] = True
            copy_default = copy_default or base.__options__.get('copy_default', False)
            if copy_default:
                options['copy_default'] = True
            gc = gc or base.__options__.get('gc', False)
            if gc:
                options['gc'] = True
            iterable = iterable or base.__options__.get('iterable', False)
            if iterable:
                options['iterable'] = True
        else:
            continue

        fs = getattr(base, '__fields__', ())
        base_defaults = getattr(base, '__defaults__', {})
        n_defaults = len(base_defaults)
        base_annotations = getattr(base, '__annotations__', {})
        base_options = getattr(base, '__options__', {})
        base_fields_dict = base_options['fields_dict']
        n = number_of_dataitems(base)
        if type(fs) is tuple and len(fs) == n:
            for i, fn in enumerate(fs):
                if fn in fields:
                    raise TypeError('field %s is already defined in the %s' % (fn, base))
                else:
                    fields_dict[fn] = f = Field()
                    if _is_readonly_member(base.__dict__[fn]):
                        f['readonly'] = True
                    if fn in base_defaults:
                        f['default'] = base_defaults[fn]
                    if fn in base_annotations:
                        f['type'] = base_annotations[fn]
                    _fields.append(fn)
        else:
            raise TypeError("invalid fields in base class %r" % base)

    # for f in fields_dict.values():
    #     if not f.get('readonly', False):
    #         readonly = False
    #         break
        
    return _fields + fields

def _have_pyinit(bases):
    for base in bases:
        if base is object or base is dataobject:
            continue
        if '__init__' in base.__dict__:
            return True
        elif _have_pyinit(base.__bases__):
            return True
        
    return False

def _have_pynew(bases):
    for base in bases:
        if base is object or base is dataobject:
            continue
        if '__new__' in base.__dict__:
            return True
        elif _have_pynew(base.__bases__):
            return True
        
    return False
