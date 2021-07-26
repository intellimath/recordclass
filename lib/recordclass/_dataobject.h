#define PyDataObject_ITEMS(op) (PyObject**)((char*)(op) + sizeof(PyObject))

#define PyDataObject_NUMITEMS(tp) ((tp->tp_basicsize - sizeof(PyObject))/sizeof(PyObject*)) - \
                                  (tp->tp_dictoffset?1:0) - \
                                  (tp->tp_weaklistoffset?1:0)

#define PyDataObject_LEN(o) (PyDataObject_NUMITEMS(Py_TYPE(o)))
#define PyDataObject_GET_ITEM(op, i) ((PyDataObject_ITEMS(op))[i])

#define PyDataObject_DICTPTR(type, op) ((PyObject**)((char*)(op) + type->tp_dictoffset))
#define PyDataObject_WEAKLISTPTR(type, op) ((PyObject**)((char*)op + type->tp_weaklistoffset))
#define PyDataObject_HAS_DICT(type) (type->tp_dictoffset != 0)
#define PyDataObject_HAS_WEAKLIST(type) (type->tp_weaklistoffset != 0)

#define Py_TP_BASE(o) (Py_TYPE(o)->tp_base)

// typedef struct {
//     PyObject ob_head;
//     PyObject *ob_slot[1];
// } PyDataObject;

// typedef struct {
//     PyVarObject ob_head;
//     PyObject *ob_slot[1];
// } PyDataTuple;