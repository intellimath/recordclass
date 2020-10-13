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

def enable_gc(cls):
    from ._dataobject import _enable_gc
    _enable_gc(cls)
    return cls

def _matching_annotations_and_defaults(annotations, defaults):
#     print(annotations, defaults)
    args = True
    for name, val in annotations.items():
        if name in defaults:
            args = False
        else:
            if not args:
                defaults[name] = None

class datatype(type):

    def __new__(metatype, typename, bases, ns):
        from ._dataobject import _clsconfig, _dataobject_type_init, dataslotgetset

        options = ns.pop('__options__', {})
        readonly = options.get('readonly', False)
        hashable = options.get('hashable', True)
        sequence = options.get('sequence', False)
        mapping = options.get('mapping', False)
        iterable = options.get('iterable', True)
        argsonly = options.get('argsonly', False)
        fast_new = options.get('fast_new', False)
        use_dict = options.get('use_dict', False)
        use_weakref = options.get('use_weakref', False)

        use_dict = False
        use_weakref = False

        if not bases:
            raise TypeError("The base class in not specified")

        if bases[0].__itemsize__:
            varsize = True
        else:
            varsize = False

        annotations = ns.get('__annotations__', {})

        if '__fields__' in ns:
            fields = ns['__fields__']
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
                if '__dict__' in annotations:
                    del annotations['__dict__']
                use_dict = True

            if '__weakref__' in fields:
                fields.remove('__weakref__')
                if '__weakref__' in annotations:
                    del annotations['__weakref__']
                use_weakref = True

            _fields, _defaults, _annotations = collect_info_from_bases(bases)

            defaults = {f:ns[f] for f in fields if f in ns}
            _matching_annotations_and_defaults(annotations, defaults)

            if fields:
                fields = [f for f in fields if f not in _fields]
            fields = _fields + fields
            fields = tuple(fields)
            n_fields = len(fields)

            _defaults.update(defaults)
            defaults = _defaults

            _annotations.update(annotations)
            annotations = _annotations

            if fields and not fast_new and (not argsonly or defaults) and '__new__' not in ns:
                __new__ = _make_new_function(typename, fields, defaults, annotations, varsize, use_dict)
                __new__.__qualname__ = typename + '.' + '__new__'

                ns['__new__'] = __new__

        if has_fields:
            if readonly:
                if type(readonly) is type(True):
                    readonly_fields = set(fields)
                else:
                    readonly_fields = set(readonly)
            else:
                readonly_fields = set()

            for i, name in enumerate(fields):
                offset = dataslot_offset(i, n_fields, varsize)
                if name in readonly_fields:
                    ns[name] = dataslotgetset(offset, True)
                else:
                    ns[name] = dataslotgetset(offset)

        module = ns.get('__module__', None)
        if module is None:
            try:
                module = _sys._getframe(2).f_globals.get('__name__', '__main__')
                ns['__module'] = module
            except (AttributeError, ValueError):
                pass
        else:
            pass

        cls = type.__new__(metatype, typename, bases, ns)

        if has_fields:
            cls.__fields__ = fields
            if defaults:
                cls.__defaults__ = defaults
            if annotations:
                cls.__annotations__ = annotations

            cls.__doc__ = _make_cls_doc(cls, typename, fields, defaults, varsize, use_dict)

        _dataobject_type_init(cls)
        _clsconfig(cls, sequence=sequence, mapping=mapping, readonly=readonly, use_dict=use_dict,
                   use_weakref=use_weakref, iterable=iterable, hashable=hashable)

        return cls

def _make_new_function(typename, fields, defaults, annotations, varsize, use_dict):

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
def __new__(_cls_, {2}, *args, **kw):
    'Create new instance: {0}({1}, *args, **kw)'
    return _method_new(_cls_, {1}, *args, **kw)
"""
        else:
            new_func_template = \
"""
def __new__(_cls_, {2}, **kw):
    'Create new instance: {0}({1}, **kw)'
    return _method_new(_cls_, {1}, **kw)
"""
    else:
        if varsize:
            new_func_template = \
"""
def __new__(_cls_, {2}, *args):
    'Create new instance: {0}({1}, *args)'
    return _method_new(_cls_, {1}, *args)
"""
        else:
            new_func_template = \
"""
def __new__(_cls_, {2}):
    'Create new instance: {0}({1})'
    return _method_new(_cls_, {1})
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

def _make_cls_doc(cls, typename, fields, defaults, varsize, use_dict):

    from ._dataobject import dataobject, datatuple

    if fields and defaults:
        fields2 = [f for f in fields if f not in defaults] + ["%s=%r" % (f, defaults[f]) for f in fields if f in defaults]
    else:
        fields2 = fields
    fields2 = tuple(fields2)

    if use_dict:
        if varsize:
            template = "{0}({2}, *args, **kw)\n--\nCreate class instance"
        else:
            template = "{0}({2}, **kw)\n--\nCreate class instance"
    else:
        if varsize:
            template = "{0}({2}, *args)\n--\nCreate class instance"
        else:
            template = "{0}({2})\n--\nCreate class instance"
    doc = template.format(typename, ', '.join(fields), ', '.join(fields2))

    return doc

