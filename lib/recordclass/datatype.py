# coding: utf-8

# The MIT License (MIT)

# Copyright (c) «2017-2022» «Shibzukhov Zaur, szport at gmail dot com»

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

__all__ = 'clsconfig', 'datatype'

import sys as _sys
_PY36 = _sys.version_info[:2] >= (3, 6)
_PY37 = _sys.version_info[:2] >= (3, 7)
_PY310 = _sys.version_info[:2] >= (3, 10)
_PY311 = _sys.version_info[:2] >= (3, 11)
    
import typing
if _PY37:
    def _is_classvar(a_type):
        return (a_type is typing.ClassVar
                or (type(a_type) is typing._GenericAlias
                    and a_type.__origin__ is typing.ClassVar))
else:
    def _is_classvar(a_type):
        return a_type is typing._ClassVar #  or issubclass(a_type, typing.ClassVar)

def clsconfig(*, sequence=False, mapping=False, readonly=False,
              use_dict=False, use_weakref=False, iterable=False, 
              hashable=False, gc=False, deep_dealloc=False):
    from ._dataobject import _clsconfig
    def func(cls, *, sequence=sequence, mapping=mapping, readonly=readonly, use_dict=use_dict,
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

def get_option(options, name, default=False):
    if name in options:
        val = options[name]
        if not val:
            del options[name]
    else:
        val = default
        if val:
            options[name] = val
    return val
                
_ds_cache = {}
_ds_ro_cache = {}

def make_init(ns, init=0, post_init=0):
    if init == 2:
        if post_init == 2:
            def __init__(self, *args, **kw):
                print('2/2')
                self.__py_init__(*args, **kw)
                self.__post_init__()
            return __init__
        elif post_init == 1:
            def __init__(self, *args, **kw):
                print('2/1')
                self.__py_init__(*args, **kw)
                self.__post_init__()
            return __init__
    elif init == 1:
        init = ns['__init__']
        if post_init == 2:
            def __init__(self, *args, **kw):
                print('1/2')
                self.__py_init__(*args, **kw)
                self.__post_init__()
            return __init__
        elif post_init == 1:
            def __init__(self, *args, **kw):
                print('1/1')
                init(self, *args, **kw)
                self.__post_init__()
            return __init__
            
                
class datatype(type):
    """
    Metatype for creating classes based on dataobject.
    """
    def __new__(metatype, typename, bases, ns, *,
                gc=False, fast_new=True, readonly=False, iterable=False,
                deep_dealloc=False, sequence=False, mapping=False,
                use_dict=False, use_weakref=False, hashable=False, 
                mapping_only=False):

        from .utils import check_name, collect_info_from_bases
        from ._dataobject import dataobject
        from ._dataobject import _clsconfig, _dataobject_type_init, dataobjectproperty
        from sys import intern as _intern
        if _PY311:
            from ._dataobject import member_new

        options = ns.get('__options__', None)
        if options is None:
            options = ns['__options__'] = {}

        gc = get_option(options, 'gc', gc)
        fast_new = get_option(options, 'fast_new', fast_new)
        readonly = get_option(options, 'readonly', readonly)
        iterable = get_option(options, 'iterable', iterable)
        deep_dealloc = get_option(options, 'deep_dealloc', deep_dealloc)
        sequence = get_option(options, 'sequence', sequence)
        mapping = get_option(options, 'mapping', mapping)
        use_dict = get_option(options, 'use_dict', use_dict)
        use_weakref = get_option(options, 'use_weakref', use_weakref)
        hashable = get_option(options, 'hashable', hashable)
        
        if bases:
            base0 = bases[0]
            if not issubclass(base0, dataobject):
                raise TypeError("First base class should be subclass of dataobject")
        else:
            bases = (dataobject,)

        annotations = ns.get('__annotations__', {})
        
        int_type = type(1)

        if '__fields__' in ns:
            fields = ns['__fields__']
            if annotations:
                for fn in fields:
                    if _is_classvar(annotations.get(fn, None)):
                        raise TypeError(f'__fields__ contain  {fn}:ClassVar')
            if not isinstance(fields, int_type):
                fields_dict = {fn:{} for fn in fields}
            else:
                fields_dict = {}
                
        else:
            fields_dict = {fn:{'type':tp} \
                           for fn,tp in annotations.items() \
                           if not _is_classvar(tp)}
            fields = tuple(fields_dict)
            
        has_fields = True
        if isinstance(fields, int_type):
            has_fields = False
            n_fields = fields
            sequence = options['sequence'] = True
            iterable = options['iterable'] = True
            fields = ()
        else:
            fields = [_intern(check_name(fn)) for fn in fields]

        if sequence:
            options['sequence'] = True
        if mapping:
            options['mapping'] = True
            
        if sequence or mapping:
            iterable = True
            options['iterable'] = True
            
        if '__iter__' in ns:
            iterable = options['iterable'] = True
        else:
            for base in bases:
                if '__iter__' in base.__dict__:
                    iterable = True
                    options['iterable'] = True
                    break

        if readonly:
            hashable = True
        if hashable:
            options['hashable'] = hashable

        if has_fields:
            if annotations:
                annotations = {fn:annotations[fn] \
                               for fn in fields \
                               if fn in annotations}

            if '__dict__' in fields:                
                fields.remove('__dict__')
                if '__dict__' in annotations:
                    del annotations['__dict__']
                use_dict = options['use_dict'] = True
                import warnings
                warnings.warn("Use 'use_dict=True' instead")

            if '__weakref__' in fields:
                fields.remove('__weakref__')
                if '__weakref__' in annotations:
                    del annotations['__weakref__']
                use_weakref = options['use_weakref'] = True
                import warnings
                warnings.warn("Use 'use_weakref=True' instead")

            if '__defaults__' in ns:
                defaults_dict = ns['__defaults__']
            else:
                defaults_dict = {f:ns[f] for f in fields if f in ns}
            _matching_annotations_and_defaults(annotations, defaults_dict)

            fields_dict = {}
            for fn in fields:
                fields_dict[fn] = f = {}
                if fn in annotations:
                    f['type'] = annotations[fn]
                if fn in defaults_dict:
                    f['default'] = defaults_dict[fn]

            if readonly:
                if type(readonly) is type(True):
                    for f in fields_dict.values():
                        f['readonly'] = True
                else:
                    for fn in readonly:
                        fields_dict[fn]['readonly'] = True
            fields = [f for f in fields if f in fields_dict]

            if bases and (len(bases) > 1 or bases[0] is not dataobject):
                _fields, _fields_dict, _use_dict, _use_weakref = collect_info_from_bases(bases)
                use_dict = _use_dict or use_dict
                use_weakref = _use_weakref or use_weakref
                _defaults_dict = {fn:fd['default'] for fn,fd in _fields_dict.items() if 'default' in fd} 
                _annotations = {fn:fd['type'] for fn,fd in _fields_dict.items() if 'type' in fd} 

                if fields:
                    fields = [fn for fn in fields if fn not in _fields]

                fields = _fields + fields

                _fields_dict.update(fields_dict)
                fields_dict = _fields_dict

                _defaults_dict.update(defaults_dict)
                defaults_dict = _defaults_dict

                _annotations.update(annotations)
                annotations = _annotations
                del _fields, _fields_dict, _use_dict

            fields = tuple(fields)
            n_fields = len(fields)

            if use_dict:
                options['use_dict'] = use_dict
            if use_weakref:
                options['use_weakref'] = use_weakref

            if fast_new:
                options['fast_new'] = fast_new

            if has_fields and not fast_new and '__new__' not in ns:
                __new__ = _make_new_function(typename, fields, defaults_dict, annotations, use_dict)
                __new__.__qualname__ = typename + '.' + '__new__'
                if not __new__.__doc__:
                    __new__.__doc__ = _make_cls_doc(typename, fields, annotations, defaults)

                ns['__new__'] = __new__

        if has_fields and not _PY311:
            for i, name in enumerate(fields):
                fd = fields_dict[name]
                fd_readonly = fd.get('readonly', False)
                if fd_readonly:
                    ds = _ds_ro_cache.get(i, None)
                else:
                    ds = _ds_cache.get(i, None)
                if ds is None:
                    if fd_readonly:
                        ds = dataobjectproperty(i, True)
                    else:
                        ds = dataobjectproperty(i, False)
                ns[name] = ds

        module = ns.get('__module__', None)
        if module is None:
            try:
                module = _sys._getframe(2).f_globals.get('__name__', '__main__')
                ns['__module'] = module
            except (AttributeError, ValueError):
                pass
        else:
            pass
        
        has_init = False
#         py_post_init = 0
        
#         if '__post_init__' in ns:
#             py_post_init = 1
#         else:
#             for base in bases:
#                 if '__post_init__' in base.__dict__:
#                     py_post_init = 2
#                     break
        
        if '__init__' in ns:
            has_init = True
        else:
            for base in bases:
                if base != dataobject and '__init__' in base.__dict__:
                    has_init = True
                    ns['__init__'] = base.__dict__['__init__']
                    break
                    
#         if py_init > 0 and py_post_init > 0:
#             init = make_init(ns, py_init, py_post_init)
#             if init is not None:
#                 ns['__init__'] = init
                    
        if has_fields:
            defaults = tuple([defaults_dict.get(fn, None) for fn in fields])
            ns['__fields__'] = fields
            ns['__defaults__'] = defaults
            ns['__annotations__'] = annotations

            if _PY310:
                ns['__match_args__'] = fields

            if '__doc__' not in ns:
                ns['__doc__'] = _make_cls_doc(typename, fields, annotations, defaults, use_dict)

        cls = type.__new__(metatype, typename, bases, ns)

        if has_fields and _PY311:
            for i, name in enumerate(fields):
                fd = fields_dict[name]
                fd_readonly = fd.get('readonly', False)
                if fd_readonly:
                    ds = member_new(cls, name, i, 1)
                else:
                    ds = member_new(cls, name, i, 0)
                setattr(cls, name, ds)

        _dataobject_type_init(cls)

        _clsconfig(cls, sequence=sequence, mapping=mapping, readonly=readonly,
                        use_dict=use_dict, use_weakref=use_weakref, 
                        iterable=iterable, hashable=hashable,
                        gc=gc, deep_dealloc=deep_dealloc, mapping_only=mapping_only)
        return cls

    def __delattr__(cls, name):
        from ._dataobject import dataobjectproperty
        if name in cls.__dict__:
            o = getattr(cls, name)
            if type(o) is dataobjectproperty or name in {'__fields__', '__defaults__', '__annotations__'}:
                raise AttributeError(f"Attribute {name} of the class {cls.__name__} can't be deleted")
        type.__delattr__(cls, name)

    def __setattr__(cls, name, ob):
        if name in {'__fields__', '__defaults__', '__annotations__'}:
            raise AttributeError(f"Attribute {name} of the class {cls.__name__} can't be modified")
        type.__setattr__(cls, name, ob)

def _make_new_function(typename, fields, defaults_dict, annotations, use_dict):

    from ._dataobject import dataobject

    if fields and defaults_dict:
        fields2 = [fn for fn in fields if fn not in defaults_dict] + \
                  ["%s=%r" % (fn,None) for fn in fields if fn in defaults_dict]
    else:
        fields2 = fields

    joined_fields = ', '.join(fields)
    joined_fields2 = ', '.join(fields2)

    new_func_def = f"""\
def __new__(_cls_, {joined_fields2}):
    "Create new instance: {typename}({joined_fields2})"
    return _method_new(_cls_, {joined_fields})
"""
    
    new_func_def_use_dict = f"""\
def __new__(_cls_, {joined_fields2}, **kw):
    "Create new instance: {typename}({joined_fields2}, **kw)"
    return _method_new(_cls_, {joined_fields}, **kw)
"""
    
    if use_dict:
        new_func_def = new_func_def_use_dict

    # if has_init:
    #     _method_new = new_basic
    # else:
    _method_new = dataobject.__new__

    namespace = dict(_method_new=_method_new)

    code = compile(new_func_def, "", "exec")
    eval(code, namespace)

    __new__ = namespace['__new__']

    if annotations:
        __new__.__annotations__ = annotations

    if defaults_dict:
        __new__.__defaults__ = tuple(defaults_dict.values())

    return __new__

def _type2str(tp):
    if hasattr(tp, '__name__'):
        return tp.__name__
    else:
        return str(tp)

def _make_cls_doc(typename, fields, annotations, defaults, use_dict):

    fields2 = []
    for i, fn in enumerate(fields):
        if fn in annotations:
            tp = annotations[fn]
            fn_txt = "%s:%s" % (fn, (tp if type(tp) is str else _type2str(tp)))            
        else:
            fn_txt = fn
        defval = defaults[i]
        if defval is not None:
            fn_txt += "=%r" % defval
        fields2.append(fn_txt)
    joined_fields2 = ', '.join(fields2)

    if use_dict:
        doc = f"""{typename}({joined_fields2}, **kw)\n--\nCreate class {typename} instance"""
    else:
        doc = f"""{typename}({joined_fields2})\n--\nCreate class {typename} instance"""

    return doc
