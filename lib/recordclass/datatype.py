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

__all__ = 'clsconfig', 'datatype'

def clsconfig(*, sequence=False, mapping=False, readonly=False,
              use_dict=False, use_weakref=False, iterable=False, 
              hashable=False, gc=False, deep_dealloc=False, mapping_only=False):
    from ._dataobject import _clsconfig
    def func(cls, *, sequence=sequence, mapping=mapping, readonly=readonly, use_dict=use_dict,
                  use_weakref=use_weakref, iterable=iterable, hashable=hashable, _clsconfig=_clsconfig):
        _clsconfig(cls, sequence=sequence, mapping=mapping, readonly=readonly, use_dict=use_dict,
                        use_weakref=use_weakref, iterable=iterable, hashable=hashable, gc=gc, 
                        deep_dealloc=deep_dealloc, mapping_only=mapping_only)
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
    """
    Metatype for creating classes based on dataobject.
    """

    def __new__(metatype, typename, bases, ns, *,
                gc=False, fast_new=False, readonly=False, iterable=False,
                deep_dealloc=False, sequence=False, mapping=False,
                use_dict=False, use_weakref=False, hashable=False, mapping_only=False):

        from .utils import check_name, collect_info_from_bases
        from ._dataobject import _clsconfig, _dataobject_type_init, dataobjectproperty
        from sys import intern as _intern

        options = ns.pop('__options__', {})

        gc = options.get('gc', gc)
        fast_new = options.get('fast_new', fast_new)
        readonly = options.get('readonly', readonly)
        iterable = options.get('iterable', iterable)
        deep_dealloc = options.get('deep_dealloc', deep_dealloc)
        sequence = options.get('sequence', sequence)
        mapping = options.get('mapping', mapping)
        use_dict = options.get('use_dict', use_dict)
        use_weakref = options.get('use_weakref', use_weakref)
        hashable = options.get('hashable', hashable)

        if not bases:
            raise TypeError("The base class in not specified")

        annotations = ns.get('__annotations__', {})
        
        int_type = type(1)

        if '__fields__' in ns:
            fields = ns['__fields__']
            if not isinstance(fields, int_type):
                field_dicts = {fn:{} for fn in fields}
            else:
                field_dicts = {}
        else:
            fields = tuple(annotations)
            field_dicts = {fn:{'type':tp} for fn,tp in annotations.items()}

        has_fields = True
        if isinstance(fields, type(1)):
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

            _fields, _fields_dict, _use_dict = collect_info_from_bases(bases)
            if _use_dict:
                use_dict = _use_dict
            _defaults = {fn:fd['default'] for fn,fd in _fields_dict.items() if 'default' in fd} 
            _annotations = {fn:fd['type'] for fn,fd in _fields_dict.items() if 'type' in fd} 

            if '__defaults__' in ns:
                defaults = ns['__defaults__']
            else:
                defaults = {f:ns[f] for f in fields if f in ns}
            _matching_annotations_and_defaults(annotations, defaults)

            if fields:
                fields = [fn for fn in fields if fn not in _fields]
            
            fields_dict = {}
            for fn in fields:
                fields_dict[fn] = f = {}
                if fn in annotations:
                    f['type'] = annotations[fn]
                if fn in defaults:
                    f['default'] = defaults[fn]
                
            if readonly:
                if type(readonly) is type(True):
                    for f in fields_dict.values():
                        f['readonly'] = True
                else:
                    for fn in readonly:
                        fields_dict[fn]['readonly'] = True
                
            fields = _fields + fields
            fields = tuple(fields)
            n_fields = len(fields)
            
            _fields_dict.update(fields_dict)
            fields_dict = _fields_dict

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
            if mapping_only:
                ns['__fields_dict__'] = {fn:i for i,fn in enumerate(fields)}
            else:
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
                            ds = dataobjectproperty(i)
                    ns[name] = ds

        if '__repr__' not in ns:
            if mapping_only:
                def __repr__(self):
                    args = ', '.join((name + '=' + repr(self[name])) for name in self.__class__.__fields__) 
                    kw = getattr(self, '__dict__', None)
                    if kw:
                        return f'{typename}({args}, **{kw})'
                    else:
                        return f'{typename}({args})'
            else:
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
                        gc=gc, deep_dealloc=deep_dealloc, mapping_only=mapping_only)
        return cls
    
    def __delattr__(cls, name):
        from ._dataobject import dataobjectproperty
        if name in cls.__dict__:
            o = getattr(cls, name)
            if type(o) is dataobjectproperty or name == '__fields__':
                raise AttributeError(f"Attribute {name} of the class {cls.__name__} can't be deleted")
        type.__delattr__(cls, name)
        
    def __setattr__(cls, name, ob):
        if name in ('__fields__', '__defaults__'):
            raise AttributeError(f"Attribute {name} of the class {cls.__name__} can't be modified")
        type.__setattr__(cls, name, ob)

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
    "Create new instance: {0}({2}, **kw)"
    return _method_new(_cls_, {1}, **kw)
"""
    else:
        new_func_template = \
"""
def __new__(_cls_, {2}):
    "Create new instance: {0}({2})"
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

def _type2str(tp):
    if hasattr(tp, '__name__'):
        return tp.__name__
    else:
        return str(tp)

def _make_cls_doc(typename, fields, annotations, defaults, use_dict):

    fields2 = []
    for fn in fields:
        if fn in annotations:
            tp = annotations[fn]
            fn_txt = "%s:%s" % (fn, (tp if type(tp) is str else _type2str(tp)))            
        else:
            fn_txt = fn
        if fn in defaults:
            fn_txt += "=%r" % defaults[fn]
        fields2.append(fn_txt)
    fields2 = tuple(fields2)

    if use_dict:
        template = """{0}({1}, **kw)\n--\nCreate class {0} instance"""
    else:
        template = """{0}({1})\n--\nCreate class {0} instance"""
    doc = template.format(typename, ', '.join(fields2))

    return doc
