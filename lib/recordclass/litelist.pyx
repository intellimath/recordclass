# coding: utf-8

# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: nonecheck=False
# cython: embedsignature=True
# cython: initializedcheck=False
 
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

cimport cython

from cpython.object cimport PyObject, PyTypeObject, Py_TYPE
from cpython.sequence cimport PySequence_Fast, PySequence_Fast_GET_ITEM, PySequence_Fast_GET_SIZE
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from cpython.mem cimport PyObject_Malloc, PyObject_Realloc, PyObject_Free
from cpython.slice cimport PySlice_Check, PySlice_GetIndices

cdef extern from "Python.h":
    cdef inline void Py_XDECREF(PyObject*)
    cdef inline void Py_DECREF(PyObject*)
    cdef inline void Py_INCREF(PyObject*)
    cdef inline void Py_XINCREF(PyObject*)
    cdef inline Py_ssize_t Py_SIZE(PyObject*)

cdef inline Py_ssize_t resize(Py_ssize_t size):
    if size < 9:
        return size + (size // 8) + 3
    else:
        return size + (size // 8) + 6

cdef litelist make_empty(Py_ssize_t size):
    cdef litelist op = litelist.__new__(litelist, ())
    cdef Py_ssize_t i
    
    op.items = <PyObject**>PyObject_Malloc(size*sizeof(PyObject*))
    op.size = op.allocated = size
    for i in range(size):
        op.items[i] = NULL
        
    return <litelist>op
    
@cython.no_gc
cdef public class litelist[object PyLiteListObject, type PyLiteListType]:
    cdef Py_ssize_t size
    cdef Py_ssize_t allocated
    cdef PyObject **items
    
    def __cinit__(self, args):
        cdef Py_ssize_t i, size
        cdef PyObject *v

        if args:
            tpl = PySequence_Fast(args, "Invalid arguments")
            size = PySequence_Fast_GET_SIZE(tpl)
            self.items = <PyObject**>PyObject_Malloc(size*sizeof(PyObject*))
            self.size = self.allocated = size
            for i in range(size):
                v = PySequence_Fast_GET_ITEM(tpl, i)
                Py_INCREF(v)
                self.items[i] = v
        else:
            self.items = NULL
            self.size = self.allocated = 0
        

    cdef object get_slice(self, Py_ssize_t i, Py_ssize_t n):
        cdef litelist op = make_empty(n)
        cdef Py_ssize_t j
        
        for j in range(n):
            op.items[j] = self.items[i+j]
            
        return op
            
    cdef object set_slice(self, Py_ssize_t i, Py_ssize_t n, vals):
        cdef Py_ssize_t j
            
        tpl = PySequence_Fast(vals, "Invalid arguments")
        size = Py_SIZE(<PyObject*>tpl)
        
        if n != Py_SIZE(<PyObject*>tpl):
            raise ValueError("incompatible range of indexes")
        
        for j in range(n):
            v = PySequence_Fast_GET_ITEM(tpl, j)
            Py_INCREF(v)
            u = self.items[i+j]
            Py_XDECREF(u)
            self.items[i+j] = v
            
    def __getitem__(self, index):
        cdef Py_ssize_t i
        cdef Py_ssize_t size = self.size
        cdef Py_ssize_t start, stop, step
        
        if PySlice_Check(index):
            if PySlice_GetIndices(index, self.size, &start, &stop, &step) < 0:
                raise IndexError("Invalid slice")
            return self.get_slice(start, stop-start)
        else:
            i = index
            if i < 0:
                i += size
            if i < 0 or i >= size:
                raise IndexError('%s' % index)
        return <object>(self.items[i])

    def __setitem__(self, index, val):
        cdef Py_ssize_t i
        cdef Py_ssize_t size = self.size
        cdef Py_ssize_t start, stop, step

        if PySlice_Check(index):
            if PySlice_GetIndices(index, self.size, &start, &stop, &step) < 0:
                raise IndexError("Invalid slice")
            self.set_slice(start, stop-start, val)
        else:
            i = index
            if i < 0:
                i += size
            if i < 0 or i >= size:
                raise IndexError('%s' % index)

            Py_INCREF(<PyObject*>val)
            self.items[i] = <PyObject*>val

    def __delitem__(self, index):
        cdef Py_ssize_t i = index
        cdef Py_ssize_t size = self.size
        cdef PyObject **items = self.items
        
        if i < 0:
            i += size
        if i < 0 or i >= size:
            raise IndexError('%s' % index)
 
        Py_DECREF(items[i])
        size -= 1
        self.size = size
        while i < size:
            items[i] = items[i+1]
            i += 1

        if size + size < self.allocated:
            newsize = size + (size // 8)
            self.items = <PyObject**>PyObject_Realloc(self.items, newsize*sizeof(PyObject*))
            self.allocated = newsize

    def __repr__(self):
        cdef Py_ssize_t i
        cdef Py_ssize_t size = self.size
        cdef list temp
        
        if size == 0:
            return "litelist([])"
        
        temp = []
        for i in range(size):
            val = <object>self.items[i]
            temp.append(repr(val))
            
        return "litelist([" + ", ".join(temp) + "])"
    
    def __reduce__(self):
        return self.__class__, (tuple(self),)

    def append(self, val):
        cdef Py_ssize_t i, newsize, size = self.size

        if size == self.allocated:
            newsize = resize(size+1)
            self.items = <PyObject**>PyObject_Realloc(self.items, newsize*sizeof(PyObject*))
            self.allocated = newsize
        
        Py_INCREF(<PyObject*>val)
        self.items[self.size] = <PyObject*>val
        self.size += 1

    def remove(self, ob):
        cdef Py_ssize_t i, size = self.size
        cdef PyObject **items = self.items

        i = 0
        while i < size:
            if items[i] == <PyObject*>ob:
                break
            i += 1
            
        if i == size:
            return 

        Py_DECREF(items[i])
        size -= 1
        self.size = size
        while i < size:
            items[i] = items[i+1]
            i += 1

    def extend(self, vals):
        cdef Py_ssize_t i, newsize, size = self.size
        cdef Py_ssize_t n=len(vals)
        cdef Py_ssize_t size_n = size + n

        if size_n > self.allocated:
            newsize = resize(size_n)

            self.items = <PyObject**>PyObject_Realloc(self.items, newsize*sizeof(PyObject*))
            self.allocated = newsize

        i = size
        for val in vals:
            Py_INCREF(<PyObject*>val)
            self.items[i] = <PyObject*>val
            i += 1
        self.size += n
       
    def trim(self):
        cdef Py_ssize_t size = self.size

        self.items = <PyObject**>PyObject_Realloc(self.items, size*sizeof(PyObject*))
        self.allocated = size
            
    def __len__(self):
        return self.size
    
    def __sizeof__(self):
        return sizeof(litelist) + sizeof(PyObject*) * self.allocated
    
    def __nonzero__(self):
        return self.size > 0
    
    def __iter__(self):
        return litelistiter(self)
    
    def __dealloc__(self):
        cdef Py_ssize_t i, size = self.size
        for i in range(size):
            Py_XDECREF(self.items[i])
            self.items[i] = NULL
        PyObject_Free(self.items)

cdef class litelistiter:
    cdef litelist op
    cdef Py_ssize_t i
    
    def __init__(self, litelist op):
        self.op = op
        self.i = 0
        
    def __next__(self):
        if self.i < self.op.size:
            v = self.op[self.i]
            self.i += 1
            return v
        else:
            raise StopIteration
            
    def __iter__(self):
        return self
        