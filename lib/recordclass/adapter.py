# coding: utf-8

# The MIT License (MIT)

# Copyright (c) «2021-2023» «Shibzukhov Zaur, szport at gmail dot com»

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

def as_dataclass(*, use_dict=False, use_weakref=False, hashable=False,
                    sequence=False, mapping=False, iterable=False, readonly=False,
                    module=None, fast_new=True, rename=False, gc=False):

    """Returns a new dataobject-based class with named fields, smaller memory footprint and 
    faster instance creation.
    
        @as_dataclass()
        class Point:
            x:int
            y:int
    """
    def _adapter(cls, use_dict=use_dict, use_weakref=use_weakref, hashable=hashable,
                      sequence=sequence, mapping=mapping, iterable=iterable, readonly=readonly,
                      fast_new=fast_new, rename=rename, gc=gc):
        from ._dataobject import dataobject
        from .datatype import datatype
        from sys import intern as _intern
        
        ns = {}
        if '__fields__' not in cls.__dict__:
            ns['__fields__'] = tuple(cls.__dict__.get('__annotations__', ()))
            
        ns['__annotations__'] = cls.__dict__.get('__annotations__', {})

        if sequence or mapping:
            iterable = True

        if '__iter__' in ns:
            iterable = True

        if readonly:
            hashable = True
        
        for k,v in cls.__dict__.items():
            if not k.startswith("___"):
                ns[k] = v
        
        typename = cls.__name__

        new_cls = datatype(typename, (dataobject,), ns, 
                       gc=gc, fast_new=fast_new, readonly=readonly, iterable=iterable,
                       mapping=mapping, sequence=sequence, use_dict=use_dict, 
                       use_weakref=use_weakref, hashable=hashable)

        return new_cls
    return _adapter
