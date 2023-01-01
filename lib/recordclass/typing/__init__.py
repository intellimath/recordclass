# The MIT License (MIT)

# Copyright (c) «2015-2022» «Shibzukhov Zaur, szport at gmail dot com»

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

from recordclass.datatype import datatype
from recordclass._dataobject import dataobject
from recordclass.recordclass import _add_namedtuple_api

class recordclassmeta(datatype):
    
    def __new__(metatype, typename, bases, ns, *,
                gc=False, fast_new=True, readonly=False, 
                use_dict=False, use_weakref=False, hashable=False):
        
        ns.update(_add_namedtuple_api(typename, readonly))
        
        if readonly:
            hashable = True
        
        return datatype.__new__(metatype, typename, bases, ns,
                    gc=gc, fast_new=fast_new, readonly=readonly, iterable=True,
                    sequence=True, use_dict=use_dict, use_weakref=use_weakref, hashable=hashable)
    
class RecordClass(dataobject, metaclass=recordclassmeta):
    pass



__all__ = 'RecordClass',

