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
