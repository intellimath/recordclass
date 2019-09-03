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

from .utils import dataslot_offset, dataitem_offset
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

__all__ = ('datatype', 'make_class', 'make_dataclass', 'make_arrayclass',
           'asdict', 'clsconfig', 'enable_gc')

int_type = type(1)

def clsconfig(sequence=False, mapping=False, readonly=False, 
              use_dict=False, use_weakref=False, iterable=True, hashable=False):
    from ._dataobject import _clsconfig    
    def func(cls, sequence=sequence, mapping=mapping, readonly=readonly, use_dict=use_dict,
                  use_weakref=use_weakref, iterable=iterable, hashable=hashable, _clsconfig=_clsconfig):
        _clsconfig(cls, sequence=sequence, mapping=mapping, readonly=readonly, use_dict=use_dict,
                   use_weakref=use_weakref, iterable=iterable, hashable=hashable)
        return cls
    return func

def make_dataclass(typename, fields=None, bases=None, namespace=None, 
                   varsize=False,  use_dict=False, use_weakref=False, hashable=True,
                   sequence=False, mapping=False, iterable=False, readonly=False,
                   defaults=None, module=None, argsonly=False, gc=False):
    
    from ._dataobject import _clsconfig, enable_gc
    from ._dataobject import dataobject, datatuple

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
    }

    if namespace is None:
        ns = {}
    else:
        ns = namespace

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
        
    if not bases:
        if varsize:
            bases = (datatuple,)
        else:
            bases = (dataobject,)
    elif varsize and not isinstance(base[0], datatuple):
        raise TypeError("First base class should be subclass of datatuple")

    cls = datatype(typename, bases, ns)
    
    _clsconfig(cls, sequence=sequence, mapping=mapping, readonly=readonly, 
               use_dict=use_dict, use_weakref=use_weakref, iterable=iterable, hashable=hashable)

    if gc:
        cls = enable_gc(cls)

    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            module = None
    if module is not None:
        cls.__module__ = module

    return cls

make_class = make_dataclass

def make_arrayclass(typename, fields=0, bases=None, namespace=None, 
                 varsize=False, use_dict=False, use_weakref=False, hashable=False,
                 readonly=False, gc=False,
                 module=None):

    from ._dataobject import dataobject, datatuple, enable_gc
    
    if not isinstance(fields, int_type):
        raise TypeError("argument fields is not integer")
        
    if not bases:
        if varsize:
            bases = (datatuple,)
        else:
            bases = (dataobject,)        

    options = {
        'dict':use_dict, 'weakref':use_weakref, 'hashable':hashable, 
        'sequence':True, 'iterable':True, 'readonly':readonly, 
    }

    if namespace is None:
        ns = {}
    else:
        ns = namespace

    ns['__options__'] = options
    ns['__fields__'] = fields

    cls = datatype(typename, bases, ns)

    if gc:
        cls = enable_gc(cls)

    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            module = None
    if module is not None:
        cls.__module__ = module

    return cls

class datatype(type):

    def __new__(metatype, typename, bases, ns):        
        from ._dataobject import _clsconfig, _dataobject_type_init, dataslotgetset

        options = ns.pop('__options__', {})
        readonly = options.get('readonly', False)
        hashable = options.get('hashable', False)
        sequence = options.get('sequence', False)
        mapping = options.get('mapping', False)
        iterable = options.get('iterable', False)
        argsonly = options.get('argsonly', False)
        use_dict = options.get('dict', False)
        use_weakref = options.get('weakref', False)

        if not bases:
            raise TypeError("The base class in not specified")

        if bases[0].__itemsize__:
            varsize = True
        else:
            varsize = False

        annotations = ns.get('__annotations__', {})

        if '__fields__' in ns:
            fields = ns.get('__fields__')
        else:
            fields = [name for name in annotations]

        has_fields = True
        if isinstance(fields, int_type):
            has_fields = False
            n_fields = fields
            sequence = True
            iterable = True
            fields = ()
        else:
            fields = [_intern(check_name(fn)) for fn in fields]

        if varsize:
            sequence = True
            iterable = True
            
        if sequence or mapping:
            iterable = True

        if has_fields:
            if annotations:
                annotations = {fn:annotations[fn] for fn in fields if fn in annotations}

            if '__dict__' in fields:
                fields.remove('__dict__')
                use_dict = True

            if '__weakref__' in fields:
                fields.remove('__weakref__')
                use_weakref = True

            n_fields = len(fields)

            _fields, _defaults, _annotations = collect_info_from_bases(bases)

            defaults = {f:ns[f] for f in fields if f in ns}

            if fields:
                fields = [f for f in fields if f not in _fields]
                n_fields = len(fields)
            fields = _fields + fields
            n_fields += len(_fields)

            _defaults.update(defaults)
            defaults = _defaults

            _annotations.update(annotations)
            annotations = _annotations

            fields = tuple(fields)

            if fields and (not argsonly or defaults) and '__new__' not in ns:
                __new__ = make_new_function(typename, fields, defaults, annotations, varsize, use_dict)

                ns['__new__'] = __new__

        cls = type.__new__(metatype, typename, bases, ns)

        if has_fields:
            cls.__fields__ = fields
            if defaults:
                cls.__defaults__ = defaults
            if annotations:
                cls.__annotations__ = annotations

        _dataobject_type_init(cls)
        _clsconfig(cls, sequence=sequence, mapping=mapping, readonly=readonly, use_dict=use_dict,
                   use_weakref=use_weakref, iterable=iterable, hashable=hashable)

        if has_fields:
            if readonly is None or type(readonly) is bool:
                if readonly:
                    readonly_fields = set(fields)
                else:
                    readonly_fields = set()
            else:
                readonly_fields = set(readonly)

            for i, name in enumerate(fields):
                if name in readonly_fields:
                    setattr(cls, name, dataslotgetset(dataslot_offset(cls, i), True))
                else:
                    setattr(cls, name, dataslotgetset(dataslot_offset(cls, i)))

        return cls

def make_new_function(typename, fields, defaults, annotations, varsize, use_dict):
    
    from ._dataobject import dataobject, datatuple
    
    if fields and defaults:
        fields2 = [f for f in fields if f not in defaults] + [f for f in fields if f in defaults]
    else:
        fields2 = fields
    fields2 = tuple(fields2)
    
    if use_dict:
        if varsize:
            new_func_template = \
"""
def __new__(cls, {2}, *args, **kw):
    'Create new instance: {0}({1})'
    return _method_new(cls, {1}, *args, **kw)
"""            
        else:
            new_func_template = \
"""
def __new__(cls, {2}, **kw):
    'Create new instance: {0}({1})'
    return _method_new(cls, {1}, **kw)
"""
    else:
        if varsize:
            new_func_template = \
"""
def __new__(cls, {2}, *args):
    'Create new instance: {0}({1})'
    return _method_new(cls, {1}, *args)
"""
        else:
            new_func_template = \
"""
def __new__(cls, {2}):
    'Create new instance: {0}({1})'
    return _method_new(cls, {1})
"""
    new_func_def = new_func_template.format(typename, ', '.join(fields), ', '.join(fields2))
    
    if varsize:
        _method_new = datatuple.__new__
    else:
        _method_new = dataobject.__new__

    namespace = dict(_method_new=_method_new)

    code = compile(new_func_def, "", "exec")
    eval(code, namespace)
    
    __new__ = namespace['__new__']
    
    if defaults:
        default_vals = tuple(defaults[f] for f in fields2 if f in defaults)
        __new__.__defaults__ = default_vals    
    if annotations:
        __new__.__annotations__ = annotations

    return __new__

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
