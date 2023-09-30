# coding: utf-8

# The MIT License (MIT)

# Copyright (c) «2017-2023» «Shibzukhov Zaur, szport at gmail dot com»

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

__all__ = 'datatype',

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
        return isinstance(a_type, typing._ClassVar) #or issubclass(a_type, typing.ClassVar)

def _matching_annotations_and_defaults(annotations, defaults):
    first_default = False
    for name in annotations:
        if name in defaults:
            first_default = True
        else:
            if first_default:
                raise TypeError('A field without default value appears after a field with default value')
                
_ds_cache = {}
_ds_ro_cache = {}

class Field(dict):
    pass
                
class datatype(type):
    """
    Metatype for creating classes based on dataobject.
    """
    def __new__(metatype, typename, bases, ns, *,
                gc=False, fast_new=True, readonly=False, iterable=False,
                deep_dealloc=False, sequence=False, mapping=False,
                use_dict=False, use_weakref=False, hashable=False, 
                immutable_type=False, copy_default=False):

        from .utils import check_name, collect_info_from_bases
        from ._dataobject import dataobject
        from ._dataobject import dataobjectproperty
        from sys import intern as _intern
        if _PY311:
            from ._dataobject import member_new

        options = {}
        if gc:
            options['gc'] = gc
        if fast_new:
            options['fast_new'] = fast_new
        if readonly:
            options['readonly'] = readonly
        if iterable:
            options['iterable'] = iterable
        if deep_dealloc:
            options['deep_dealloc'] = deep_dealloc
        if sequence:
            options['sequence'] = sequence
        if mapping:
            options['mapping'] = mapping
        if hashable:
            options['hashable'] = hashable
        if use_dict:
            options['use_dict'] = use_dict
        if use_weakref:
            options['use_weakref'] = use_weakref
        if copy_default:
            options['copy_default'] = copy_default
        if immutable_type:
            options['immutable_type'] = immutable_type
            
        
        if bases:
            base0 = bases[0]
            if not issubclass(base0, dataobject):
                raise TypeError("First base class should be subclass of dataobject")
        else:
            bases = (dataobject,)

        annotations = ns.get('__annotations__', {})
        classvars = {fn for fn,tp in annotations.items() \
                        if _is_classvar(tp)}
        
        int_type = type(1)

        if '__fields__' in ns:
            fields = ns['__fields__']
            fields_dict = {}
            if not isinstance(fields, int_type):
                for fn in fields:
                    if fn in classvars:
                        raise TypeError(f'__fields__ contain  {fn}:ClassVar')
                    if fn in annotations:
                        fields_dict[fn] = f = Field(type=annotations[fn])
                    else:
                        fields_dict[fn] = f = Field()
        else:
            fields_dict = {fn:Field(type=tp) \
                           for fn,tp in annotations.items() \
                           if fn not in classvars}
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
        # else:
        #     for base in bases:
        #         if '__iter__' in base.__dict__:
        #             iterable = True
        #             options['iterable'] = True
        #             break

        if readonly:
            hashable = True
        if hashable:
            options['hashable'] = hashable

        if not _PY311 and immutable_type:
            import warnings
            warnings.warn("immutable_type parameter can be used only for python >= 3.11")

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

            for fn,val in defaults_dict.items():
                f = fields_dict.get(fn, None)
                if f is not None:
                    f['default'] = val

            if readonly:
                if type(readonly) is bool:
                    for f in fields_dict.values():
                        f['readonly'] = True
                else:
                    for fn in readonly:
                        fields_dict[fn]['readonly'] = True
            fields = [f for f in fields if f in fields_dict]

            if bases and (len(bases) > 1) or bases[0] is not dataobject:
                fields = collect_info_from_bases(bases, fields, fields_dict, options)
                for fn in classvars:
                    if fn in fields:
                        raise TypeError(f"field '{fn}' is a class variable and an instance field at the same time")
                use_dict = options.get('use_dict', False)
                use_weakref = options.get('use_weakref', False)
                copy_default = options.get('copy_default', False)
                gc = options.get('gc', False)
                iterable = options.get('iterable', False)
                defaults_dict = {fn:fd['default'] for fn,fd in fields_dict.items() if 'default' in fd} 
                annotations = {fn:fd['type'] for fn,fd in fields_dict.items() if 'type' in fd} 

            fields = tuple(fields)

            if has_fields and not fast_new and ('__new__' not in ns or '__init__' not in ns):
                __new__ = _make_new_function(typename, fields, defaults_dict, annotations, use_dict)
                __new__.__qualname__ = typename + '.' + '__new__'
                if not __new__.__doc__:
                    __new__.__doc__ = _make_cls_doc(typename, fields, annotations, defaults)

                ns['__new__'] = __new__

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
            options['fields_dict'] = fields_dict
            default_vals = tuple([fields_dict[fn].get('default',None) for fn in fields])
            ns['__fields__'] = fields
            ns['__defaults__'] = defaults_dict
            ns['__default_vals__'] = default_vals
            ns['__annotations__'] = annotations

            if _PY310:
                ns['__match_args__'] = fields

            if '__doc__' not in ns:
                ns['__doc__'] = _make_cls_doc(typename, fields, annotations, default_vals, use_dict)
        
        ns['__options__'] = options

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

        cls.__configure__(sequence=sequence, mapping=mapping, readonly=readonly,
                          hashable=hashable, iterable=iterable, use_dict=use_dict, use_weakref=use_weakref,
                          gc=gc, deep_dealloc=deep_dealloc, immutable_type=immutable_type,
                          copy_default=copy_default,
                         )

        return cls

    def __configure__(cls,  gc=False, fast_new=True, readonly=False, iterable=False,
                            deep_dealloc=False, sequence=False, mapping=False,
                            use_dict=False, use_weakref=False, hashable=False, 
                            mapping_only=False, immutable_type=False, copy_default=False):

        from ._dataobject import (_datatype_collection_mapping, _datatype_hashable, _datatype_iterable,
                                  _datatype_use_weakref, _datatype_use_dict, _datatype_enable_gc, 
                                  _datatype_deep_dealloc, _datatype_vectorcall, _pytype_modified, 
                                  _datatype_immutable, _dataobject_type_init, _datatype_copy_default,
                                  _datatype_from_basetype_hashable, _datatype_from_basetype_iterable)
        from .utils import _have_pyinit, _have_pynew


        is_pyinit = '__init__' in cls.__dict__
        is_pynew = '__new__' in cls.__dict__
        if not is_pyinit:
            is_pyinit = _have_pyinit(cls.__bases__)
        if not is_pynew:
            is_pynew = _have_pynew(cls.__bases__)

        if immutable_type and (is_pynew or is_pyinit):
            raise TypeError('if immutable_type=True then __init__ or __new__ are not allowed')
        
        _dataobject_type_init(cls)

        _datatype_collection_mapping(cls, sequence, mapping, readonly)
        if hashable:
            _datatype_hashable(cls)
        else:
            _datatype_from_basetype_hashable(cls)
        if iterable:
            _datatype_iterable(cls)
        else:
            _datatype_from_basetype_iterable(cls)
        if use_dict:
            _datatype_use_dict(cls)
        if use_weakref:
            _datatype_use_weakref(cls)
        if gc:
            _datatype_enable_gc(cls)
        if deep_dealloc:
            _datatype_deep_dealloc(cls)
        if not copy_default and not is_pyinit and not is_pynew:
            _datatype_vectorcall(cls)
        if copy_default and not is_pyinit and not is_pynew:
            _datatype_copy_default(cls)
        if _PY311 and immutable_type:
            _datatype_immutable(cls)
        _pytype_modified(cls)

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
            fn_txt += "=%s" % repr(defval)
        fields2.append(fn_txt)

    joined_fields2 = ', '.join(fields2)

    if use_dict:
        doc = f"""{typename}({joined_fields2}, **kw)\n--\nCreate class {typename} instance"""
    else:
        doc = f"""{typename}({joined_fields2})\n--\nCreate class {typename} instance"""

    return doc
