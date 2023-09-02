// The MIT License (MIT)

// Copyright (c) «2021-2023» «Shibzukhov Zaur, szport at gmail dot com»

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software - recordclass library - and associated documentation files 
// (the "Software"), to deal in the Software without restriction, including 
// without limitation the rights to use, copy, modify, merge, publish, distribute, 
// sublicense, and/or sell copies of the Software, and to permit persons to whom 
// the Software is furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

#ifdef Py_LIMITED_API
#undef Py_LIMITED_API
#endif

#include "Python.h"
#include <stddef.h>

static PyTypeObject PyLiteTuple_Type;
static PyTypeObject PyMLiteTuple_Type;

#define PyLiteTuple_GET_ITEM(op, i) (((PyLiteTupleObject *)(op))->ob_item[i])
#define PyLiteTuple_SET_ITEM(op, i, v) (((PyLiteTupleObject *)(op))->ob_item[i] = v)
#define PyLiteTuple_GET_SIZE(seq) PyTuple_GET_SIZE(seq)

#define PyLiteTuple_CheckExact(op) (Py_TYPE(op) == &PyLiteTuple_Type || Py_TYPE(op) == &PyMLiteTuple_Type)
#define PyLiteTuple_Check(op) (PyLiteTuple_CheckExact(op) || PyObject_IsInstance(op, (PyObject*)&PyLiteTuple_Type) || PyObject_IsInstance(op, (PyObject*)&PyMLiteTuple_Type))

#if !defined(Py_SET_TYPE)
#define Py_SET_TYPE(ob, type) (((PyObject*)(ob))->ob_type) = (type)
#endif

#if !defined(Py_TYPE)
#define Py_TYPE(ob) ((PyObject*)(ob))->ob_type
#endif

#define py_refcnt(ob) (((PyObject*)(ob))->ob_refcnt)

#if !defined(Py_SET_SIZE)
#define Py_SET_SIZE(ob, size) (((PyVarObject*)(ob))->ob_size = (size))
#endif

#define DEFERRED_ADDRESS(addr) 0

static PyTypeObject PyLiteTuple_Type;
typedef PyTupleObject PyLiteTupleObject;

static PyObject *
pyobject_get_builtin(const char *attrname_c)
{
    PyObject *modname;
    PyObject *mod, *ob;

    modname = PyUnicode_FromString("builtins");
    if (modname == NULL)
        return NULL;
    mod = PyImport_Import(modname);
    if (mod == NULL) {
        Py_DECREF(modname);    
        return NULL;
    }
    ob = PyObject_GetAttrString(mod, attrname_c);
    if (ob == NULL) {
        Py_DECREF(mod);
        return NULL;
    }
    Py_DECREF(modname);    
    Py_DECREF(mod);
    return ob;
}

static PyObject *
litetuple_alloc(PyTypeObject *tp, Py_ssize_t nitems)
{
    // Py_ssize_t size = _PyObject_VAR_SIZE(tp, nitems);
    PyObject *op = (PyObject*)_PyObject_NewVar(tp, nitems);

//     if (!op)
//         return PyErr_NoMemory();

//     // memset(op, '\0', size);

//     Py_SET_TYPE(op, tp);
//     if (tp->tp_flags & Py_TPFLAGS_HEAPTYPE)
//         Py_INCREF(tp);

//     Py_SET_SIZE(op, nitems);
//     _Py_NewReference(op);

    return op;
}

static PyObject *
litetuple_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    const Py_ssize_t n = Py_SIZE(args);

    PyObject *newobj = (PyObject*)_PyObject_NewVar(type, n);

    PyTupleObject *tmp = (PyTupleObject*)args; 
    PyObject **dest = ((PyLiteTupleObject*)newobj)->ob_item;
    PyObject **src = tmp->ob_item;

    Py_ssize_t i;
    for (i = 0; i < n; i++) {
        PyObject *val = *(src++);
        Py_INCREF(val);
        *(dest++) = val;
    }

    return newobj;
}

#if PY_VERSION_HEX >= 0x030A0000
static PyObject *
litetuple_vectorcall(PyObject *type, PyObject * const*args,
                 size_t nargsf, PyObject *kwnames)
{
    const Py_ssize_t n = PyVectorcall_NARGS(nargsf);

    PyObject *newobj = (PyObject*)_PyObject_NewVar((PyTypeObject*)type, n);

    PyObject **dest = ((PyLiteTupleObject*)newobj)->ob_item;

    Py_ssize_t i;
    for (i = 0; i < n; i++) {
        PyObject *val = *(args++);
        Py_INCREF(val);
        *(dest++) = val;
    }

    return newobj;
}
#endif

static int
litetuple_init(PyObject *ob, PyObject *args, PyObject *kwds) {
    return 0;
}

static PyObject *
litetuple_getnewargs(PyLiteTupleObject *ob)
{
    PyObject *v;
    PyTupleObject *res;
    Py_ssize_t i;
    const Py_ssize_t n = Py_SIZE(ob);

    res = (PyTupleObject*)PyTuple_New(n);

    if (res == NULL)
        return NULL;

    for (i = n; --i >= 0; ) {
        v = PyLiteTuple_GET_ITEM(ob, i);
        PyTuple_SET_ITEM(res, i, v);
        Py_INCREF(v);
    }

    return (PyObject*)res;
}

static void
litetuple_dealloc(PyLiteTupleObject *op)
{
    Py_ssize_t i = Py_SIZE(op);

    while (--i >= 0) {
        Py_XDECREF(op->ob_item[i]);
    }

    Py_TYPE(op)->tp_free((PyObject *)op);
}

static PyObject *
litetuple_repr(PyObject *dd)
{
    PyObject *baserepr;
    PyObject *v, *result;
    const Py_ssize_t n = Py_SIZE(dd);
        
    if (n == 0) {
        result = PyUnicode_FromString("litetuple()\0");
        return result;
    }

    if (n == 1) {
        v = PyTuple_GET_ITEM(dd, 0);
        baserepr = PyObject_Repr(v);
        result = PyUnicode_FromFormat("litetuple(%U)", baserepr);
        return result;
    }    
    
    baserepr = PyTuple_Type.tp_repr(dd);
    if (baserepr == NULL)
        return NULL;

    result = PyUnicode_FromFormat("litetuple%U", baserepr);
    Py_DECREF(baserepr);
    return result;
}

PyDoc_STRVAR(litetuple_doc,
"litetuple([...]) --> litetuple\n\n\
");

static PyObject *
litetuple_concat(PyLiteTupleObject *a, PyObject *bb)
{
    Py_ssize_t size;
    Py_ssize_t i, n;
    PyObject **src, **dest;
    PyLiteTupleObject *np;
    
    if (!PyLiteTuple_Check(bb)) {
        PyErr_Format(PyExc_TypeError,
             "can only concatenate tuple (not \"%.200s\") to tuple",
                 Py_TYPE(bb)->tp_name);
        return NULL;
    }
#define b ((PyLiteTupleObject *)bb)
    size = Py_SIZE(a) + Py_SIZE(b);
    if (size < 0)
        return PyErr_NoMemory();

    np = (PyLiteTupleObject *) litetuple_alloc(Py_TYPE(a), size);
    if (np == NULL) {
        return NULL;
    }
    
    src = a->ob_item;
    dest = np->ob_item;

    n = Py_SIZE(a);
    if (n > 0) {
        for (i = 0; i < n; i++) {
            PyObject *v = src[i];
            Py_INCREF(v);
            dest[i] = v;
        }
    }
    
    src = b->ob_item;
    dest = np->ob_item + Py_SIZE(a);
    n = Py_SIZE(b);
    for (i = 0; i < n; i++) {
        PyObject *v = src[i];
        Py_INCREF(v);
        dest[i] = v;
    }
#undef b

    return (PyObject *)np;
}

static PyObject *
litetuple_slice(PyLiteTupleObject *a, Py_ssize_t ilow, Py_ssize_t ihigh)
{
    PyLiteTupleObject *np;
    PyObject **src, **dest;
    Py_ssize_t i;
    Py_ssize_t len;

    if (ilow < 0)
        ilow = 0;
    if (ihigh >= Py_SIZE(a))
        ihigh = Py_SIZE(a);
    if (ihigh < ilow)
        ihigh = ilow;

    len = ihigh - ilow;

    np = (PyLiteTupleObject*)litetuple_alloc(Py_TYPE(a), len);
    if (np == NULL)
        return NULL;
        
    src = a->ob_item + ilow;
    dest = np->ob_item;
    if (len > 0) {
        for (i = 0; i < len; i++) {
            PyObject *v = src[i];
            Py_INCREF(v);
            dest[i] = v;
        }
    }
    return (PyObject *)np;
}

static int
litetuple_ass_slice(PyLiteTupleObject *a, Py_ssize_t ilow, Py_ssize_t ihigh, PyObject *v)
{
    PyObject **item;
    PyObject **vitem = NULL;
    PyObject *v_as_SF = NULL; /* PySequence_Fast(v) */
    Py_ssize_t n;
    Py_ssize_t k;
    int result = -1;
    
    if (v == NULL)
        return result;
    else {
        if ((PyObject*)a == v) {
            v = litetuple_slice((PyLiteTupleObject*)v, 0, Py_SIZE(v));
            if (v == NULL)
                return result;
                
            result = litetuple_ass_slice(a, ilow, ihigh, v);
            Py_DECREF(v);
            return result;
        }
        v_as_SF = PySequence_Fast(v, "can only assign an iterable");
        if(v_as_SF == NULL) {
            return result;
        }
        n = PySequence_Fast_GET_SIZE(v_as_SF);
        vitem = PySequence_Fast_ITEMS(v_as_SF);
    }
    
    if (ilow < 0)
        ilow = 0;
    else if (ilow > Py_SIZE(a))
        ilow = Py_SIZE(a);

    if (ihigh < ilow)
        ihigh = ilow;
    else if (ihigh > Py_SIZE(a))
        ihigh = Py_SIZE(a);

    if (n != ihigh - ilow) {
        Py_XDECREF(v_as_SF);    
        return -1;
    }
    
    item = ((PyLiteTupleObject*)a)->ob_item;
    if (n > 0) {
        for (k = 0; k < n; k++, ilow++) {
            PyObject *w = vitem[k];
            PyObject *u = item[ilow];
            Py_XDECREF(u);
            item[ilow] = w;
            Py_XINCREF(w);
        }
    }
    Py_XDECREF(v_as_SF);    
    return 0;
}

static int
litetuple_ass_item(PyLiteTupleObject *a, Py_ssize_t i, PyObject *v)
{
    const Py_ssize_t n = Py_SIZE(a);
    
    if (i < 0)
        i += n;
    if (i < 0 || i >= Py_SIZE(a)) {
        PyErr_SetString(PyExc_IndexError,
                        "assignment index out of range");
        return -1;
    }
    
    if (v == NULL)
        return -1;
    
    PyObject **ptr = a->ob_item + i;
    PyObject *old_value = *ptr;
    *ptr = v;

    Py_DECREF(old_value);
    Py_INCREF(v);
    return 0;
}

static PyObject *
litetuple_item(PyLiteTupleObject *a, Py_ssize_t i)
{
    const Py_ssize_t n = Py_SIZE(a);
    
    if (i < 0)
        i += n;
    if (i < 0 || i >= n) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }

    PyObject *v = a->ob_item[i];
    Py_INCREF(v);
    return v;
}

static inline int
_PyIndex_Check(PyObject *obj)
{
    PyNumberMethods *tp_as_number = Py_TYPE(obj)->tp_as_number;
    return (tp_as_number != NULL && tp_as_number->nb_index != NULL);
}

static PyObject*
litetuple_subscript(PyLiteTupleObject* self, PyObject* item)
{
    if (_PyIndex_Check(item)) {        
        Py_ssize_t i = PyLong_AsSsize_t(item);
        if (i == -1 && PyErr_Occurred())
            return NULL;
        return litetuple_item(self, i);
    }
    if (PySlice_Check(item)) {
        Py_ssize_t start, stop, step, slicelength;

        if (PySlice_GetIndicesEx(item, (PyTuple_GET_SIZE(self)), &start, &stop, &step, &slicelength) < 0)
            return NULL;
        return litetuple_slice(self, start, stop);
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "subscript must be integer, slice or string, but not %.200s",
                     Py_TYPE(item)->tp_name);
        return NULL;
    }
}

static int
litetuple_ass_subscript(PyLiteTupleObject* self, PyObject* item, PyObject* value)
{
    if (_PyIndex_Check(item)) {
        Py_ssize_t i = PyLong_AsSsize_t(item);
        if (i == -1 && PyErr_Occurred())
            return -1;
        return litetuple_ass_item(self, i, value);
    }
    if (PySlice_Check(item)) {
        Py_ssize_t start, stop, step, slicelength;

        if (PySlice_GetIndicesEx(item, (Py_SIZE(self)), &start, &stop, &step, &slicelength) < 0)
            return -1; 
        return litetuple_ass_slice(self, start, stop, value);
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "indices must be integers, not %.200s",
                     Py_TYPE(item)->tp_name);
        return -1;
    }
}

static PyObject *
litetuple_repeat(PyLiteTupleObject *a, Py_ssize_t n)
{
    Py_ssize_t i, j;
    Py_ssize_t size;
    PyTupleObject *np;
    PyObject **p, **items;
    if (n < 0)
        n = 0;
    if (Py_SIZE(a) == 0) {
        return litetuple_alloc(Py_TYPE(a), 0);
    }
    if (n > PY_SSIZE_T_MAX / Py_SIZE(a))
        return PyErr_NoMemory();
    size = Py_SIZE(a);
    np = (PyLiteTupleObject *) litetuple_alloc(Py_TYPE(a), Py_SIZE(a) * n);
    if (np == NULL)
        return NULL;
    
    if (size == 0)
        return (PyObject *)np;
        
    p = np->ob_item;
    items = a->ob_item;
    for (i = 0; i < n; i++) {
        for (j = 0; j < size; j++) {
            *p = items[j];
            Py_INCREF(*p);
            p++;
        }
    }
    return (PyObject *) np;
}

PyDoc_STRVAR(litetuple_len_doc,
"T.__len__() -- len of T");

static Py_ssize_t
litetuple_len(PyLiteTupleObject *op)
{
    return Py_SIZE(op);
}

PyDoc_STRVAR(litetuple_sizeof_doc,
"T.__sizeof__() -- size of T in memory, in bytes");

static PyObject *
litetuple_sizeof(PyLiteTupleObject *self)
{
    Py_ssize_t res;

    res = PyLiteTuple_Type.tp_basicsize + Py_SIZE(self) * sizeof(PyObject*);
    return PyLong_FromSsize_t(res);
}

static PyObject *
litetuple_richcompare(PyObject *v, PyObject *w, int op)
{
    PyLiteTupleObject *vt, *wt;
    Py_ssize_t i;
    Py_ssize_t vlen, wlen;

    if (!PyLiteTuple_Check(v) || !PyLiteTuple_Check(w))
        Py_RETURN_NOTIMPLEMENTED;

    vt = (PyLiteTupleObject *)v;
    wt = (PyLiteTupleObject *)w;

    vlen = Py_SIZE(vt);
    wlen = Py_SIZE(wt);
    
    if ((vlen != wlen) && (op == Py_EQ || op == Py_NE)) {
        PyObject *res;
        if (op == Py_EQ)
            res = Py_False;
        else
            res = Py_True;
        Py_INCREF(res);
        return res;
    }    
    
    for (i = 0; i < vlen && i < wlen; i++) {
        int k = PyObject_RichCompareBool(vt->ob_item[i],
                                         wt->ob_item[i], Py_EQ);
        if (k < 0)
            return NULL;
        if (!k)
            break;
    }

    if (i >= vlen || i >= wlen) {
        /* No more items to compare -- compare sizes */
        int cmp;
        PyObject *res;
        switch (op) {
        case Py_LT: cmp = vlen <  wlen; break;
        case Py_LE: cmp = vlen <= wlen; break;
        case Py_EQ: cmp = vlen == wlen; break;
        case Py_NE: cmp = vlen != wlen; break;
        case Py_GT: cmp = vlen >  wlen; break;
        case Py_GE: cmp = vlen >= wlen; break;
        default: return NULL; /* cannot happen */
        }
        if (cmp)
            res = Py_True;
        else
            res = Py_False;
        Py_INCREF(res);
        return res;
    }

    /* We have an item that differs -- shortcuts for EQ/NE */
    if (op == Py_EQ) {
        Py_INCREF(Py_False);
        return Py_False;
    }
    if (op == Py_NE) {
        Py_INCREF(Py_True);
        return Py_True;
    }

    /* Compare the final item again using the proper operator */
    return PyObject_RichCompare(vt->ob_item[i], wt->ob_item[i], op);
}

static PySequenceMethods litetuple_as_sequence = {
    (lenfunc)litetuple_len,                          /* sq_length */
    (binaryfunc)litetuple_concat,                    /* sq_concat */
    (ssizeargfunc)litetuple_repeat,                  /* sq_repeat */
    (ssizeargfunc)litetuple_item,                    /* sq_item */
    0,                                                 /* sq_slice */
    (ssizeobjargproc)litetuple_ass_item,             /* sq_ass_item */
    0,                                                 /* sq_ass_item */
    0,                                                 /* sq_ass_slice */
    0,                                                 /* sq_contains */
};

static PyMappingMethods litetuple_as_mapping = {
    (lenfunc)litetuple_len,
    (binaryfunc)litetuple_subscript,
    (objobjargproc)litetuple_ass_subscript
};

static PySequenceMethods litetuple_ro_as_sequence = {
    (lenfunc)litetuple_len,                          /* sq_length */
    (binaryfunc)litetuple_concat,                    /* sq_concat */
    (ssizeargfunc)litetuple_repeat,                  /* sq_repeat */
    (ssizeargfunc)litetuple_item,                    /* sq_item */
    0,                                                 /* sq_slice */
    0,                                                 /* sq_ass_item */
    0,                                                 /* sq_ass_item */
    0,                                                 /* sq_ass_slice */
    0,                                                 /* sq_contains */
};

static PyMappingMethods litetuple_ro_as_mapping = {
    (lenfunc)litetuple_len,
    (binaryfunc)litetuple_subscript,
    0
};

PyDoc_STRVAR(litetuple_copy_doc, "D.copy() -> a shallow copy of D.");

static PyObject *
litetuple_copy(PyLiteTupleObject *ob)
{
    const Py_ssize_t len = Py_SIZE(ob);

    PyLiteTupleObject *np = (PyLiteTupleObject*)litetuple_alloc(Py_TYPE(ob), len);
    if (np == NULL)
        return NULL;
        
    PyObject **src = ob->ob_item;
    PyObject **dest = np->ob_item;
    if (len > 0) {
        Py_ssize_t i;
        for (i = 0; i < len; i++) {
            PyObject *v = src[i];
            Py_INCREF(v);
            dest[i] = v;
        }
    }
    return (PyObject *)np;
}


PyDoc_STRVAR(litetuple_reduce_doc, "D.__reduce__()");

static PyObject *
litetuple_reduce(PyObject *ob)
{
    PyObject *args;
    PyObject *result;
    PyObject *tmp;

    tmp = PySequence_Tuple(ob);
    args = PyTuple_Pack(1, tmp);
    Py_DECREF(tmp);
    if (args == NULL)
        return NULL;

    result = PyTuple_Pack(2, Py_TYPE(ob), args);
    Py_DECREF(args);
    return result;
}

PyDoc_STRVAR(litetuple_bool_doc, "t.__nonzero__ -> bool");

static PyObject*
litetuple_bool(PyLiteTupleObject *o) 
{
    if (Py_SIZE(o) > 0)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static Py_hash_t
litetuple_hash(PyObject *v)
{
    register Py_uhash_t x;
    Py_hash_t y;
    register Py_ssize_t len = Py_SIZE(v);
    register PyObject **p;
    Py_hash_t mult = 1000003L;

    x = 0x345678L;
    p = ((PyTupleObject*)v)->ob_item;
    while (--len >= 0) {
        y = PyObject_Hash(*p++);
        if (y == -1)
            return -1;
        x = (x ^ y) * mult;
        /* the cast might truncate len; that doesn't change hash stability */
        mult += (long)(82520L + len + len);
    }
    x += 97531L;
    if (x == (Py_uhash_t)-1)
        x = -2;
    return (Py_hash_t)x;
}

static PyMethodDef litetuple_methods[] = {
    {"__getnewargs__",          (PyCFunction)litetuple_getnewargs,  METH_NOARGS},
    {"__copy__", (PyCFunction)litetuple_copy, METH_NOARGS, litetuple_copy_doc},
    {"__len__", (PyCFunction)litetuple_len, METH_NOARGS, litetuple_len_doc},
    {"__nonzero__", (PyCFunction)litetuple_bool, METH_NOARGS, litetuple_bool_doc},
    {"__sizeof__",      (PyCFunction)litetuple_sizeof, METH_NOARGS, litetuple_sizeof_doc},     
    {"__reduce__", (PyCFunction)litetuple_reduce, METH_NOARGS, litetuple_reduce_doc},
    {NULL}
};

static PyObject* 
litetuple_iter(PyObject *seq);

static PyTypeObject PyLiteTuple_Type = {
    PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
    "recordclass.litetuple.litetuple",          /* tp_name */
    sizeof(PyLiteTupleObject) - sizeof(PyObject*),      /* tp_basicsize */
    sizeof(PyObject*),                              /* tp_itemsize */
    /* methods */
    (destructor)litetuple_dealloc,        /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_reserved */
    (reprfunc)litetuple_repr,             /* tp_repr */
    0,                                      /* tp_as_number */
    &litetuple_ro_as_sequence,               /* tp_as_sequence */
    &litetuple_ro_as_mapping,                /* tp_as_mapping */
    litetuple_hash          ,            /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                     /* tp_setattro */
    0,                                      /* tp_as_buffer */
#if PY_VERSION_HEX >= 0x030A0000
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | 
    Py_TPFLAGS_HAVE_VECTORCALL | Py_TPFLAGS_IMMUTABLETYPE | Py_TPFLAGS_SEQUENCE,
#else
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
#endif
                                            /* tp_flags */
    litetuple_doc,                        /* tp_doc */
    0,     /* tp_traverse */
    0,             /* tp_clear */
    litetuple_richcompare,                /* tp_richcompare */
    0,                                      /* tp_weaklistoffset*/
    litetuple_iter,                       /* tp_iter */
    0,                                      /* tp_iternext */
    litetuple_methods,                    /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_litetuple */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_litetupleoffset */
    litetuple_init,                                      /* tp_init */
    0,                                      /* tp_alloc */
    litetuple_new,                        /* tp_new */
    PyObject_Del,                        /* tp_free */
    0,                                       /* tp_is_gc */
#if PY_VERSION_HEX >= 0x030A0000
    .tp_vectorcall = litetuple_vectorcall,                                      /* tp_vectorcall */
    .tp_vectorcall_offset = offsetof(PyTypeObject, tp_vectorcall),
#endif
};

static PyTypeObject PyMLiteTuple_Type = {
    PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
    "recordclass.litetuple.mutabletuple",          /* tp_name */
    sizeof(PyLiteTupleObject) - sizeof(PyObject*),      /* tp_basicsize */
    sizeof(PyObject*),                              /* tp_itemsize */
    /* methods */
    (destructor)litetuple_dealloc,          /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_reserved */
    (reprfunc)litetuple_repr,               /* tp_repr */
    0,                                      /* tp_as_number */
    &litetuple_as_sequence,                 /* tp_as_sequence */
    &litetuple_as_mapping,                  /* tp_as_mapping */
    PyObject_HashNotImplemented,            /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                      /* tp_setattro */
    0,                                      /* tp_as_buffer */
#if PY_VERSION_HEX >= 0x030A0000
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | 
    Py_TPFLAGS_HAVE_VECTORCALL | Py_TPFLAGS_IMMUTABLETYPE | Py_TPFLAGS_SEQUENCE,
#else
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
#endif
                                            /* tp_flags */
    litetuple_doc,                          /* tp_doc */
    0,                                      /* tp_traverse */
    0,                                      /* tp_clear */
    litetuple_richcompare,                  /* tp_richcompare */
    0,                                      /* tp_weaklistoffset*/
    litetuple_iter,                         /* tp_iter */
    0,                                      /* tp_iternext */
    litetuple_methods,                      /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_litetuple */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_litetupleoffset */
    litetuple_init,                         /* tp_init */
    0,                                      /* tp_alloc */
    litetuple_new,                          /* tp_new */
    PyObject_Del,                           /* tp_free */
    0,                                       /* tp_is_gc */
#if PY_VERSION_HEX >= 0x030A0000
    .tp_vectorcall = litetuple_vectorcall,                                      /* tp_vectorcall */
    .tp_vectorcall_offset = offsetof(PyTypeObject, tp_vectorcall),
#endif
};

/*********************** MLiteTuple Iterator **************************/

typedef struct {
    PyObject_HEAD
    Py_ssize_t it_index;
    PyLiteTupleObject *it_seq; /* Set to NULL when iterator is exhausted */
} litetupleiterobject;

static void
litetupleiter_dealloc(litetupleiterobject *it)
{
    PyObject_GC_UnTrack(it);
    Py_CLEAR(it->it_seq);
    PyObject_GC_Del(it);
}

static int
litetupleiter_traverse(litetupleiterobject *it, visitproc visit, void *arg)
{
    Py_VISIT(it->it_seq);
    return 0;
}

static int
litetupleiter_clear(litetupleiterobject *it)
{
    Py_CLEAR(it->it_seq);
    return 0;
}

static PyObject *
litetupleiter_next(litetupleiterobject *it)
{
    PyTupleObject *seq;
    PyObject *item;

    seq = it->it_seq;
    if (seq == NULL)
        return NULL;

    if (it->it_index < PyLiteTuple_GET_SIZE(seq)) {
        item = PyLiteTuple_GET_ITEM(seq, it->it_index);
        Py_INCREF(item);
        ++it->it_index;
        return item;
    }

    Py_DECREF(seq);
    it->it_seq = NULL;
    return NULL;
}

static PyObject *
litetupleiter_len(litetupleiterobject *it)
{
    Py_ssize_t len = 0;
    if (it->it_seq)
        len = PyLiteTuple_GET_SIZE(it->it_seq) - it->it_index;
    return PyLong_FromSsize_t(len);
}

PyDoc_STRVAR(length_hint_doc, "Private method returning an estimate of len(list(it)).");

static PyObject *
litetupleiter_reduce(litetupleiterobject *it) //, PyObject *Py_UNUSED(ignore))
{
    if (it->it_seq)
        return Py_BuildValue("N(O)n", pyobject_get_builtin("iter"),
                             it->it_seq, it->it_index);
    else
        return Py_BuildValue("N(())", pyobject_get_builtin("iter"));
}

PyDoc_STRVAR(litetupleiter_reduce_doc, "D.__reduce__()");

static PyObject *
litetupleiter_setstate(litetupleiterobject *it, PyObject *state)
{
    Py_ssize_t index;

    index = PyLong_AsSsize_t(state);
    if (index == -1 && PyErr_Occurred())
        return NULL;
    if (it->it_seq != NULL) {
        if (index < 0)
            index = 0;
        else if (index > PyLiteTuple_GET_SIZE(it->it_seq))
            index = PyLiteTuple_GET_SIZE(it->it_seq); /* exhausted iterator */
        it->it_index = index;
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(setstate_doc, "Set state information for unpickling.");

static PyMethodDef litetupleiter_methods[] = {
    {"__length_hint__", (PyCFunction)litetupleiter_len, METH_NOARGS, length_hint_doc},
    {"__reduce__",      (PyCFunction)litetupleiter_reduce, METH_NOARGS, litetupleiter_reduce_doc},
    {"__setstate__",    (PyCFunction)litetupleiter_setstate, METH_O, setstate_doc},
    {NULL,              NULL}           /* sentinel */
};

PyTypeObject PyLiteTupleIter_Type = {
    PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
    "recordclass.litetuple.litetuple_iterator",                           /* tp_name */
    sizeof(litetupleiterobject),                    /* tp_basicsize */
    0,                                          /* tp_itemsize */
    /* methods */
    (destructor)litetupleiter_dealloc,              /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_reserved */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    (traverseproc)litetupleiter_traverse,     /* tp_traverse */
    (inquiry)litetupleiter_clear,             /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    PyObject_SelfIter,                          /* tp_iter */
    (iternextfunc)litetupleiter_next,         /* tp_iternext */
    litetupleiter_methods,                    /* tp_methods */
    0,
};

static PyObject *
litetuple_iter(PyObject *seq)
{
    litetupleiterobject *it;

    it = PyObject_GC_New(litetupleiterobject, &PyLiteTupleIter_Type);
    if (it == NULL)
        return NULL;
    it->it_index = 0;
    it->it_seq = (PyTupleObject *)seq;
    Py_INCREF(seq);
    PyObject_GC_Track(it);
    return (PyObject *)it;
}

/* List of functions defined in the module */

PyDoc_STRVAR(litetuplemodule_doc,
"Litetuple module provide mutable and immutable tuple types without cyclic garbage collection (reference count only).");

static PyMethodDef litetuplemodule_methods[] = {
//   {"getitem", get_item,     METH_VARARGS,   "__getitem__"},
//   {"freeze", litetuple_freeze,     METH_VARARGS,   "freeze litetuple object (make it readonly and hashable)"},
   {0, 0, 0, 0}
};

static struct PyModuleDef litetuplemodule = {
    PyModuleDef_HEAD_INIT,
    "recordclass._litetuple",
    litetuplemodule_doc,
    -1,
    litetuplemodule_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit__litetuple(void)
{
    PyObject *m;
    
#ifndef PYPY_VERSION
    m = PyState_FindModule(&litetuplemodule);
    if (m) {
        Py_INCREF(m);
        return m;
    }    
#endif
    
    m = PyModule_Create(&litetuplemodule);
    if (m == NULL)
        return NULL;

    if (PyType_Ready(&PyLiteTuple_Type) < 0)
        Py_FatalError("Can't initialize litetuple type");

    if (PyType_Ready(&PyMLiteTuple_Type) < 0)
         Py_FatalError("Can't initialize litetuplereadonly type");

    if (PyType_Ready(&PyLiteTupleIter_Type) < 0)
        Py_FatalError("Can't initialize litetuple iter type");
    
// #if PY_VERSION_HEX >= 0x03080000
//     if (PyLiteTuple_Type.tp_flags & Py_TPFLAGS_METHOD_DESCRIPTOR)
//         PyLiteTuple_Type.tp_flags &= ~Py_TPFLAGS_METHOD_DESCRIPTOR;
//     if (PyMLiteTuple_Type.tp_flags & Py_TPFLAGS_METHOD_DESCRIPTOR)
//         PyMLiteTuple_Type.tp_flags &= ~Py_TPFLAGS_METHOD_DESCRIPTOR;
//     if (PyLiteTupleIter_Type.tp_flags & Py_TPFLAGS_METHOD_DESCRIPTOR)
//         PyLiteTupleIter_Type.tp_flags &= ~Py_TPFLAGS_METHOD_DESCRIPTOR;
// #endif
    
    Py_INCREF(&PyLiteTuple_Type);
    PyModule_AddObject(m, "litetuple", (PyObject *)&PyLiteTuple_Type);

    Py_INCREF(&PyMLiteTuple_Type);
    PyModule_AddObject(m, "mutabletuple", (PyObject *)&PyMLiteTuple_Type);

    Py_INCREF(&PyLiteTupleIter_Type);    
    PyModule_AddObject(m, "litetupleiter", (PyObject *)&PyLiteTupleIter_Type);

    return m;
}
