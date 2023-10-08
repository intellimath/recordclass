typedef struct {
    PyObject ob_head;
    PyObject *ob_items[1];
} PyDataStruct;

struct PyFactoryObject {
  PyObject_HEAD
  PyObject *factory;
};

typedef struct {
    PyObject_HEAD
    Py_ssize_t index;
    int readonly;
} dataobjectproperty_object;


#define PyDataObject_ITEMS(op) (PyObject**)(((PyDataStruct*)op)->ob_items)

#define PyDataObject_NUMITEMS(tp) (tp->tp_itemsize)

#define PyDataObject_LEN(o) (Py_TYPE(o)->tp_itemsize)
#define PyDataObject_GET_ITEM(op, i) (((PyDataStruct*)(op))->ob_items[(i)])
#define PyDataObject_SET_ITEM(op, i, v) (((PyDataStruct*)(op))->ob_items[(i)]=(v)) 

#define PyDataObject_DICTPTR(type, op) ((PyObject**)((char*)(op) + (type)->tp_dictoffset))
#define PyDataObject_WEAKLISTPTR(type, op) ((PyObject**)((char*)op + type->tp_weaklistoffset))
#define PyDataObject_HAS_DICT(type) (type->tp_dictoffset != 0)
#define PyDataObject_HAS_WEAKLIST(type) (type->tp_weaklistoffset != 0)

#define Py_TP_BASE(o) (Py_TYPE(o)->tp_base)
#define Py_METATYPE(o) Py_TYPE(Py_TYPE(o))
