typedef struct _PyLiteListObject {
  PyObject_HEAD
  Py_ssize_t ob_size;
  Py_ssize_t allocated;
  PyObject **ob_item;
} PyLiteListObject;

