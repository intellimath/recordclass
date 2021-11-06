struct PyLiteListObject;

struct PyLiteListObject {
  PyObject_HEAD
  Py_ssize_t size;
  Py_ssize_t allocated;
  PyObject **items;
};

