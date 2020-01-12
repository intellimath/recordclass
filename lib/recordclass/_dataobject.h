#define datatuple_items(type, op) (PyObject**)((char*)(op) + type->tp_basicsize)

#define dataobject_slots(op) (PyObject**)((char*)(op) + sizeof(PyObject))
#define datatuple_slots(op) (PyObject**)((char*)(op) + sizeof(PyVarObject))

#define datatuple_numslots(tp) ((tp->tp_basicsize - sizeof(PyVarObject))/sizeof(PyObject*) - \
                                (tp->tp_dictoffset?1:0) - \
                                (tp->tp_weaklistoffset?1:0))

#define dataobject_numslots(tp) ((tp->tp_basicsize - sizeof(PyObject))/sizeof(PyObject*)) - \
                                 (tp->tp_dictoffset?1:0) - \
                                 (tp->tp_weaklistoffset?1:0)

#define datatuple_numitems(op) Py_SIZE(op)

#define dataobject_dictptr(type, op) ((PyObject**)((char*)(op) + type->tp_dictoffset))
#define dataobject_weaklistptr(type, op) ((PyObject**)((char*)op + type->tp_weaklistoffset))
#define dataobject_hasdict(type) (type->tp_dictoffset != 0)
#define dataobject_hasweaklist(type) (type->tp_weaklistoffset != 0)

// #define _Py_SIZE_ROUND_DOWN(n, a) ((size_t)(n) & ~(size_t)((a) - 1))
// #define _Py_SIZE_ROUND_UP(n, a) (((size_t)(n) + \
//         (size_t)((a) - 1)) & ~(size_t)((a) - 1))
// #define _Py_ALIGN_DOWN(p, a) ((void *)((uintptr_t)(p) & ~(uintptr_t)((a) - 1)))