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
from cython cimport sizeof, pointer
from libc.string cimport memset
from cpython.object cimport Py_TPFLAGS_HAVE_GC, Py_TPFLAGS_HEAPTYPE

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

cdef inline int py_visit(PyObject *ob, visitproc visit, void *arg) except -1:
    cdef int vret
    if ob:
        vret = visit(ob, arg)
        if vret:
            return vret
    return 0

cdef PyObject* recordobject_alloc "recordobject_alloc"(PyTypeObject *tp, Py_ssize_t n):
    cdef PyObject *op "op"
    cdef Py_ssize_t size "size" = tp.tp_basicsize
    cdef bint is_gc "is_gc"

    is_gc = PyType_IS_GC(tp)
    if is_gc:
        op = _PyObject_GC_Malloc(size)
    else:
        op = <PyObject*>PyObject_Malloc(size)

    if op == NULL:
        return PyErr_NoMemory()

    memset(op, 0, size)

    if tp.tp_flags & Py_TPFLAGS_HEAPTYPE:
        Py_INCREF(<PyObject*>tp)

    PyObject_INIT(op, tp)

    if is_gc:
        PyObject_GC_Track(op)

    return op

cdef void recordobject_free "recordobject_free"(void *op):
    if PyType_IS_GC(Py_TYPE(<PyObject*>op)):
        PyObject_GC_UnTrack(<PyObject*>op)
        PyObject_GC_Del(<PyObject*>op)
    else:
        PyObject_Del(<PyObject*>op)

cdef inline Py_ssize_t recordobject_len "recordobject_len"(PyObject *op):
    cdef PyTypeObject *tp = Py_TYPE(op)
    cdef Py_ssize_t size

    size = C_DIV(tp.tp_basicsize - sizeof(PyObject), sizeof(PyObject*))
    if tp.tp_dictoffset != 0:
        size -= 1
    if tp.tp_weaklistoffset != 0:
        size -= 1

    return size

cdef inline PyObject* recordobject_item "recordobject_item"(PyObject *op, Py_ssize_t i):
    cdef Py_ssize_t n
    cdef PyObject* val
    cdef PyObject **items

    n = recordobject_len(op)
    items = recordobject_items(op)

    if i < 0:
        i += n
    if i < 0 or i >= n:
        PyErr_SetString(PyExc_IndexError, "index out of range")
        return NULL

    val = items[i]
    Py_INCREF(val)
    return val

cdef inline int recordobject_ass_item "recordobject_ass_item"(PyObject *op, Py_ssize_t i, PyObject *val):
    cdef Py_ssize_t n
    cdef PyObject **items

    n = recordobject_len(op)
    items = recordobject_items(op)

    if i < 0:
        i += n
    if i < 0 or i >= n:
        PyErr_SetString(PyExc_IndexError, "index out of range")
        return 0

    Py_INCREF(val)
    items[i] = val
    return 0

cdef inline PyObject* recordobject_subscript "recordobject_subscript"(PyObject *op, PyObject *ind):
    cdef PyObject *val
    cdef Py_ssize_t i, n
    cdef PyObject **items

    n = recordobject_len(op)
    items = recordobject_items(op)

    i = PyNumber_AsSsize_t(ind, <PyObject*>PyExc_IndexError)
    if i < 0:
        i += n
    if i >= n or i < 0:
        PyErr_SetString(PyExc_IndexError, "index out of range")
        return NULL        

    val = items[i]
    Py_INCREF(val)
    return val

cdef inline int recordobject_ass_subscript "recordobject_ass_subscript"(PyObject *op, PyObject *ind, PyObject *val):
    cdef Py_ssize_t i "i", n "n"
    cdef PyObject **items "items"

    n = recordobject_len(op)
    items = recordobject_items(op)

    i = PyNumber_AsSsize_t(ind, <PyObject*>PyExc_IndexError)
    if i < 0:
        i += n
    if i >= n or i < 0:
        PyErr_SetString(PyExc_IndexError, "index out of range")
        return 0

    Py_INCREF(val)
    items[i] = val
    return 0

cdef inline int recordobject_clear "recordobject_clear"(PyObject *op) except -1:
    cdef PyObject **items "items"
    cdef PyObject **temp "temp"
    cdef PyObject *ob "ob"
    cdef PyTypeObject *tp "tp" = Py_TYPE(op)
    cdef Py_ssize_t i "i", n "n"

    n = recordobject_len(op)
    items = recordobject_items(op)    

    for i in range(n):
        ob = items[i]
        Py_XDECREF(ob)
        Py_INCREF(Py_None)
        items[i] = Py_None

    if tp.tp_dictoffset != 0:
        temp = recordobject_dictptr(op, tp)
        ob = temp[0]
        if ob:
            (<dict>ob).clear()
        Py_XDECREF(ob)
        temp[0] = Py_None
        Py_INCREF(Py_None)
    if tp.tp_weaklistoffset != 0:
        temp = recordobject_weaklistptr(op, tp)
        ob = temp[0]
        Py_XDECREF(ob)
        temp[0] = Py_None
        Py_INCREF(Py_None)

    return 0

cdef inline int recordobject_traverse "recordobject_traverse"(PyObject *op, visitproc visit, void *arg) except -1:
    cdef PyTypeObject *tp "tp" = Py_TYPE(op)
    cdef PyObject **items "items"
    cdef PyObject **temp "temp"
    cdef PyObject *ob "ob"
    cdef PyObject *v "v"
    cdef Py_ssize_t i "i", n "n"
    cdef int vret "vret"

    n = recordobject_len(op)

    items = recordobject_items(op)    

    for i in range(n):
        ob = items[i]
        if ob:
            vret = visit(ob, arg)
            if vret:
                return vret

    if tp.tp_dictoffset != 0:
        temp = recordobject_dictptr(op, tp)
        if temp[0]:
            obj = <object>temp[0]
            for key in obj:
                v = <PyObject*>obj[key]
                if v:
                    vret = visit(v, arg)
                    if vret:
                        return vret

    if tp.tp_weaklistoffset != 0:
        temp = recordobject_weaklistptr(op, tp)
        ob = temp[0]
        if ob:
            vret = visit(ob, arg)
            if vret:
                return vret

    return 0

cdef inline Py_hash_t recordobject_hash "recordobject_hash"(PyObject *op):
    t = tuple(<object>op)
    return <Py_hash_t>PyObject_Hash(<PyObject*>t)

@cython.auto_pickle(False)
cdef public class recordobject[object recordobject, type recordobjectType]:

    def __cinit__(self, *args, **kw):
        cdef PyObject *op "op"=<PyObject*>self
        cdef PyObject **items "items"
        cdef PyTypeObject *tp "tp" = Py_TYPE(op)
        cdef PyObject **dictptr "dictptr"
        cdef PyObject *v "v"
        cdef Py_ssize_t i "i", n "n"
        cdef tuple t "t"
        cdef dict vv "vv"

        n = recordobject_len(op)
        items = recordobject_items(op)

        if Py_TYPE(<PyObject*>args) == &PyTuple_Type:
            t = args
        else:
            t = tuple(args)

        if n != Py_SIZE(<PyObject*>t):
            raise TypeError("Invalid length of args")

        if n:
            for i in range(n):
                v = PyTuple_GET_ITEM(<PyObject*>t, i)
                Py_INCREF(v)
                items[i] = v

        if tp.tp_dictoffset:
            dictptr = recordobject_dictptr(op, tp)
            vv = {}
            if kw:
                vv.update(kw)
            Py_INCREF(<PyObject*>vv)
            dictptr[0] = <PyObject*>vv

    def __dealloc__(self):
        cdef PyObject* op "op" = <PyObject*>self
        cdef PyTypeObject *tp "tp" = Py_TYPE(op)
        cdef PyObject **items "items"
        cdef PyObject *v "v"
        cdef Py_ssize_t i "i", n "n"

        n = recordobject_len(op)

        if n > 0:
            items = recordobject_items(op)    
            for i in range(0,n):
                Py_CLEAR(items[i])

        if tp.tp_dictoffset:
            dictptr = recordobject_dictptr(op, tp)
            v = dictptr[0]
            (<dict>v).clear()
            Py_XDECREF(<PyObject*>v)
            dictptr[0] = NULL

    def __len__(ob):
        return recordobject_len(<PyObject*>ob)

    def __nonzero__(self):
        if recordobject_len(<PyObject*>self):
            return True
        if recordobject_hasdict(<PyObject*>self):
            return bool(self.__dict__)
        return False

    def __richcmp__(self, other, int flag):
        cdef Py_ssize_t i "i", n_self "n_self", n_other "n_other"
        cdef object v_self "v_self", v_other "v_other"

        n_self = len(self)
        n_other = len(other)

        if not isinstance(other, recordobject):
            raise TypeError("Types are not comparable")

        if flag == 2: # ==
            if n_self != n_other:
                return False
            for i in range(n_self):
                v_self = <object>recordobject_item(<PyObject*>self, i)
                v_other = <object>recordobject_item(<PyObject*>other, i)
                if v_self != v_other:
                    return False
            if recordobject_hasdict(<PyObject*>self):
                return self.__dict__ == other.__dict__
            else:
                return True
        elif flag == 3: # !=
            if n_self != n_other:
                return True
            for i in range(n_self):
                v_self = <object>recordobject_item(<PyObject*>self, i)
                v_other = <object>recordobject_item(<PyObject*>other, i)
                if v_self != v_other:
                    return True
            if recordobject_hasdict(<PyObject*>self):
                return self.__dict__ != other.__dict__
            else:
                return False
        else:
            raise TypeError('The type support only != and ==')

    def __iter__(self):
        return recordobjectiter(self)

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'
        if recordobject_hasdict(<PyObject*>self):
            return self.__dict__
        else:
            return None

    def __setstate__(self, state):
        'Update __dict__ if that exists' 
        if recordobject_hasdict(<PyObject*>self):
            self.__dict__.update(state)

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    def __reduce__(self):
        'Reduce'
        if recordobject_hasdict(<PyObject*>self):
            return type(self), tuple(self), self.__dict__
        else:
            return type(self), tuple(self)

    def __copy__(self):
        cdef object args "args"
        cdef object ob "ob"

        args = tuple(self)
        ob = self.__class__(*args)
        if recordobject_hasdict(<PyObject*>self):
            ob.__dict__.update(self.__dict__)
        return ob

cdef _type_configure_basic "_type_configure_basic"(ob, n, 
            usedict=False, gc=False, weakref=False, hashable=False):
    cdef PyTypeObject *tp "tp" = <PyTypeObject*>ob;
    cdef Py_ssize_t size "size" = PyNumber_AsSsize_t(<PyObject*>n, <PyObject*>PyExc_IndexError)

    tp.tp_basicsize = size * sizeof(PyObject*) + sizeof(PyObject)
    tp.tp_itemsize = 0

    if tp.tp_bases:
        all_AC = all(c is recordobject for c in <object>tp.tp_bases)
    else:
        all_AC = False

    tp.tp_dictoffset = 0
    if usedict or not all_AC:
        tp.tp_dictoffset = tp.tp_basicsize
        tp.tp_basicsize += sizeof(PyObject*)

    tp.tp_weaklistoffset = 0
    if weakref:
        tp.tp_weaklistoffset = tp.tp_basicsize
        tp.tp_basicsize += sizeof(PyObject*)

    if gc:
        if not tp.tp_flags & Py_TPFLAGS_HAVE_GC:
            tp.tp_flags |= Py_TPFLAGS_HAVE_GC
    else:
        if tp.tp_flags & Py_TPFLAGS_HAVE_GC:
            tp.tp_flags ^= Py_TPFLAGS_HAVE_GC

    if hashable:
        tp.tp_hash = recordobject_hash
    else:
        tp.tp_hash = NULL

    tp.tp_alloc = recordobject_alloc
    #tp.tp_new = recordobject_new

    if gc:
        tp.tp_traverse = recordobject_traverse
        tp.tp_clear = recordobject_clear
    else:
        tp.tp_traverse = NULL
        tp.tp_clear = NULL

    #tp.tp_dealloc = recordobject_dealloc
    tp.tp_free = recordobject_free

    tp.tp_init = NULL

cdef _type_configure_getsetitem "_type_configure_getsetitem"(ob, readonly=False):
    cdef PyTypeObject *tp "tp" = <PyTypeObject*>ob;

    tp.tp_as_sequence.sq_item = recordobject_item
    if readonly:
       tp.tp_as_sequence.sq_ass_item = NULL
    else:
       tp.tp_as_sequence.sq_ass_item = recordobject_ass_item

    tp.tp_as_mapping.mp_subscript = recordobject_subscript
    if readonly:
       tp.tp_as_mapping.mp_ass_subscript = NULL
    else:
       tp.tp_as_mapping.mp_ass_subscript = recordobject_ass_subscript

cdef dict fieldsgetset_cache "fieldsgetset_cache" = {}
cdef dict fieldsget_cache "fieldsget_cache" = {}

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

        if hashable:
            tp_cls.tp_hash = recordclass_hash
        else:
            tp_cls.tp_hash = NULL

        return cls

class structclasstype(type):
    #
    def __new__(tp, name, bases, ns):
        cdef object options "options"
        cdef bint readonly "readonly"
        cdef bint usedict "usedict"
        cdef bint gc "gc"
        cdef bint weakref "weakref"
        cdef bint hashable "hashable"
        cdef bint assequence "assequence"
        cdef object cls "cls"
        cdef object item_object "item_object"
        cdef object index "index"
        cdef object attrname "attrname"

        options = ns.pop('__options__', {})
        readonly = options.get('readonly', False)
        usedict = options.get('usedict', False)
        weakref = options.get('weakref', False)
        hashable = options.get('hashable', False)
        assequence = options.get('assequence', True)

        if 'gc' in options:
            gc = options.get('gc')
        else:
            gc = 0

        if readonly and not hashable:
            hashable = 1

        cls = type.__new__(tp, name, bases, ns)

        if not hasattr(cls, "__fields__"):
            raise TypeError('Class is missing __fields__')

        fields = cls.__fields__

        _type_configure_basic(cls, len(fields), usedict, gc, weakref, hashable)
        if assequence:
            _type_configure_getsetitem(cls, readonly)

        for index, attrname in enumerate(fields):
            if readonly:
                item_object = fieldsget_cache.get(index, None)
                if item_object is None:
                    item_object = recordobjectget(index)
                    fieldsget_cache[index] = item_object
            else:
                item_object = fieldsgetset_cache.get(index)
                if item_object is None:
                    item_object = recordobjectgetset(index)
                    fieldsgetset_cache[index] = item_object
            setattr(cls, attrname, item_object)

        return cls

class arrayclasstype(type):
    #
    def __new__(tp, name, bases, ns):
        cdef object options "options"
        cdef bint readonly "readonly"
        cdef bint usedict "usedict"
        cdef bint hashable "hashable"
        cdef bint gc "gc"
        cdef object weakref "weakref"
        cdef object cls "cls"
        cdef object n "n"

        n = ns.pop('__size__')
        options = ns.pop('__options__')
        readonly = options.get('readonly', False)
        usedict = options.get('usedict', False)
        if 'gc' in options:
            gc = options.get('gc')
        else:
            gc = 0
        weakref = options.get('weakref', False)
        hashable = options.get('hashable', False)
        if readonly and not hashable:
            hashable = 1

        cls = type.__new__(tp, name, bases, ns)

        _type_configure_basic(cls, n, usedict, gc, weakref, hashable)
        _type_configure_getsetitem(cls, readonly)

        return cls

@cython.final
cdef public class recordobjectiter[object recordobjectIter, type recordobjectIterType]:
    cdef PyObject *op "op"
    cdef Py_ssize_t i "i"
    cdef Py_ssize_t n "n"

    def __init__(self, op):
        self.op = <PyObject*>op
        self.i = 0
        self.n = recordobject_len(self.op)

    def __next__(self):
        if self.i < self.n:
            ob = <object>recordobject_item(self.op, self.i)
            self.i += 1
            return ob
        else:
            raise StopIteration

    def __iter__(self):
        return self

@cython.final
cdef public class recordobjectgetset[object recordobjectGetSet, type recordobjectGetSetType]:

    cdef Py_ssize_t i "i"

    def __init__(self, i):
        self.i = i

    def __get__(self, ob, tp):
        if ob is None:
            return self
        return <object>recordobject_item(<PyObject*>ob, self.i)

    def __set__(self, ob, val):
        if ob is None:
            raise ValueError('None object')
        recordobject_ass_item(<PyObject*>ob, self.i, <PyObject*>val)

@cython.final
cdef public class recordobjectget[object recordobjectGet, type recordobjectGetType]:

    cdef Py_ssize_t i "i"

    def __init__(self, i):
        self.i = i

    def __get__(self, ob, tp):
        if ob is None:
            return self
        return <object>recordobject_item(<PyObject*>ob, self.i)

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
