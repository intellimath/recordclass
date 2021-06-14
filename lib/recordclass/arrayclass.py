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

__all__ = 'make_arrayclass', 

import sys as _sys

_intern = _sys.intern

int_type = type(1)
    
def make_arrayclass(typename, fields=0, namespace=None, 
             use_dict=False, use_weakref=False,
             hashable=False, readonly=False, gc=False,
             module=None):

    from ._dataobject import dataobject
    from .datatype import datatype
    
    if not isinstance(fields, int_type):
        raise TypeError("argument fields is not integer")
        
    bases = (dataobject,)        

    options = {
        'use_dict':use_dict, 'use_weakref':use_weakref, 'hashable':hashable, 
        'sequence':True, 'iterable':True, 'readonly':readonly, 'gc':gc,
        'fast_new':True,
    }
    
    typename = _intern(typename)

    if namespace is None:
        ns = {}
    else:
        ns = namespace

    ns['__options__'] = options
    ns['__fields__'] = fields

    if module is None:
        try:
            module = _sys._getframe(1).f_globals.get('__name__', '__main__')
        except (AttributeError, ValueError):
            pass
        
    ns['__module__'] = module
    
    cls = datatype(typename, bases, ns)

    return cls
