# coding: utf-8

# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: nonecheck=False
# cython: embedsignature=True
# cython: initializedcheck=False

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

cimport cython
from cython cimport sizeof, pointer
from libc.string cimport memset
from cpython.object cimport Py_TPFLAGS_HAVE_GC, Py_TPFLAGS_HEAPTYPE

import sys as _sys

cdef extern from "Python.h":

    ctypedef class __builtin__.object [object PyObject]:
        pass

    ctypedef class __builtin__.type [object PyTypeObject]:
        pass

    ctypedef struct PyObject:
        Py_ssize_t ob_refcnt
        PyTypeObject *ob_type

    ctypedef struct PyTupleObject:
        PyObject *ob_item[1]

    ctypedef struct PyVarObject:
        Py_ssize_t ob_refcnt
        PyTypeObject *ob_type
        Py_ssize_t ob_size

    ctypedef PyObject * (*unaryfunc)(PyObject *)
    ctypedef PyObject * (*binaryfunc)(PyObject *, PyObject *)
    ctypedef PyObject * (*ternaryfunc)(PyObject *, PyObject *, PyObject *)
    ctypedef int (*inquiry)(PyObject *) except -1
    ctypedef Py_ssize_t (*lenfunc)(PyObject *) except -1
    ctypedef PyObject *(*ssizeargfunc)(PyObject *, Py_ssize_t)
    ctypedef PyObject *(*ssizessizeargfunc)(PyObject *, Py_ssize_t, Py_ssize_t)
    ctypedef int(*ssizeobjargproc)(PyObject *, Py_ssize_t, PyObject *)
    ctypedef int(*ssizessizeobjargproc)(PyObject *, Py_ssize_t, Py_ssize_t, PyObject *)
    ctypedef int(*objobjargproc)(PyObject *, PyObject *, PyObject *)

    ctypedef Py_hash_t(*hashfunc)(PyObject *)

    ctypedef int (*objobjproc)(PyObject *, PyObject *)

    ctypedef PyObject *(*newfunc)(PyTypeObject *, PyObject *, PyObject *)
    ctypedef PyObject *(*allocfunc)(PyTypeObject *, Py_ssize_t)
    ctypedef int (*initproc)(PyObject *, PyObject *, PyObject *)

    ctypedef int (*visitproc)(PyObject *, void *) except -1
    ctypedef int (*traverseproc)(PyObject *, visitproc, void *) except -1
    ctypedef void (*freefunc)(void *)
    ctypedef void (*destructor)(PyObject *)

    ctypedef struct PySequenceMethods:
        lenfunc sq_length
        binaryfunc sq_concat
        ssizeargfunc sq_repeat
        ssizeargfunc sq_item
        void *was_sq_slice
        ssizeobjargproc sq_ass_item
        void *was_sq_ass_slice
        objobjproc sq_contains

        binaryfunc sq_inplace_concat
        ssizeargfunc sq_inplace_repeat

    ctypedef struct PyMappingMethods:
        lenfunc mp_length
        binaryfunc mp_subscript
        objobjargproc mp_ass_subscript

    ctypedef struct PyTypeObject:
        Py_ssize_t tp_basicsize
        Py_ssize_t tp_itemsize
        Py_ssize_t tp_dictoffset
        Py_ssize_t tp_weaklistoffset
        unsigned long tp_flags

        PyTypeObject *tp_base
        PyObject *tp_bases
        PyObject *tp_mro

        destructor tp_dealloc

        newfunc tp_new
        allocfunc tp_alloc
        initproc tp_init
        freefunc tp_free
        traverseproc tp_traverse
        inquiry tp_clear
        hashfunc tp_hash

        PySequenceMethods *tp_as_sequence
        PyMappingMethods *tp_as_mapping

        inquiry tp_is_gc

    ctypedef struct PyHeapTypeObject:
        PyTypeObject ht_type
        PyObject *ht_name
        PyObject *ht_fields
        PyObject *ht_qualname

    cdef inline PyTypeObject* Py_TYPE(PyObject*)

    cdef inline void Py_INCREF(PyObject*)
    cdef inline void Py_DECREF(PyObject*)
    cdef inline void Py_XDECREF(PyObject*)

    cdef Py_ssize_t PyNumber_AsSsize_t(PyObject*, PyObject*) except? -1

    cdef PyObject* PyErr_Occurred()
    cdef PyObject* PyExc_IndexError
    cdef PyObject* PyExc_TypeError
    cdef void PyErr_SetString(PyObject*, char*)

    cdef PyObject* Py_None

    cdef PyTypeObject PyTuple_Type
    cdef inline void PyTuple_SET_ITEM(PyObject*, Py_ssize_t, PyObject*)
    cdef inline PyObject* PyTuple_GET_ITEM(PyObject*, Py_ssize_t)
    cdef PyObject* PyTuple_New(Py_ssize_t)

    cdef void PyType_Modified(PyTypeObject*)
    cdef bint PyType_IS_GC(PyTypeObject *o)
    cdef int PyType_Ready(PyTypeObject*)

    cdef void* PyObject_Malloc(size_t size)  

    cdef long PyObject_Hash(PyObject*)

    cdef Py_ssize_t Py_SIZE(PyObject*)
    cdef void Py_CLEAR(PyObject*)

    cdef PyObject* _PyObject_GC_New(PyTypeObject*)
    cdef PyObject* PyObject_New(PyTypeObject*)
    cdef PyObject* _PyObject_GC_Malloc(size_t size)

    cdef void PyObject_INIT(PyObject *op, PyTypeObject *tp) 

    cdef PyObject* PyErr_NoMemory() except NULL

    cdef void PyObject_GC_Track(PyObject*)
    cdef void PyObject_GC_UnTrack(PyObject*)
    cdef void PyObject_GC_Del(void*)
    cdef void PyObject_Del(void*)

# cdef extern from "objimpl.h":
#     cdef void Py_VISIT(PyObject*)

cdef extern from *:
    """
    #define C_DIV(a,b) ((a)/(b))

    #define recordobject_items(op) ((PyObject**)((char*)(op) + sizeof(PyObject)))
    #define recordobject_dictptr(op, tp) ((PyObject**)((char*)(op) + tp->tp_dictoffset))
    #define recordobject_weaklistptr(op, tp) ((PyObject**)((char*)op + tp->tp_weaklistoffset))
    #define recordobject_hasdict(op) ((Py_TYPE((PyObject*)(op)))->tp_dictoffset != 0)
    #define recordobject_hasweaklist(op) ((Py_TYPE((PyObject*)(op)))->tp_weaklistoffset != 0)
    """
    cdef inline Py_ssize_t C_DIV(Py_ssize_t, Py_ssize_t)
    cdef inline PyObject** recordobject_items(PyObject*)
    cdef inline PyObject** recordobject_dictptr(PyObject*, PyTypeObject*)
    cdef inline PyObject** recordobject_weaklistptr(PyObject*, PyTypeObject*)
    cdef inline bint recordobject_hasdict(PyObject *op)
    cdef inline bint recordobject_hasweaklist(PyObject *op)

from cpython.object cimport Py_TPFLAGS_HAVE_GC, Py_TPFLAGS_READY

cdef Py_hash_t recordclass_hash(PyObject *v):
    cdef long x, y
    cdef Py_ssize_t len = Py_SIZE(v) - 1
    cdef PyObject *temp
    cdef long mult = 1000003L

    x = 0x345678L
    p = (<PyTupleObject*>v).ob_item
    while len >= 0:
        temp = PyTuple_GET_ITEM(v, len)
        Py_INCREF(temp)
        y = PyObject_Hash(temp)
        Py_DECREF(temp)
        if y == -1:
            return -1
        x = (x ^ y) * mult
        mult += (long)(82520L + len + len)
        len -= 1

    x += 97531L
    if x == -1:
        x = -2
    return <Py_hash_t>x

class recordclasstype(type):
    #
    def __new__(tp, name, bases, ns):
        cdef PyTypeObject *tp_cls "tp_cls"
#         cdef PyTypeObject *tp_base "tp_base";
        cdef object options "options"
        cdef bint gc "gc"
        cdef bint hashable "hashable"

        options = ns.pop('__options__', {})
        hashable = options.get('hashable', False)

        if 'gc' in options:
            gc = options.get('gc')
        else:
            gc = 0

        cls = type.__new__(tp, name, bases, ns)
        tp_cls = <PyTypeObject*>cls
#         tp_base = tp_cls->tp_base

        if gc:
            if not tp_cls.tp_flags & Py_TPFLAGS_HAVE_GC:
                tp_cls.tp_flags |= Py_TPFLAGS_HAVE_GC
        else:
            if tp_cls.tp_flags & Py_TPFLAGS_HAVE_GC:
                tp_cls.tp_flags ^= Py_TPFLAGS_HAVE_GC
            tp_cls.tp_free = PyObject_Del
            tp_cls.tp_is_gc = NULL
            tp_cls.tp_clear = NULL
            tp_cls.tp_traverse = NULL
            
        

#         if not getattr(cls, '__hash__', None) or tp_cls.tp_hash != NULL:
#             if hashable:
#                 tp_cls.tp_hash = recordclass_hash
#             else:
#                 tp_cls.tp_hash = NULL

        module = ns.get('__module__', None)
            
        if module is None:
            try:
                cls.__module__ = _sys._getframe(2).f_globals.get('__name__', '__main__')
            except (AttributeError, ValueError):
                pass
        else:
            pass

        return cls

@cython.final
cdef public class SequenceProxy[object SequenceProxyObject, type SequenceProxyType]:
    cdef object ob "ob"
    cdef Py_hash_t hash "hash"

    @property
    def obj(self):
        return self.ob

    def __init__(self, ob):
        self.ob = ob
        self.hash = 0

    def __getitem__(self, ind):
        return self.ob.__getitem__(ind)

    def __len__(self):
        return self.ob.__len__()

    def __hash__(self):
        if self.hash == 0:
            self.hash = hash(tuple(self.ob))
        return self.hash

    def __richcmp__(self, other, flag):
        return self.ob.__richcmp__(other, flag)

    def __iter__(self):
        return iter(self.ob)

    def __repr__(self):
        return "sequenceproxy(" + repr(self.ob) + ")"

def sequenceproxy(ob):
    return SequenceProxy(ob)
