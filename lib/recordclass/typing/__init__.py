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

import collections
from recordclass import recordclass #, dataobject, clsconfig
from typing import _type_check

__all__ = 'RecordClass',

# @clsconfig(sequence=True)
# class RecordClass(dataobject):

#     def _make(_cls, iterable):
#         ob = _cls(*iterable)
#         return ob

#     _make.__doc__ = 'Make a new object from a sequence or iterable'

#     if readonly:
#         def _replace(_self, **kwds):
#             result = _self._make(map(kwds.pop, _self.__fields__, _self))
#             if kwds:
#                 kwnames = tuple(kwds)
#                 raise AttributeError(f'Got unexpected field names: {kwnames}')
#             return result
#     else:
#         def _replace(_self, **kwds):
#             for name, val in kwds.items():
#                 setattr(_self, name, val)
#             return _self

#     _replace.__doc__ = 'Return a new object replacing specified fields with new values'

#     def _asdict(self):
#         'Return a new dict which maps field names to their values.'
#         return asdict(self)

#     _make = classmethod(_make)


import sys as _sys

_excluded = ('__new__', '__init__', '__slots__', '__getnewargs__',
             '__fields__', '_field_defaults', '_field_types',
             '_make', '_replace', '_asdict', '_source')

_special = ('__module__', '__name__', '__qualname__', '__annotations__')

def _make_recordclass(name, types, readonly=False, hashable=False):
    msg = "RecordClass('Name', [(f0, t0), (f1, t1), ...]); each t must be a type"
    types = [(n, _type_check(t, msg)) for n, t in types]
    
    module = None
    try:
        module = _sys._getframe(2).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass
    
    rec_cls = recordclass(name, [n for n, t in types], readonly=readonly, hashable=hashable, module=module)
    rec_cls.__annotations__ = dict(types)
    return rec_cls

class RecordClassMeta(type):
    def __new__(cls, typename, bases, ns):
        if ns.get('_root', False):
            return super().__new__(cls, typename, bases, ns)
        types = ns.get('__annotations__', {})

        options = ns.pop('__options__', {})
        readonly = options.get('readonly', False)
        hashable = options.get('hashable', False)

        if readonly and not hashable:
            hashable = True

        defaults = []
        defaults_dict = {}
        for field_name in types:
            if field_name in ns:
                default_value = ns[field_name]
                defaults.append(default_value)
                defaults_dict[field_name] = default_value
            elif defaults:
                raise TypeError("Non-default recordclass field {field_name} cannot "
                                "follow default field(s) {default_names}"
                                .format(field_name=field_name,
                                        default_names=', '.join(defaults_dict.keys())))

        rec_cls = _make_recordclass(typename, types.items(), readonly=readonly, hashable=hashable)
        rec_cls.__annotations__ = dict(types)

        rec_cls.__new__.__defaults__ = tuple(defaults)
        rec_cls.__new__.__annotations__ = collections.OrderedDict(types)
        # update from user namespace without overriding special recordclass attributes
        for name in ns:
            if name in _excluded:
                raise AttributeError("Cannot overwrite RecordClass attribute " + name)
            elif name not in _special and name not in rec_cls.__fields__:
                setattr(rec_cls, name, ns[name])

        return rec_cls


class RecordClass(metaclass=RecordClassMeta):
    _root = True

    def __new__(cls, typename, fields=None, **kwargs):
        if fields is None:
            fields = kwargs.items()
        elif kwargs:
            raise TypeError("Either list of fields or keywords"
                            " can be provided to RecordClass, not both")
        return _make_recordclass(typename, fields)
# 