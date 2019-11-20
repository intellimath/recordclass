/* Generated by Cython 0.29.14 */

#ifndef __PYX_HAVE__recordclass__recordobject
#define __PYX_HAVE__recordclass__recordobject

#include "Python.h"
struct recordobject;
struct recordobjectIter;
struct recordobjectGetSet;
struct recordobjectGet;
struct SequenceProxyObject;

/* "recordclass/recordobject.pyx":401
 * 
 * @cython.auto_pickle(False)
 * cdef public class recordobject[object recordobject, type recordobjectType]:             # <<<<<<<<<<<<<<
 * 
 *     def __cinit__(self, *args, **kw):
 */
struct recordobject {
  PyObject_HEAD
};

/* "recordclass/recordobject.pyx":728
 * 
 * @cython.final
 * cdef public class recordobjectiter[object recordobjectIter, type recordobjectIterType]:             # <<<<<<<<<<<<<<
 *     cdef PyObject *op "op"
 *     cdef Py_ssize_t i "i"
 */
struct recordobjectIter {
  PyObject_HEAD
  PyObject *op;
  Py_ssize_t i;
  Py_ssize_t n;
};

/* "recordclass/recordobject.pyx":750
 * 
 * @cython.final
 * cdef public class recordobjectgetset[object recordobjectGetSet, type recordobjectGetSetType]:             # <<<<<<<<<<<<<<
 * 
 *     cdef Py_ssize_t i "i"
 */
struct recordobjectGetSet {
  PyObject_HEAD
  Py_ssize_t i;
};

/* "recordclass/recordobject.pyx":768
 * 
 * @cython.final
 * cdef public class recordobjectget[object recordobjectGet, type recordobjectGetType]:             # <<<<<<<<<<<<<<
 * 
 *     cdef Py_ssize_t i "i"
 */
struct recordobjectGet {
  PyObject_HEAD
  Py_ssize_t i;
};

/* "recordclass/recordobject.pyx":781
 * 
 * @cython.final
 * cdef public class SequenceProxy[object SequenceProxyObject, type SequenceProxyType]:             # <<<<<<<<<<<<<<
 *     cdef object ob "ob"
 *     cdef Py_hash_t hash "hash"
 */
struct SequenceProxyObject {
  PyObject_HEAD
  PyObject *ob;
  Py_hash_t hash;
};

#ifndef __PYX_HAVE_API__recordclass__recordobject

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

#ifndef DL_IMPORT
  #define DL_IMPORT(_T) _T
#endif

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) recordobjectType;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) recordobjectIterType;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) recordobjectGetSetType;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) recordobjectGetType;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) SequenceProxyType;

#endif /* !__PYX_HAVE_API__recordclass__recordobject */

/* WARNING: the interface of the module init function changed in CPython 3.5. */
/* It now returns a PyModuleDef instance instead of a PyModule instance. */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initrecordobject(void);
#else
PyMODINIT_FUNC PyInit_recordobject(void);
#endif

#endif /* !__PYX_HAVE__recordclass__recordobject */
