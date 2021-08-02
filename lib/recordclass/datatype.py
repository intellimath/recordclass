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

from .utils import dataslot_offset
from .utils import check_name, collect_info_from_bases

__all__ = 'clsconfig', 'datatype'

import sys as _sys

_intern = _sys.intern

int_type = type(1)

def clsconfig(sequence=False, mapping=False, readonly=False,
              use_dict=False, use_weakref=False, iterable=False, 
              hashable=False, gc=False, deep_dealloc=False):
    from ._dataobject import _clsconfig, dataslotgetset
    def func(cls, sequence=sequence, mapping=mapping, readonly=readonly, use_dict=use_dict,
                  use_weakref=use_weakref, iterable=iterable, hashable=hashable, _clsconfig=_clsconfig):
        _clsconfig(cls, sequence=sequence, mapping=mapping, readonly=readonly, use_dict=use_dict,
                        use_weakref=use_weakref, iterable=iterable, hashable=hashable, gc=gc, 
                        deep_dealloc=deep_dealloc)
        return cls
    return func

def _matching_annotations_and_defaults(annotations, defaults):
    first_default = 0
    for name in annotations:
        if name in defaults:
            first_default = 1
        else:
            if first_default:
                raise TypeError('A field without default value appears after a field with default value')

_ds_cache = {}
_ds_ro_cache = {}
                
class datatype(type):

    def __new__(metatype, typename, bases, ns, 
                gc=False, fast_new=False, readonly=False, iterable=False,
                deep_dealloc=False):

        from ._dataobject import _clsconfig, _dataobject_type_init, dataslotgetset

        options = ns.pop('__options__', {})
        hashable = options.get('hashable', False)
        sequence = options.get('sequence', False)
        mapping = options.get('mapping', False)
        use_dict = options.get('use_dict', False)
        use_weakref = options.get('use_weakref', False)
        deep_dealloc = options.get('deep_dealloc', False)

        gc = options.get('gc', gc)
        fast_new = options.get('fast_new', fast_new)
        readonly = options.get('readonly', readonly)
        iterable = options.get('iterable', iterable)
        deep_dealloc = options.get('deep_dealloc', deep_dealloc)

        if not bases:
            raise TypeError("The base class in not specified")

        annotations = ns.get('__annotations__', {})

        if '__fields__' in ns:
            fields = ns['__fields__']
        else:
            fields = tuple(annotations)

        has_fields = True
        if isinstance(fields, int_type):
            has_fields = False
            n_fields = fields
            sequence = True
            iterable = True
            fields = ()
        else:
            fields = [_intern(check_name(fn)) for fn in fields]

        if sequence or mapping:
            iterable = True
            
        if '__iter__' in ns:
            iterable = True
        else:
            for base in bases:
                if '__iter__' in base.__dict__:
                    iterable = True
#                     ns['__iter__'] = base.__dict__['__iter__']
                    break
            
        if readonly:
            hashable = True

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

            if '__defaults__' in ns:
                defaults = ns['__defaults__']
            else:
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

            if fields and not fast_new and '__new__' not in ns:
                __new__ = _make_new_function(typename, fields, defaults, annotations, use_dict)
                __new__.__qualname__ = typename + '.' + '__new__'
                if not __new__.__doc__:
                    __new__.__doc__ = _make_cls_doc(typename, fields, annotations, defaults, use_dict)

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
                offset = dataslot_offset(i, n_fields)
                if name in readonly_fields:
                    ds = _ds_ro_cache.get(offset, None)
                else:
                    ds = _ds_cache.get(offset, None)
                if ds is None:
                    if name in readonly_fields:
                        ds = dataslotgetset(offset, True)
                    else:
                        ds = dataslotgetset(offset)
                ns[name] = ds

        if '__repr__' not in ns:
            def __repr__(self):
                args = ', '.join((name + '=' + repr(getattr(self, name))) for name in self.__class__.__fields__) 
                kw = getattr(self, '__dict__', None)
                if kw:
                    return f'{typename}({args}, **{kw})'
                else:
                    return f'{typename}({args})'
            __repr__.__qual_name__ =  f'{typename}.__repr__'

            ns['__repr__'] = __repr__

            if '__str__' not in ns:
                ns['__str__'] = __repr__

        module = ns.get('__module__', None)
        if module is None:
            try:
                module = _sys._getframe(2).f_globals.get('__name__', '__main__')
                ns['__module'] = module
            except (AttributeError, ValueError):
                pass
        else:
            pass

        if has_fields:
            ns['__fields__'] = fields
            ns['__defaults__'] = defaults
            ns['__annotations__'] = annotations
            
            if '__doc__' not in ns:
                ns['__doc__'] = _make_cls_doc(typename, fields, annotations, defaults, use_dict)
        
        cls = type.__new__(metatype, typename, bases, ns)

        _dataobject_type_init(cls)
        
        _clsconfig(cls, sequence=sequence, mapping=mapping, readonly=readonly,
                        use_dict=use_dict, use_weakref=use_weakref, 
                        iterable=iterable, hashable=hashable,
                        gc=gc, deep_dealloc=deep_dealloc)
        return cls

def _make_new_function(typename, fields, defaults, annotations, use_dict):

    from ._dataobject import dataobject

    if fields and defaults:
        fields2 = [fn for fn in fields if fn not in defaults] + \
                  ["%s=%r" % (fn,defaults[fn]) for fn in fields if fn in defaults]
    else:
        fields2 = fields
    fields2 = tuple(fields2)

    if use_dict:
        new_func_template = \
"""
def __new__(_cls_, {2}, **kw):
    'Create new instance: {0}({2}, **kw)'
    return _method_new(_cls_, {1}, **kw)
"""
    else:
        new_func_template = \
"""
def __new__(_cls_, {2}):
    'Create new instance: {0}({2})'
    return _method_new(_cls_, {1})
"""
    new_func_def = new_func_template.format(typename, ', '.join(fields), ', '.join(fields2))

    _method_new = dataobject.__new__

    namespace = dict(_method_new=_method_new)

    code = compile(new_func_def, "", "exec")
    eval(code, namespace)

    __new__ = namespace['__new__']

    if annotations:
        __new__.__annotations__ = annotations

    return __new__

def _make_cls_doc(typename, fields, annotations, defaults, use_dict):

    fields2 = []
    for fn in fields:
        if fn in annotations:
            tp = annotations[fn]
            fn_txt = "%s:%s" % (fn, (tp if type(tp) is str else tp.__name__))            
        else:
            fn_txt = fn
        if fn in defaults:
            fn_txt += "=%r" % defaults[fn]
        fields2.append(fn_txt)
    fields2 = tuple(fields2)

    if use_dict:
        template = "{0}({1}, **kw)\n--\nCreate class {0} instance"
    else:
        template = "{0}({1})\n--\nCreate class {0} instance"
    doc = template.format(typename, ', '.join(fields2))

    return doc
