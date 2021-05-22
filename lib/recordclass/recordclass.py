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

from collections import namedtuple, OrderedDict
from .dataclass import make_dataclass

import sys as _sys

def recordclass(typename, fields, defaults=None, 
                rename=False, readonly=False, hashable=False, gc=False,
                use_dict=False, use_weakref=False, fast_new=False, module=None):
    """Returns a new subclass of array with named fields.

    >>> Point = recordclass('Point', 'x y')
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
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)
    """
    
    def _make(_cls, iterable):
        ob = _cls(*iterable)
        return ob
    
    _make.__doc__ = 'Make a new %s object from a sequence or iterable' % typename

    if readonly:
        def _replace(_self, **kwds):
            result = _self._make((kwds.pop(name) for name in self.__fields__))
            if kwds:
                raise ValueError('Got unexpected field names: %r' % list(kwds))
            return result
    else:
        def _replace(_self, **kwds):
            for name, val in kwds.items():
                setattr(_self, name, val)
            return _self
    
    _replace.__doc__ = 'Return a new %s object replacing specified fields with new values' % typename
    
    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values.'
        return OrderedDict(zip(self.__fields__, self))
        
    for method in (_make, _replace, _asdict,):
        method.__qualname__ = typename + "." + method.__name__        
        
    _make = classmethod(_make)        

    ns = {
            '_make': _make, 
            '_replace': _replace, 
            '_asdict': _asdict,
         }

    if module is None:
        try:
            _module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
    else:
        _module = module
    
    invalid_names = ('_make', '_replace', '_asdict')
    return make_dataclass(typename, fields, defaults=defaults, namespace=ns,
                    use_dict=use_dict, use_weakref=use_weakref, hashable=hashable, 
                    sequence=True, mapping=False, iterable=True, rename=rename, invalid_names=invalid_names,
                    readonly=readonly, module=_module, fast_new=fast_new, gc=False)
    

