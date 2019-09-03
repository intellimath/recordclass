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

from keyword import iskeyword as _iskeyword
from collections import namedtuple, OrderedDict
from .recordobject import recordobject, structclasstype

import sys as _sys
_PY3 = _sys.version_info[0] >= 3

if _PY3:
    _intern = _sys.intern
    def _isidentifier(s):
        return s.isidentifier()
    if _sys.version_info[1] >= 6:
        from typing import _type_check
    else:
        _type_check = None
else:
    from __builtin__ import intern as _intern
    import re as _re
    def _isidentifier(s):
        return _re.match(r'^[a-z_][a-z0-9_]*$', s, _re.I) is not None
    _type_check = None

_repr_template = '{name}=%r'


def structclass(typename, fields, rename=False, defaults=None, 
                readonly=False, usedict=False, gc=False, weakref=False,
                hashable=False, assequence=True, module=None):
    """Returns a new subclass of array with named fields.

    >>> Point = structclass('Point', 'x y')
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessable by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d.x
    11
    >>> d.x = 33                        # assign new value
    >>> Point(**d)                      # convert from a dictionary
    Point(x=33, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)
    """

    if isinstance(fields, str):
        field_names = fields.replace(',', ' ').split()
        annotations = None
    else:
        msg = "recordclass('Name', [(f0, t0), (f1, t1), ...]); each t must be a type"
        annotations = {}
        field_names = []
        for fn in fields:
            if type(fn) is tuple:
                n, t = fn
                n = str(n)
                if _type_check:
                    t = _type_check(t, msg)
                annotations[n] = t
                field_names.append(n)
            else:
                field_names.append(str(fn))
    typename = _intern(str(typename))
    if rename:
        seen = set()
        for index, name in enumerate(field_names):
            if (not _isidentifier(name)
                or _iskeyword(name)
                or name.startswith('_')
                or name in seen):
                field_names[index] = '_%d' % index
            seen.add(name)

    for name in [typename] + field_names:
        if type(name) != str:
            raise TypeError('Type names and field names must be strings')
        if not _isidentifier(name):
            raise ValueError('Type names and field names must be valid '
                             'identifiers: %r' % name)
        if _iskeyword(name):
            raise ValueError('Type names and field names cannot be a '
                             'keyword: %r' % name)
    seen = set()
    for name in field_names:
        if name.startswith('_') and not rename:
            raise ValueError('Field names cannot start with an underscore: '
                             '%r' % name)
        if name in seen:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen.add(name)

    if defaults is not None:
        defaults = tuple(defaults)
        if len(defaults) > len(field_names):
            raise TypeError('Got more default values than field names')

    field_names = tuple(map(_intern, field_names))
    n_fields = len(field_names)
    arg_list = ', '.join(field_names)
    repr_fmt=', '.join(_repr_template.format(name=name) for name in field_names)

    if usedict:
        new_func_template = """\
def __new__(_cls, {1}, **kw):
    'Create new instance of {0}({1})'
    return _baseclass.__new__(_cls, {1}, **kw)
""" 
    else:
        new_func_template = """\
def __new__(_cls, {1}):
    'Create new instance of {0}({1})'
    return _baseclass.__new__(_cls, {1})
""" 
    new_func_def = new_func_template.format(typename, arg_list)
    
    #print(new_func_def)
        
    namespace = dict(_baseclass=recordobject)    
    code = compile(new_func_def, "", "exec")
    eval(code, namespace)
    
    __new__ = namespace['__new__']
    if defaults is not None:
        __new__.__defaults__ = defaults
    
    #@classmethod
    def _make(_cls, iterable):
        ob = _cls(*iterable)
        if len(ob) != n_fields:
            raise TypeError('Expected %s arguments, got %s' % (n_fields, len(ob)))
        return ob
    
    _make.__doc__ = 'Make a new %s object from a sequence or iterable' % typename

    def _replace(_self, **kwds):
        for name, val in kwds.items():
            setattr(_self, name, val)
        return _self
    
    _replace.__doc__ = 'Return a new %s object replacing specified fields with new values' % typename

    def __repr__(self):
        'Return a nicely formatted representation string'
        args_text = repr_fmt % tuple(self)
        try:
            kw = self.__dict__
        except AttributeError:
            kw = None
        if kw:
            kw_text = repr(kw)
            return self.__class__.__name__ + "(" + args_text + ", **" + kw_text + ")" 
        else:
            return self.__class__.__name__ + "(" + args_text + ")" 
    
    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values.'
        return OrderedDict(zip(self.__fields__, self))
        
    for method in (__new__, _make, _replace, __repr__, _asdict,):
        method.__qualname__ = typename + "." + method.__name__        
        
    _make = classmethod(_make)

    __options__ = {'readonly':readonly, 'usedict':usedict, 'gc':gc, 'weakref':weakref, 
                   'hashable':hashable, 'assequence':assequence}
    
    class_namespace = {
        '__doc__': typename+'('+arg_list+')',
        '__fields__': field_names,
        '__new__': __new__,
        '_make': _make,
        '_replace': _replace,
        '__repr__': __repr__,
        '_asdict': _asdict,
        '__options__': __options__,
    }
        
    _result = structclasstype(typename, (recordobject,), class_namespace)
    
    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the class is created. 
    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
    if module is not None:
        _result.__module__ = module    
    if annotations:
        _result.__annotations__ = annotations

    return _result

def join_classes(name, classes, readonly=False, usedict=False, gc=False, 
                 weakref=False, hashable=False, assequence=True, module=None):
    if not all((cls.__bases__ == (recordobject,)) for cls in classes):
        raise TypeError('All arguments should be child of dataobject')
    if not all(hasattr(cls, '__fields__') for cls in classes):
        raise TypeError('Some of the base classes has not __fields__')

    _attrs = []
    for cls in classes:
        for a in cls.__fields__:
            if a in _attrs:
                raise AttributeError('Duplicate attribute in the base classes')
            _attrs.append(a)

    return structclass(name, _attrs, 
                       readonly=readonly, usedict=usedict, gc=gc, weakref=weakref, 
                       hashable=False, assequence=True, module=module)
