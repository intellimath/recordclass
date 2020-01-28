#define PyDataTuple_ITEMS(type, op) (PyObject**)((char*)(op) + type->tp_basicsize)

#define PyDataObject_SLOTS(op) (PyObject**)((char*)(op) + sizeof(PyObject))
#define PyDataTuple_SLOTS(op) (PyObject**)((char*)(op) + sizeof(PyVarObject))

#define PyDataTuple_NUMSLOTS(tp) ((tp->tp_basicsize - sizeof(PyVarObject))/sizeof(PyObject*) - \
                                 (tp->tp_dictoffset?1:0) - \
                                 (tp->tp_weaklistoffset?1:0))

#define PyDataObject_NUMSLOTS(tp) ((tp->tp_basicsize - sizeof(PyObject))/sizeof(PyObject*)) - \
                                  (tp->tp_dictoffset?1:0) - \
                                  (tp->tp_weaklistoffset?1:0)

#define PyDataTuple_NUMITEMS(op) Py_SIZE(op)

#define PyDataObject_DICTPTR(type, op) ((PyObject**)((char*)(op) + type->tp_dictoffset))
#define PyDataObject_WEAKLISTPTR(type, op) ((PyObject**)((char*)op + type->tp_weaklistoffset))
#define PyDataObject_HAS_DICT(type) (type->tp_dictoffset != 0)
#define PyDataObject_HAS_WEAKLIST(type) (type->tp_weaklistoffset != 0)

// typedef struct {
//     PyObject ob_head;
//     PyObject *ob_slot[1];
// } PyDataObject;

// typedef struct {
//     PyVarObject ob_head;
//     PyObject *ob_slot[1];
// } PyDataTuple;