// The MIT License (MIT)

// Copyright (c) «2021-2022» «Shibzukhov Zaur, szport at gmail dot com»

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

static PyTypeObject PyLiteList_Type;

#define PyLiteList_ITEMS(op) ((PyLiteListObject *)(op))->ob_item
#define PyLiteList_GET_ITEM(op, i) (((PyLiteListObject *)(op))->ob_item[i])
#define PyLiteList_SET_ITEM(op, i, v) (((PyLiteListObject *)(op))->ob_item[i] = v)
#define PyLiteList_GET_SIZE(seq) Py_SIZE(seq)
#define PyLiteList_ALLOCATED(op) (((PyLiteListObject *)(op))->allocated)
#define PyLiteList_SET_ALLOCATED(op, n) (((PyLiteListObject *)(op))->allocated = (n))

#define PyLiteList_CheckExact(op) (Py_TYPE(op) == &PyLiteList_Type)
#define PyLiteList_Check(op) (PyLiteList_CheckExact(op) || PyObject_IsInstance(op, (PyObject*)&PyLiteList_Type))

#define DEFERRED_ADDRESS(addr) 0

#define pyobject_size(tp) ( (tp)->tp_basicsize )

#define py_incref(o) ((PyObject*)(o))->ob_refcnt++
#define py_decref(o) if (--(((PyObject*)(o))->ob_refcnt) == 0) Py_TYPE((PyObject*)(o))->tp_dealloc((PyObject*)(o))

#define py_xincref(op)                                \
    do {                                              \
        PyObject *_py_xincref_tmp = (PyObject *)(op); \
        if (_py_xincref_tmp != NULL)                  \
            py_incref(_py_xincref_tmp);               \
    } while (0)

#define py_xdecref(op)                                \
    do {                                              \
        PyObject *_py_xdecref_tmp = (PyObject *)(op); \
        if (_py_xdecref_tmp != NULL)                  \
            py_decref(_py_xdecref_tmp);               \
    } while (0)

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

static PyTypeObject PyLiteList_Type;
typedef PyListObject PyLiteListObject;

static void
litelist_resize(PyObject *op, Py_ssize_t size) {
    Py_ssize_t newsize;

    if (size < 9)
        newsize =  size + (size / 8) + 3;
    else
        newsize =  size + (size / 8) + 6;

    PyLiteList_ITEMS(op) = (PyObject**)PyMem_Realloc(PyLiteList_ITEMS(op), newsize*sizeof(PyObject*));
    PyLiteList_SET_ALLOCATED(op, newsize);
}


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
        py_decref(modname);    
        return NULL;
    }
    ob = PyObject_GetAttrString(mod, attrname_c);
    if (ob == NULL) {
        py_decref(mod);
        return NULL;
    }
    py_decref(modname);    
    py_decref(mod);
    return ob;
}

static PyObject *
litelist_alloc(PyTypeObject *tp, Py_ssize_t n_items)
{
    Py_ssize_t size = pyobject_size(tp);
    PyObject *op = (PyObject*)PyObject_Malloc(size);

    if (!op)
        return PyErr_NoMemory();

    // memset(op, '\0', size);
    
    PyLiteList_ITEMS(op) = (PyObject**)PyMem_Malloc(n_items*sizeof(PyObject*));

    Py_SET_TYPE(op, tp);
    if (tp->tp_flags & Py_TPFLAGS_HEAPTYPE)
        py_incref(tp);

    PyLiteList_SET_ALLOCATED(op, n_items);
    Py_SET_SIZE(op, n_items);
    _Py_NewReference(op);

    return op;
}

static PyObject *
litelist_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    const Py_ssize_t n_args = Py_SIZE(args);
    Py_ssize_t n;
    PyObject **src;
    int is_tpl = 0;
    PyTupleObject *tpl = NULL;

    if (n_args != 1)
        PyErr_Format(PyExc_TypeError,
             "%s.__new__ accept only one argument",
                 type->tp_name);
                 
    PyObject *items = PyTuple_GET_ITEM(args, 0);
    
    if (Py_TYPE(items) == &PyTuple_Type) {
        n = Py_SIZE(items);
        src = ((PyTupleObject*)items)->ob_item;
    } else if (Py_TYPE(items) == &PyList_Type) {
        n = Py_SIZE(items);
        src = ((PyListObject*)items)->ob_item;
    } else {
        tpl = (PyTupleObject*)PySequence_Tuple(items);
        n = Py_SIZE(tpl);
        src = ((PyTupleObject*)tpl)->ob_item;
        is_tpl = 1;
    }

    PyObject *op = litelist_alloc(type, n);
    PyObject **dest = PyLiteList_ITEMS(op);

    Py_ssize_t i;
    for (i = 0; i < n; i++) {
        PyObject *val = *(src++);
        py_incref(val);
        *(dest++) = val;
    }

    if (is_tpl)
        py_decref(tpl);
    return op;
}

static int
litelist_init(PyObject *ob, PyObject *args, PyObject *kwds) {
    return 0;
}

// static PyObject *
// litelist_getnewargs(PyLiteListObject *ob)
// {
//     PyObject *v;
//     PyTupleObject *res;
//     Py_ssize_t i;
//     const Py_ssize_t n = Py_SIZE(ob);

//     res = (PyTupleObject*)PyTuple_New(n);

//     if (res == NULL)
//         return NULL;

//     for (i = 0; i<n; i++) {
//         v = PyLiteList_GET_ITEM(ob, i);
//         PyTuple_SET_ITEM(res, i, v);
//         py_incref(v);
//     }

//     return (PyObject*)res;
// }

// static int
// litelist_clear(PyLiteListObject *op)
// {
//     Py_ssize_t i;

//     for (i = Py_SIZE(op); --i >= 0; ) {
//         Py_CLEAR(op->ob_item[i]);
//     }
//     Py_SET_SIZE(op, 0);
//     return 0;
// }

static void
litelist_dealloc(PyLiteListObject *op)
{
    Py_ssize_t i = Py_SIZE(op);

    while (--i >= 0) {
        PyObject *item = op->ob_item[i];
        if (item != NULL) {
            py_decref(item);
            op->ob_item[i] = NULL;
        }
    }
    
    PyMem_Free(op->ob_item);

    Py_TYPE(op)->tp_free((PyObject *)op);
}

// static void litelist_free(void *o) {
//         PyObject_Del((PyObject*)o);
// }

// static int
// litelist_traverse(PyLiteListObject *o, visitproc visit, void *arg)
// {
//     Py_ssize_t i;

//     for (i = Py_SIZE(o); --i >= 0; ) {
//         Py_VISIT(o->ob_item[i]);
//     }
//     return 0;
// }

static PyObject *
litelist_repr(PyObject *dd)
{
    PyObject *baserepr;
    PyObject *result;
    const Py_ssize_t n = Py_SIZE(dd);
        
    if (n == 0) {
        result = PyUnicode_FromString("litelist([])\0");
        return result;
    }

    baserepr = PyList_Type.tp_repr(dd);
    if (baserepr == NULL)
        return NULL;

    result = PyUnicode_FromFormat("litelist(%U)", baserepr);
    py_decref(baserepr);
    return result;
}

PyDoc_STRVAR(litelist_doc,
"litelist([...]) --> litelist\n\n\
");

static PyObject *
litelist_concat(PyLiteListObject *a, PyObject *bb)
{
    Py_ssize_t size;
    Py_ssize_t i, n;
    PyObject **src, **dest;
    PyLiteListObject *np;
    
    if (!PyLiteList_Check(bb)) {
        PyErr_Format(PyExc_TypeError,
             "can only concatenate tuple (not \"%.200s\") to tuple",
                 Py_TYPE(bb)->tp_name);
        return NULL;
    }
#define b ((PyLiteListObject *)bb)
    size = Py_SIZE(a) + Py_SIZE(b);
    if (size < 0)
        return PyErr_NoMemory();

    np = (PyLiteListObject *) litelist_alloc(Py_TYPE(a), size);
    if (np == NULL) {
        return NULL;
    }
    
    src = a->ob_item;
    dest = np->ob_item;

    n = Py_SIZE(a);
    if (n > 0) {
        for (i = 0; i < n; i++) {
            PyObject *v = src[i];
            py_incref(v);
            dest[i] = v;
        }
    }
    
    src = b->ob_item;
    dest = np->ob_item + Py_SIZE(a);
    n = Py_SIZE(b);
    for (i = 0; i < n; i++) {
        PyObject *v = src[i];
        py_incref(v);
        dest[i] = v;
    }
#undef b

    return (PyObject *)np;
}

static PyObject *
litelist_slice(PyLiteListObject *a, Py_ssize_t ilow, Py_ssize_t ihigh)
{
    PyLiteListObject *np;
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

    np = (PyLiteListObject*)litelist_alloc(Py_TYPE(a), len);
    if (np == NULL)
        return NULL;
        
    src = a->ob_item + ilow;
    dest = np->ob_item;
    if (len > 0) {
        for (i = 0; i < len; i++) {
            PyObject *v = src[i];
            py_incref(v);
            dest[i] = v;
        }
    }
    return (PyObject *)np;
}

static int
litelist_ass_slice(PyLiteListObject *a, Py_ssize_t ilow, Py_ssize_t ihigh, PyObject *v)
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
            v = litelist_slice((PyLiteListObject*)v, 0, Py_SIZE(v));
            if (v == NULL)
                return result;
                
            result = litelist_ass_slice(a, ilow, ihigh, v);
            py_decref(v);
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
        py_xdecref(v_as_SF);    
        return -1;
    }
    
    item = ((PyLiteListObject*)a)->ob_item;
    if (n > 0) {
        for (k = 0; k < n; k++, ilow++) {
            PyObject *w = vitem[k];
            PyObject *u = item[ilow];
            py_xdecref(u);
            item[ilow] = w;
            py_xincref(w);
        }
    }
    py_xdecref(v_as_SF);    
    return 0;
}

static int
litelist_ass_item(PyLiteListObject *a, Py_ssize_t i, PyObject *v)
{
    const Py_ssize_t n = Py_SIZE(a);
    
    if (i < 0)
        i += n;
    if (i < 0 || i >= Py_SIZE(a)) {
        PyErr_SetString(PyExc_IndexError,
                        "assignment index out of range");
        return -1;
    }
    
    if (v == NULL) {
        PyObject **dst = a->ob_item + i;
        PyObject **src = dst + 1;
        
        py_decref(*dst);
        i++;
        while (i < n) {
            *(dst++) = *(src++);
            i++;
        }
        *dst = NULL;
        Py_SET_SIZE(a, Py_SIZE(a)-1);
        return 0;
    }
    
    PyObject **ptr = a->ob_item + i;

    py_decref(*ptr);
    *ptr = v;
    py_incref(v);

    return 0;
}

static PyObject *
litelist_item(PyLiteListObject *a, Py_ssize_t i)
{
    const Py_ssize_t n = Py_SIZE(a);
    
    if (i < 0)
        i += n;
    if (i < 0 || i >= n) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }
    PyObject *v = a->ob_item[i];
    py_incref(v);
    return a->ob_item[i];
}

static inline int
_PyIndex_Check(PyObject *obj)
{
    PyNumberMethods *tp_as_number = Py_TYPE(obj)->tp_as_number;
    return (tp_as_number != NULL && tp_as_number->nb_index != NULL);
}

static PyObject*
litelist_subscript(PyLiteListObject* self, PyObject* item)
{
    if (_PyIndex_Check(item)) {        
        Py_ssize_t i = PyLong_AsSsize_t(item);
        if (i == -1 && PyErr_Occurred())
            return NULL;
        return litelist_item(self, i);
    }
    if (PySlice_Check(item)) {
        Py_ssize_t start, stop, step, slicelength;

        if (PySlice_GetIndicesEx(item, (PyTuple_GET_SIZE(self)), &start, &stop, &step, &slicelength) < 0)
            return NULL;
        return litelist_slice(self, start, stop);
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "subscript must be integer, slice or string, but not %.200s",
                     Py_TYPE(item)->tp_name);
        return NULL;
    }
}

static int
litelist_ass_subscript(PyLiteListObject* self, PyObject* item, PyObject* value)
{
    if (_PyIndex_Check(item)) {
        Py_ssize_t i = PyLong_AsSsize_t(item);
        if (i == -1 && PyErr_Occurred())
            return -1;
        return litelist_ass_item(self, i, value);
    }
    if (PySlice_Check(item)) {
        Py_ssize_t start, stop, step, slicelength;

        if (PySlice_GetIndicesEx(item, (Py_SIZE(self)), &start, &stop, &step, &slicelength) < 0)
            return -1; 
        return litelist_ass_slice(self, start, stop, value);
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "indices must be integers, not %.200s",
                     Py_TYPE(item)->tp_name);
        return -1;
    }
}

static PyObject *
litelist_repeat(PyLiteListObject *a, Py_ssize_t n)
{
    Py_ssize_t i, j;
    Py_ssize_t size;
    PyLiteListObject *np;
    PyObject **p, **items;
    if (n < 0)
        n = 0;
    if (Py_SIZE(a) == 0) {
        return litelist_alloc(Py_TYPE(a), 0);
    }
    if (n > PY_SSIZE_T_MAX / Py_SIZE(a))
        return PyErr_NoMemory();
    size = Py_SIZE(a);
    np = (PyLiteListObject *) litelist_alloc(Py_TYPE(a), Py_SIZE(a) * n);
    if (np == NULL)
        return NULL;
    
    if (size == 0)
        return (PyObject *)np;
        
    p = np->ob_item;
    items = a->ob_item;
    for (i = 0; i < n; i++) {
        for (j = 0; j < size; j++) {
            *p = items[j];
            py_incref(*p);
            p++;
        }
    }
    return (PyObject *) np;
}

PyDoc_STRVAR(litelist_len_doc,
"T.__len__() -- len of T");

static Py_ssize_t
litelist_len(PyLiteListObject *op)
{
    return Py_SIZE(op);
}

PyDoc_STRVAR(litelist_sizeof_doc,
"T.__sizeof__() -- size of T in memory, in bytes");

static PyObject *
litelist_sizeof(PyLiteListObject *self)
{
    Py_ssize_t res;

    res = PyLiteList_Type.tp_basicsize + Py_SIZE(self) * sizeof(PyObject*);
    return PyLong_FromSsize_t(res);
}

static PyObject *
litelist_richcompare(PyObject *v, PyObject *w, int op)
{
    PyLiteListObject *vt, *wt;
    Py_ssize_t i;
    Py_ssize_t vlen, wlen;

    if (!PyLiteList_Check(v) || !PyLiteList_Check(w))
        Py_RETURN_NOTIMPLEMENTED;

    vt = (PyLiteListObject *)v;
    wt = (PyLiteListObject *)w;

    vlen = Py_SIZE(vt);
    wlen = Py_SIZE(wt);
    
    if ((vlen != wlen) && (op == Py_EQ || op == Py_NE)) {
        PyObject *res;
        if (op == Py_EQ)
            res = Py_False;
        else
            res = Py_True;
        py_incref(res);
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
        py_incref(res);
        return res;
    }

    /* We have an item that differs -- shortcuts for EQ/NE */
    if (op == Py_EQ) {
        py_incref(Py_False);
        return Py_False;
    }
    if (op == Py_NE) {
        py_incref(Py_True);
        return Py_True;
    }

    /* Compare the final item again using the proper operator */
    return PyObject_RichCompare(vt->ob_item[i], wt->ob_item[i], op);
}

static PySequenceMethods litelist_as_sequence = {
    (lenfunc)litelist_len,                          /* sq_length */
    (binaryfunc)litelist_concat,                    /* sq_concat */
    (ssizeargfunc)litelist_repeat,                  /* sq_repeat */
    (ssizeargfunc)litelist_item,                    /* sq_item */
    0,                                                 /* sq_slice */
    (ssizeobjargproc)litelist_ass_item,             /* sq_ass_item */
    0,                                                 /* sq_ass_item */
    0,                                                 /* sq_ass_slice */
    0,                                                 /* sq_contains */
};

static PyMappingMethods litelist_as_mapping = {
    (lenfunc)litelist_len,
    (binaryfunc)litelist_subscript,
    (objobjargproc)litelist_ass_subscript
};

PyDoc_STRVAR(litelist_copy_doc, "D.copy() -> a shallow copy of D.");

static PyObject *
litelist_copy(PyLiteListObject *ob)
{
    const Py_ssize_t len = Py_SIZE(ob);

    PyLiteListObject *np = (PyLiteListObject*)litelist_alloc(Py_TYPE(ob), len);
    if (np == NULL)
        return NULL;
        
    if (len > 0) {
        PyObject **src = ob->ob_item;
        PyObject **dest = np->ob_item;
        Py_ssize_t i;
        for (i = 0; i < len; i++) {
            PyObject *v = src[i];
            py_incref(v);
            dest[i] = v;
        }
    }
    return (PyObject *)np;
}


PyDoc_STRVAR(litelist_reduce_doc, "D.__reduce__()");

static PyObject *
litelist_reduce(PyObject *ob)
{
    PyObject *args;
    PyObject *result;
    PyObject *tmp;

    tmp = PySequence_Tuple(ob);
    args = PyTuple_Pack(1, tmp);
    py_decref(tmp);
    if (args == NULL)
        return NULL;

    result = PyTuple_Pack(2, Py_TYPE(ob), args);
    py_decref(args);
    return result;
}

PyDoc_STRVAR(litelist_bool_doc, "t.__nonzero__ -> bool");

static PyObject*
litelist_bool(PyLiteListObject *o) 
{
    if (Py_SIZE(o) > 0)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static Py_hash_t
litelist_hash(PyObject *v)
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

PyDoc_STRVAR(litelist_append_doc,
"T.append(ob)");

static PyObject*
litelist_append(PyObject *op, PyObject *o) {
    Py_ssize_t size = Py_SIZE(op);
    
    if (size == PyLiteList_ALLOCATED(op))
        litelist_resize(op, size+1);
    
    py_incref(o);
    PyLiteList_SET_ITEM(op, size, o);
    Py_SET_SIZE(op, size + 1);
    
    Py_RETURN_NONE;
    
}

PyDoc_STRVAR(litelist_extend_doc,
"T.extend(seq)");

static PyObject*
litelist_extend(PyObject *op, PyObject *o) {
    Py_ssize_t size = Py_SIZE(op);
    PyObject *seq = PySequence_Fast(o, "argument must be iterable");
    Py_ssize_t size_o = PySequence_Fast_GET_SIZE(seq);
    
    if (size + size_o > PyLiteList_ALLOCATED(op))
        litelist_resize(op, size+size_o+1);
    
    PyObject **ptr = PySequence_Fast_ITEMS(seq);
    Py_ssize_t i;
    for (i=0; i<size_o; i++) {
        PyObject *v = ptr[i];
        py_incref(v);
        PyLiteList_SET_ITEM(op, size+i, v);
    }
    Py_SET_SIZE(op, size + size_o);
    
    py_decref(seq);
    
    Py_RETURN_NONE;    
}

PyDoc_STRVAR(litelist_remove_doc,
"T.remove(ob)");

static PyObject*
litelist_remove(PyObject *op, PyObject *v) {
    Py_ssize_t size = Py_SIZE(op);
    Py_ssize_t i;
    
    for (i=0; i<size; i++) {
        int cmp = PyObject_RichCompareBool(PyLiteList_GET_ITEM(op, i), v, Py_EQ);
        if (cmp > 0) {
            if (litelist_ass_item((PyLiteListObject*)op, i, NULL) == 0)
                Py_RETURN_NONE;
            return NULL;
        }
        else if (cmp < 0)
            return NULL;
    }
    PyErr_SetString(PyExc_ValueError, "litelist.remove(x): x not in litelist");
    return NULL;
}


static PyMethodDef litelist_methods[] = {
    {"append",  (PyCFunction)litelist_append, METH_O, litelist_append_doc},
    {"extend",  (PyCFunction)litelist_extend, METH_O, litelist_extend_doc},
    {"remove",  (PyCFunction)litelist_remove, METH_O, litelist_remove_doc},
    // {"__getnewargs__",          (PyCFunction)litelist_getnewargs,  METH_NOARGS},
    {"__copy__", (PyCFunction)litelist_copy, METH_NOARGS, litelist_copy_doc},
    {"__len__", (PyCFunction)litelist_len, METH_NOARGS, litelist_len_doc},
    {"__bool__", (PyCFunction)litelist_bool, METH_NOARGS, litelist_bool_doc},
    {"__sizeof__",      (PyCFunction)litelist_sizeof, METH_NOARGS, litelist_sizeof_doc},     
    {"__reduce__", (PyCFunction)litelist_reduce, METH_NOARGS, litelist_reduce_doc},
    {NULL}
};

static PyObject* 
litelist_iter(PyObject *seq);


static PyTypeObject PyLiteList_Type = {
    PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
    "recordclass._litelist.litelist",          /* tp_name */
    sizeof(PyLiteListObject),      /* tp_basicsize */
    0,                              /* tp_itemsize */
    /* methods */
    (destructor)litelist_dealloc,        /* tp_dealloc */
    0,                                      /* tp_print */
    0,                                      /* tp_getattr */
    0,                                      /* tp_setattr */
    0,                                      /* tp_reserved */
    (reprfunc)litelist_repr,             /* tp_repr */
    0,                                      /* tp_as_number */
    &litelist_as_sequence,               /* tp_as_sequence */
    &litelist_as_mapping,                /* tp_as_mapping */
    litelist_hash          ,            /* tp_hash */
    0,                                      /* tp_call */
    0,                                      /* tp_str */
    0,                                      /* tp_getattro */
    0,                                     /* tp_setattro */
    0,                                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
                                            /* tp_flags */
    litelist_doc,                        /* tp_doc */
    0,     /* tp_traverse */
    0,             /* tp_clear */
    litelist_richcompare,                /* tp_richcompare */
    0,                                      /* tp_weaklistoffset*/
    litelist_iter,                       /* tp_iter */
    0,                                      /* tp_iternext */
    litelist_methods,                    /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_litelist */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_litelistoffset */
    litelist_init,                                      /* tp_init */
    litelist_alloc,                                      /* tp_alloc */
    litelist_new,                        /* tp_new */
    PyObject_Del,                        /* tp_free */
    0                                       /* tp_is_gc */
};


/*********************** MLiteTuple Iterator **************************/

typedef struct {
    PyObject_HEAD
    Py_ssize_t it_index;
    PyLiteListObject *it_seq; /* Set to NULL when iterator is exhausted */
} litelistiterobject;

static void
litelistiter_dealloc(litelistiterobject *it)
{
    PyObject_GC_UnTrack(it);
    Py_CLEAR(it->it_seq);
    PyObject_GC_Del(it);
}

static int
litelistiter_traverse(litelistiterobject *it, visitproc visit, void *arg)
{
    Py_VISIT(it->it_seq);
    return 0;
}

static int
litelistiter_clear(litelistiterobject *it)
{
    Py_CLEAR(it->it_seq);
    return 0;
}

static PyObject *
litelistiter_next(litelistiterobject *it)
{
    PyLiteListObject *seq;
    PyObject *item;

//     assert(it != NULL);
    seq = it->it_seq;
    if (seq == NULL)
        return NULL;
//     assert(PyTuple_Check(seq));

    if (it->it_index < PyLiteList_GET_SIZE(seq)) {
        item = PyLiteList_GET_ITEM(seq, it->it_index);
        py_incref(item);
        ++it->it_index;
        return item;
    }

    py_decref(seq);
    it->it_seq = NULL;
    return NULL;
}

static PyObject *
litelistiter_len(litelistiterobject *it)
{
    Py_ssize_t len = 0;
    if (it->it_seq)
        len = PyLiteList_GET_SIZE(it->it_seq) - it->it_index;
    return PyLong_FromSsize_t(len);
}

PyDoc_STRVAR(length_hint_doc, "Private method returning an estimate of len(list(it)).");

static PyObject *
litelistiter_reduce(litelistiterobject *it) //, PyObject *Py_UNUSED(ignore))
{
    if (it->it_seq)
        return Py_BuildValue("N(O)n", pyobject_get_builtin("iter"),
                             it->it_seq, it->it_index);
    else
        return Py_BuildValue("N(())", pyobject_get_builtin("iter"));
}

PyDoc_STRVAR(litelistiter_reduce_doc, "D.__reduce__()");


static PyObject *
litelistiter_setstate(litelistiterobject *it, PyObject *state)
{
    Py_ssize_t index;

    index = PyLong_AsSsize_t(state);
    if (index == -1 && PyErr_Occurred())
        return NULL;
    if (it->it_seq != NULL) {
        if (index < 0)
            index = 0;
        else if (index > PyLiteList_GET_SIZE(it->it_seq))
            index = PyLiteList_GET_SIZE(it->it_seq); /* exhausted iterator */
        it->it_index = index;
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(setstate_doc, "Set state information for unpickling.");


static PyMethodDef litelistiter_methods[] = {
    {"__length_hint__", (PyCFunction)litelistiter_len, METH_NOARGS, length_hint_doc},
    {"__reduce__",      (PyCFunction)litelistiter_reduce, METH_NOARGS, litelistiter_reduce_doc},
    {"__setstate__",    (PyCFunction)litelistiter_setstate, METH_O, setstate_doc},
    {NULL,              NULL}           /* sentinel */
};

PyTypeObject PyLiteListIter_Type = {
    PyVarObject_HEAD_INIT(DEFERRED_ADDRESS(&PyType_Type), 0)
    "recordclass.litelist.litelist_iterator",                           /* tp_name */
    sizeof(litelistiterobject),                    /* tp_basicsize */
    0,                                          /* tp_itemsize */
    /* methods */
    (destructor)litelistiter_dealloc,              /* tp_dealloc */
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
    (traverseproc)litelistiter_traverse,     /* tp_traverse */
    (inquiry)litelistiter_clear,             /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    PyObject_SelfIter,                          /* tp_iter */
    (iternextfunc)litelistiter_next,         /* tp_iternext */
    litelistiter_methods,                    /* tp_methods */
    0,
};

static PyObject *
litelist_iter(PyObject *seq)
{
    litelistiterobject *it;

    it = PyObject_GC_New(litelistiterobject, &PyLiteListIter_Type);
    if (it == NULL)
        return NULL;
    it->it_index = 0;
    it->it_seq = (PyLiteListObject *)seq;
    py_incref(seq);
    PyObject_GC_Track(it);
    return (PyObject *)it;
}

PyDoc_STRVAR(litelist_fromargs_doc,
"Create new litelist from args");


static PyObject *
litelist_fromargs(PyObject *module, PyObject *args)
{
    const Py_ssize_t n_args = Py_SIZE(args);
                     
    PyObject *op = litelist_alloc(&PyLiteList_Type, n_args);
    
    PyObject **dest = PyLiteList_ITEMS(op);
    PyObject **src = ((PyTupleObject*)args)->ob_item;

    Py_ssize_t i;
    for (i = 0; i < n_args; i++) {
        PyObject *val = *(src++);
        py_incref(val);
        *(dest++) = val;
    }

    return op;
}


/* List of functions defined in the module */

PyDoc_STRVAR(litelistmodule_doc,
"Litelist module provide lite list type without cyclic garbage collection (reference count only).");

static PyMethodDef litelistmodule_methods[] = {
    {"litelist_fromargs", (PyCFunction)litelist_fromargs, METH_VARARGS, litelist_fromargs_doc},
    {0, 0, 0, 0}
};

static struct PyModuleDef litelistmodule = {
    PyModuleDef_HEAD_INIT,
    "recordclass._litelist",
    litelistmodule_doc,
    -1,
    litelistmodule_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit__litelist(void)
{
    PyObject *m;
    
#ifndef PYPY_VERSION
    m = PyState_FindModule(&litelistmodule);
    if (m) {
        py_incref(m);
        return m;
    }    
#endif
    
    m = PyModule_Create(&litelistmodule);
    if (m == NULL)
        return NULL;

    if (PyType_Ready(&PyLiteList_Type) < 0)
        Py_FatalError("Can't initialize litelist type");

    if (PyType_Ready(&PyLiteListIter_Type) < 0)
        Py_FatalError("Can't initialize litelist iter type");
    
    py_incref(&PyLiteList_Type);
    PyModule_AddObject(m, "litelist", (PyObject *)&PyLiteList_Type);

    py_incref(&PyLiteListIter_Type);    
    PyModule_AddObject(m, "litelistiter", (PyObject *)&PyLiteListIter_Type);
    

    return m;
}
