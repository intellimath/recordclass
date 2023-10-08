# Recordclass library

**Recordclass** is [MIT Licensed](http://opensource.org/licenses/MIT) python library.
It was started as a "proof of concept" for the problem of fast "mutable"
alternative of `namedtuple` (see [question](https://stackoverflow.com/questions/29290359/existence-of-mutable-named-tuple-in-python) on [stackoverflow](https://stackoverflow.com)).
It was evolved further in order to provide more memory saving, fast and flexible types.

**Recordclass** library provide record/data-like classes that do not participate in cyclic *garbage collection* (GC) mechanism by default, but support only *reference counting* for garbage collection.
The instances of such classes havn't `PyGC_Head` prefix in the memory, which decrease their size and have a little faster path for the instance creation and deallocation.
This may make sense in cases where it is necessary to limit the size of the objects as much as possible, provided that they will never be part of references cycles in the application.
For example, when an object represents a record with fields with values of simple types by convention (`int`, `float`, `str`, `date`/`time`/`datetime`, `timedelta`, etc.).

In order to illustrate this, consider a simple class with type hints:

    class Point:
        x: int
        y: int

By tacit agreement instances of the class `Point` is supposed to have attributes `x` and `y` with values of `int` type. Assigning other types of values, which are not subclass of `int`, should be considered as a violation of the agreement.

Other examples are non-recursive data structures in which all leaf elements represent a value of an atomic type.
Of course, in python, nothing prevent you from “shooting yourself in the foot" by creating the reference cycle in the script or application code.
But in many cases, this can still be avoided provided that the developer understands what he is doing and uses such classes in the codebase with care.
Another option is to use static code analyzers along with type annotations to monitor compliance with typehints.

The library is built on top of the base class `dataobject`. The type of `dataobject` is special metaclass `datatype`.
   It control creation  of subclasses, which  will not participate in cyclic GC and do not contain `__dict__`  and `__weakref__`  by default.
   As the result the instance of such class need less memory.
   It's memory footprint is similar to memory footprint of instances of the classes with `__slots__` but without `PyGC_Head`. So the difference in memory size is equal to the size of `PyGC_Head`.
   It also tunes `basicsize` of the instances, creates descriptors for the fields and etc.
   All subclasses of `dataobject` created by `class statement` support `attrs`/`dataclasses`-like API.
   For example:

        from recordclass import dataobject, astuple, asdict
        class Point(dataobject):
            x:int
            y:int

        >>> p = Point(1, 2)
        >>> astuple(p)
        (1, 2)
        >>> asdict(p)
        {'x':1, 'y':2}

The `recordclass` factory create dataobject-based subclass with specified fields and the support of `namedtuple`-like API.
   By default it will not participate in cyclic GC too.

        >>> from recordclass import recordclass
        >>> Point = recordclass('Point', 'x y')
        >>> p = Point(1, 2)
        >>> p.y = -1
        >>> print(p._astuple)
        (1, -1)
        >>> x, y = p
        >>> print(p._asdict)
        {'x':1, 'y':-1}

It also provide a factory function `make_dataclass` for creation of subclasses of `dataobject` with the specified field names.
   These subclasses support `attrs`/`dataclasses`-like API. It's equivalent to creating subclasses of dataobject using `class statement`.
   For example:

        >>> Point = make_dataclass('Point', 'x y')
        >>> p = Point(1, 2)
        >>> p.y = -1
        >>> print(p.x, p.y)
        1 -1

   If one want to use some sequence for initialization then:

        >>> p = Point(*sequence)


There is also a factory function `make_arrayclass` for creation of the subclass of `dataobject`, which can be considered as a compact array of simple objects.
   For example:

        >>> Pair = make_arrayclass(2)
        >>> p = Pair(2, 3)
        >>> p[1] = -1
        >>> print(p)
        Pair(2, -1)

The library provide in addition the classes `lightlist` (immutable) and `litetuple`, which considers as list-like and tuple-like *light* containers in order to save memory. They do not supposed to participate in cyclic GC too. Mutable variant of litetuple is called by `mutabletuple`.
    For example:

        >>> lt = litetuple(1, 2, 3)
        >>> mt = mutabletuple(1, 2, 3)
        >>> lt == mt
        True
        >>> mt[-1] = -3
        >>> lt == mt
        False
        >>> print(sys.getsizeof((1,2,3)), sys.getsizeof(litetuple(1,2,3)))
        64 48

Note if one like create `litetuple` or `mutabletuple` from some iterable then:

        >>> seq = [1,2,3]
        >>> lt = litetuple(*seq)
        >>> mt = mutabletuple(*seq)

### Memory footprint

The following table explain memory footprints of the  `dataobject`-based objects and litetuples:

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>tuple/namedtuple</th>
      <th>class with __slots__</th>
      <th>recordclass/dataobject</th>
      <th>litetuple/mutabletuple</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>g+b+s+n&times;p</td>
      <td>g+b+n&times;p</td>
      <td>b+n&times;p</td>
      <td>b+s+n&times;p</td>
    </tr>
  </tbody>
</table>

where:

 * b = sizeof(PyObject)
 * s = sizeof(Py_ssize_t)
 * n = number of items
 * p = sizeof(PyObject*)
 * g = sizeof(PyGC_Head)

This is useful in that case when you absolutely sure that reference cycle isn't supposed.
For example, when all field values are instances of atomic types.
As a result the size of the instance is decreased by 24-32 bytes for cpython 3.4-3.7 and by 16 bytes for cpython >=3.8.

### Performance counters

Here is the table with performance counters, which was measured using `tools/perfcounts.py` script:

* recordclass 0.19, python 3.10, debian/testing linux, x86-64:

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>id</th>
      <th>size</th>
      <th>new</th>
      <th>getattr</th>
      <th>setattr</th>
      <th>getitem</th>
      <th>setitem</th>
      <th>getkey</th>
      <th>setkey</th>
      <th>iterate</th>
      <th>copy</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>litetuple</td>
      <td>48</td>
      <td>0.18</td>
      <td></td>
      <td></td>
      <td>0.2</td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.33</td>
      <td>0.19</td>
    </tr>
    <tr>
      <td>mutabletuple</td>
      <td>48</td>
      <td>0.18</td>
      <td></td>
      <td></td>
      <td>0.21</td>
      <td>0.21</td>
      <td></td>
      <td></td>
      <td>0.33</td>
      <td>0.18</td>
    </tr>
    <tr>
      <td>tuple</td>
      <td>64</td>
      <td>0.24</td>
      <td></td>
      <td></td>
      <td>0.21</td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.37</td>
      <td>0.16</td>
    </tr>
    <tr>
      <td>namedtuple</td>
      <td>64</td>
      <td>0.75</td>
      <td>0.23</td>
      <td></td>
      <td>0.21</td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.33</td>
      <td>0.21</td>
    </tr>
    <tr>
      <td>class+slots</td>
      <td>56</td>
      <td>0.68</td>
      <td>0.29</td>
      <td>0.33</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>dataobject</td>
      <td>40</td>
      <td>0.25</td>
      <td>0.23</td>
      <td>0.29</td>
      <td>0.2</td>
      <td>0.22</td>
      <td></td>
      <td></td>
      <td>0.33</td>
      <td>0.2</td>
    </tr>
    <tr>
      <td>dataobject+gc</td>
      <td>56</td>
      <td>0.27</td>
      <td>0.22</td>
      <td>0.29</td>
      <td>0.19</td>
      <td>0.21</td>
      <td></td>
      <td></td>
      <td>0.35</td>
      <td>0.22</td>
    </tr>
    <tr>
      <td>dict</td>
      <td>232</td>
      <td>0.32</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.2</td>
      <td>0.24</td>
      <td>0.35</td>
      <td>0.25</td>
    </tr>
    <tr>
      <td>dataobject+map</td>
      <td>40</td>
      <td>0.25</td>
      <td>0.23</td>
      <td>0.3</td>
      <td></td>
      <td></td>
      <td>0.29</td>
      <td>0.29</td>
      <td>0.32</td>
      <td>0.2</td>
    </tr>
  </tbody>
</table>

* recordclass 0.19, python 3.11, debian/testing linux, x86-64:

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>id</th>
      <th>size</th>
      <th>new</th>
      <th>getattr</th>
      <th>setattr</th>
      <th>getitem</th>
      <th>setitem</th>
      <th>getkey</th>
      <th>setkey</th>
      <th>iterate</th>
      <th>copy</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>litetuple</td>
      <td>48</td>
      <td>0.17</td>
      <td></td>
      <td></td>
      <td>0.19</td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.27</td>
      <td>0.13</td>
    </tr>
    <tr>
      <td>mutabletuple</td>
      <td>48</td>
      <td>0.16</td>
      <td></td>
      <td></td>
      <td>0.19</td>
      <td>0.2</td>
      <td></td>
      <td></td>
      <td>0.27</td>
      <td>0.14</td>
    </tr>
    <tr>
      <td>tuple</td>
      <td>64</td>
      <td>0.16</td>
      <td></td>
      <td></td>
      <td>0.12</td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.27</td>
      <td>0.15</td>
    </tr>
    <tr>
      <td>namedtuple</td>
      <td>64</td>
      <td>0.72</td>
      <td>0.19</td>
      <td></td>
      <td>0.17</td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.26</td>
      <td>0.2</td>
    </tr>
    <tr>
      <td>class+slots</td>
      <td>56</td>
      <td>0.45</td>
      <td>0.1</td>
      <td>0.11</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>dataobject</td>
      <td>40</td>
      <td>0.17</td>
      <td>0.11</td>
      <td>0.1</td>
      <td>0.19</td>
      <td>0.19</td>
      <td></td>
      <td></td>
      <td>0.25</td>
      <td>0.19</td>
    </tr>
    <tr>
      <td>dataobject+gc</td>
      <td>56</td>
      <td>0.20</td>
      <td>0.11</td>
      <td>0.1</td>
      <td>0.18</td>
      <td>0.19</td>
      <td></td>
      <td></td>
      <td>0.25</td>
      <td>0.21</td>
    </tr>
    <tr>
      <td>dict</td>
      <td>184</td>
      <td>0.30</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.2</td>
      <td>0.22</td>
      <td>0.3</td>
      <td>0.19</td>
    </tr>
    <tr>
      <td>dataobject+map</td>
      <td>40</td>
      <td>0.17</td>
      <td>0.11</td>
      <td>0.11</td>
      <td></td>
      <td></td>
      <td>0.21</td>
      <td>0.27</td>
      <td>0.25</td>
      <td>0.19</td>
    </tr>
  </tbody>
</table>

Main repository for `recordclass` is on [github](https://github.com/intellimath/recordclass).

Here is also a simple [example](https://github.com/intellimath/recordclass/blob/main/examples/what_is_recordclass.ipynb).

More examples can be found in the folder [examples](https://github.com/intellimath/recordclass/tree/main/examples).

## Quick start

### Installation

#### Installation from directory with sources

Install:

    >>> python3 setup.py install

Run tests:

    >>> python3 test_all.py

#### Installation from PyPI

Install:

    >>> pip3 install recordclass

Run tests:

    >>> python3 -c "from recordclass.test import *; test_all()"

### Quick start with dataobject

`Dataobject` is the base class for creation of data classes with fast instance creation and small memory footprint. They provide `dataclass`-like API.

First load inventory:

    >>> from recordclass import dataobject, asdict, astuple, as_dataclass

Define class one of three ways:

    class Point(dataobject):
        x: int
        y: int

or

    @as_dataclass()
    class Point:
        x: int
        y: int

or

    >>> Point = make_dataclass("Point", [("x",int), ("y",int)])

Annotations of the fields are defined as a dict in `__annotations__`:

    >>> print(Point.__annotations__)
    {'x': <class 'int'>, 'y': <class 'int'>}

There is default text representation:

    >>> p = Point(1, 2)
    >>> print(p)
    Point(x=1, y=2)

The instances has a minimum memory footprint that is possible for CPython object, which contain only Python objects:

    >>> sys.getsizeof(p) # the output below for python 3.8+ (64bit)
    40
    >>> p.__sizeof__() == sys.getsizeof(p) # no additional space for cyclic GC support
    True

The instance is mutable by default:

    >>> p_id = id(p)
    >>> p.x, p.y = 10, 20
    >>> id(p) == p_id
    True
    >>> print(p)
    Point(x=10, y=20)

There are functions `asdict` and `astuple` for converting to `dict` and to `tuple`:

    >>> asdict(p)
    {'x':10, 'y':20}
    >>> astuple(p)
    (10, 20)

By default subclasses of dataobject are mutable. If one want make it immutable then there is the option `readonly=True`:

    class Point(dataobject, readonly=True):
        x: int
        y: int

    >>> p = Point(1,2)
    >>> p.x = -1
    . . . . . . . . . . . . .
    TypeError: item is readonly

By default subclasses of dataobject are not iterable by default.
If one want make it iterable then there is the option `iterable=True`:

    class Point(dataobject, iterable=True):
        x: int
        y: int

    >>> p = Point(1,2)
    >>> for x in p: print(x)
    1
    2

Default values are also supported::

    class CPoint(dataobject):
        x: int
        y: int
        color: str = 'white'

or

    >>> CPoint = make_dataclass("CPoint", [("x",int), ("y",int), ("color",str)], defaults=("white",))

    >>> p = CPoint(1,2)
    >>> print(p)
    Point(x=1, y=2, color='white')

But

    class PointInvalidDefaults(dataobject):
        x:int = 0
        y:int

is not allowed. A fields without default value may not appear after a field with default value.

There is an option `copy_default` (starting from 0.21) in order to assign a copy of the default value when creating an instance:

     class Polygon(dataobject, copy_default=True):
        points: list = []

    >>> pg1 = Polygon()
    >>> pg2 = Polygon()
    >>> assert pg1.points == pg2.points
    True
    >>> assert id(pg1.points) != id(pg2.points)
    True

A `Factory` (starting from 0.21) allows you to setup a factory function to calculate the default value:

    from recordclass import Factory

    class A(dataobject, copy_default=True):
        x: tuple = Factory( lambda: (list(), dict()) )

    >>> a = A()
    >>> b = A()
    >>> assert a.x == b.x
    True
    >>> assert id(a.x[0]) != id(b.x[0])
    True
    >>> assert id(a.x[1]) != id(b.x[1])
    True

There is the options `fast_new`. By default it is `True`. If one like to more options for
introspection then one need specify `fast_new=False`.

    class SlowerPoint(dataobject, fast_new=False):
        x: int
        y: int

The followings timings explain (in jupyter notebook) boosting effect of `fast_new` option:

    %timeit l1 = [SlowerPoint(i,i) for i in range(100000)]
    %timeit l2 = [Point(i,i) for i in range(100000)]
    # output with python 3.9 64bit
    25.6 ms ± 2.4 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
    10.4 ms ± 426 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

The downside of `fast_new=True` option is less possibilities for introspection of the instance.

If someone wants to define a class attribute, then there is a `ClassVar` trick:

    class Point(dataobject):
        x:int
        y:int
        color:ClassVar[int] = 0

    >>> print(Point.__fields__)
    ('x', 'y')
    >>> print(Point.color)
    0

If the default value for the `ClassVar`-attribute is not specified, 
it will just be excluded from the `__fields___`.


### Quick start with recordclass

The `recordclass` factory function is designed to create classes that support `namedtuple`'s API, can be mutable and immutable, provide fast creation of the instances and have a minimum memory footprint.

First load inventory:

    >>> from recordclass import recordclass

Example with `recordclass`:

    >>> Point = recordclass('Point', 'x y')
    >>> p = Point(1,2)
    >>> print(p)
    Point(1, 2)
    >>> print(p.x, p.y)
    1 2
    >>> p.x, p.y = 1, 2
    >>> print(p)
    Point(1, 2)
    >>> sys.getsizeof(p) # the output below is for 64bit cpython3.8+
    32

Example with class statement and typehints:

    >>> from recordclass import RecordClass

    class Point(RecordClass):
       x: int
       y: int

    >>> print(Point.__annotations__)
    {'x': <class 'int'>, 'y': <class 'int'>}
    >>> p = Point(1, 2)
    >>> print(p)
    Point(1, 2)
    >>> print(p.x, p.y)
    1 2
    >>> p.x, p.y = 1, 2
    >>> print(p)
    Point(1, 2)

By default `recordclass`-based class instances doesn't participate in cyclic GC and therefore they are smaller than `namedtuple`-based ones. If one want to use it in scenarios with reference cycles then one have to use option `gc=True` (`gc=False` by default):

    >>> Node = recordclass('Node', 'root children', gc=True)

or

    class Node(RecordClass, gc=True):
         root: 'Node'
         chilren: list

The `recordclass` factory can also specify type of the fields:

    >>> Point = recordclass('Point', [('x',int), ('y',int)])

or

    >>> Point = recordclass('Point', {'x':int, 'y':int})

### Using dataobject-based classes with mapping protocol

    class FastMapingPoint(dataobject, mapping=True):
        x: int
        y: int

or

    FastMapingPoint = make_dataclass("FastMapingPoint", [("x", int), ("y", int)], mapping=True)

    >>> p = FastMappingPoint(1,2)
    >>> print(p['x'], p['y'])
    1 2
    >>> sys.getsizeof(p) # the output below for python 3.10 (64bit)
    32

### Using dataobject-based classes for recursive data without reference cycles

There is the option `deep_dealloc` (default value is `False`) for deallocation of recursive datastructures.
Let consider simple example:

    class LinkedItem(dataobject):
        val: object
        next: 'LinkedItem'

    class LinkedList(dataobject, deep_dealloc=True):
        start: LinkedItem = None
        end: LinkedItem = None

        def append(self, val):
            link = LinkedItem(val, None)
            if self.start is None:
                self.start = link
            else:
                self.end.next = link
            self.end = link

Without `deep_dealloc=True` deallocation of the instance of `LinkedList` will be failed if the length of the linked list is too large.
But it can be resolved with `__del__` method for clearing the linked list:

    def __del__(self):
        curr = self.start
        while curr is not None:
            next = curr.next
            curr.next = None
            curr = next

There is builtin more fast deallocation method using finalization mechanizm when `deep_dealloc=True`. In such case one don't need `__del__`  method for clearing the linked list.

> Note that for classes with `gc=True` this method is disabled: the python's cyclic GC is used in these cases.

For more details see notebook [example_datatypes](https://github.com/intellimath/recordclass/tree/main/examples/example_datatypes.ipynb).

### Changes:

#### 0.21

* Add a new option `copy_default` (default `False`) to allow assigning a copy of the default
  value for the field. For example:
  
       class A(dataobject, copy_default=True):
            l: list = []

       a = A()
       b = A()
       assert(a.l == b.l)
       assert(id(a.l) != id(b.l))

* Allow to inherit the options: `copy_default`, `gc`, `iterable`. For example:
  
       class Base(dataobject, copy_default=True):
          pass

      class A(Base):
            l: list = []

       a = A()
       b = A()
       assert a.l == b.l
       assert id(a.l) != id(b.l)

* Add `Factory` to specify factory function for default values. For example:

        from recordclass import Factory
        class A(dataobject):
            x: tuple = Factory(lambda: (list(), dict()))

        a = A()
        b = A()
        assert a.x == ([],{})
        assert id(a.x) != id(b.x)
        assert id(a.x[0]) != id(b.x[0])
        assert id(a.x[1]) != id(b.x[1])

        from recordclass import Factory
        class A(dataobject, copy_default=True):
            l: list = []
            x: tuple = Factory(lambda: (list(), dict()))

        a = A()
        b = A()
        assert a.x == ([],{})
        assert id(a.x) != id(b.x)
        assert a.l == []
        assert id(a.l) != id(b.l)

  * Recordclass supports python 3.12 (tested on linux/debian 11/12 and windows via appveyor).

  

#### 0.20.1

* Improve row_factory for `sqlite` on the ground of `dataobject`-based classes.
* Move recordclass repository to https://github.com/intellimath/recordclass from bitbucket.org.

#### 0.20

* Library codebase is compatible with python 3.12
  (tested for linux only, windows until python3.12 support on appveyor).
* Fix error with update of readonly attribute via `update` function.

#### 0.19.2

* Exception message for Cls(**kwargs) with invalid kweyword argument is more precise (#37).
* Add parameter `immutable_type` for python >= 3.11. If `immutable_type=True` then a generated class
  (not an instance) will be immutable. If class do not contain user defuned `__init__` and `__new__`
  then instance creation will be faster (via vectorcall protocol).

#### 0.19.1

* Fix regression with `C.attr=value` (with immutable class by default).

#### 0.19

* Add vectorcall protocal to `litetuple` and `mutabletuple`.
* Add vectorcall protocal to `dataobject`.
* Now dataobject's `op.__hash__` return `id(op)` by default.
  The option `hashable=True` make dataobject hashably by value.
* Now `dataobject`-based classes, `litetuple` and `mutabletuple` are support
  bytecode specializations since Python 3.11 for instance creation and for getattr/setattr.
* Fix `make` function for cases, when subclass have nontrivial `__init__`.
* Note for `dataobject`-based subclasses with non-trivial `__init__` one may want define also `__reduce__`.
  For example:

      def __reduce__(self):
        from recordclass import dataobject, make
        tp, args = dataobject.__reduce__(self)
        return make, (tp, args)


#### 0.18.4

* Fix a bug #35 with duplicating the field name during inheritance and mixing it with class level attributes.
* Allow use of ClassVar to define class level field.

#### 0.18.3

* Fix bug with a tuple as default value of the field.
* Fix defaults propagtion to subclasses.
* Fix some issues with pickling in the context of dill.

#### 0.18.2

* Slightly improve performance in the default `__init__`  when fields have default values or kwargs.
* Remove experimental pypy support: slow and difficult to predict memory footprint.
* Exclude experimental cython modules.

#### 0.18.1.1

* Repackage 0.18.1 with `use_cython=0`

#### 0.18.1

* Allow to initialize fields in the user defined `__init__`  method instead of `__new__`  (issue 29).
  If `__init__`  is defined by user then it's responsible for initialization of all fields.
  Note that this feature only work for mutable fields.
  Instances of the class with `readonly=True` must be initialized only in the default `__new__`.
  For example:

        class A(dataobject):
              x:int
              y:int

              def __init__(self, x, y):
                  self.x = x
                  self.y = y

* `fast_new=True` by default.
* Add `make_row_factory` for `sqlite3` :

        class Planet(dataobject):
            name:str
            radius:int

        >>> con = sql.connect(":memory:")
        >>> cur = con.execute("SELECT 'Earth' AS name, 6378 AS radius")
        >>> cur.row_factory = make_row_factory(Planet)
        >>> row = cur.fetchone()
        >>> print(row)
        Planet(name='Earth', radius=6378)

#### 0.18.0.1

* Exclude test_dataobject_match.py (for testing `match` statement) for python < 3.10.

#### 0.18

* Python 3.11 support.
* Adapt data object to take benefit from bytecode specialization in 3.11.
* Fix issue for argument with default value in `__new__`, which havn't `__repr__`
  that can be interpreted as valid python expression
  for creation of the default value.
* Add support for typing.ClassVar.
* Add `Py_TPFLAGS_SEQUENCE`  and `Py_TPFLAGS_MAPPING`.
* Add `__match_args__`  to support match protocol for dataobject-based subclasses.

#### 0.17.5

* Make to compile, to build and to test successfully for python 3.11.

#### 0.17.4

* Fixed error with missing `_PyObject_GC_Malloc` in 3.11.

#### 0.17.3

* Fix compatibility issue: restore gnu98 C-syntax.
* Fix remained issues with use of "Py_SIZE(op)" and "Py_TYPE(op)" as l-value.

#### 0.17.2

* Add support for python 3.10.
* There are no use of "Py_SIZE(op)" and "Py_TYPE(op)" as l-value.

#### 0.17.1

* Fix packaging issue with cython=1 in setup.py

#### 0.17

* Now recordclass library may be compiled for pypy3, but there is still no complete runtime compatibility with pypy3.
* Slighly imporove performance of `litetuple` / `mutabletuple`.
* Slighly imporove performance of `dataobject`-based subclasses.
* Add adapter `as_dataclass`. For example:

        @as_dataclass()
        class Point:
            x:int
            y:int

* Module _litelist is implemented in pure C.
* Make dataobject.__copy__ faster.

#### 0.16.3

* Add possibility for recordclasses to assighn values by key:

        A = recordclass("A", "x y", mapping=True)
        a = A(1,2)
        a['x'] = 100
        a['y'] = 200

#### 0.16.2

* Fix the packaging bug in 0.16.1.

#### 0.16.1

* Add `dictclass` factory function to generate class with `dict-like` API and without attribute access to the fields.
  Features: fast instance creation, small memory footprint.

#### 0.16

* `RecordClass` started to be a direct subclass of dataobject with `sequence=True` and support
  of `namedtuple`-like API.
  Insted of `RecordClass(name, fields, **kw)` for class creation
  use factory function `recordclass(name, fields, **kw)`
  (it allows to specify types).
* Add option api='dict'  to `make_dataclass` for creating class that support dict-like API.
* Now one can't remove dataobject's property from it's class using del or builting delattr.
  For example:

        >>> Point = make_dataclass("Point", "x y")
        >>> del Point.x
        ...........
        AttributeError: Attribute x of the class Point can't be deleted

* Now one can't delete field's value using del or builting delattr.
  For example:

        >>> p = Point(1, 2)
        >>> del p.x
        ...........
        AttributeError: The value can't be deleted"
  Insted one can use assighnment to None:

        >>> p = Point(1, 2)
        >>> p.x = None

* Slightly improve performance of the access by index of dataobject-based classes with option `sequence=True`.


#### 0.15.1

* Options `readonly` and `iterable` now can be sspecified via keyword arguments in class statement.
  For example:

        class Point(dataobject, readonly=True, iterable=True):
             x:int
             y:int

* Add `update(cls, **kwargs)` function to update attribute values.`


#### 0.15

* Now library supports only Python >= 3.6
* 'gc' and 'fast_new' options now can be specified as kwargs in class statement.
* Add a function `astuple(ob)` for transformation dataobject instance `ob` to a tuple.
* Drop datatuple based classes.
* Add function `make(cls, args, **kwargs)` to create instance of the class `cls`.
* Add function `clone(ob, **kwargs)` to clone dataobject instance `ob`.
* Make structclass as alias of make_dataclass.
* Add option 'deep_dealloc' (@clsconfig(deep_dealloc=True)) for deallocation
  instances of dataobject-based recursive subclasses.

#### 0.14.3:

* Subclasses of `dataobject` now support iterable and hashable protocols by default.

#### 0.14.2:

* Fix compilation issue for python 3.9.

#### 0.14.1:

* Fix issue with __hash__ when subclassing recordclass-based classes.

#### 0.14:

* Add __doc__ to generated  `dataobject`-based class in order to support `inspect.signature`.
* Add `fast_new` argument/option for fast instance creation.
* Fix refleak in `litelist`.
* Fix sequence protocol ability for `dataobject`/`datatuple`.
* Fix typed interface for `StructClass`.

#### 0.13.2

* Fix issue #14 with deepcopy of dataobjects.

#### 0.13.1

* Restore ``join_classes` and add new function `join_dataclasses`.

#### 0.13.0.1

* Remove redundant debug code.


#### 0.13

* Make `recordclass` compiled and work with cpython 3.8.
* Move repository to **git** instead of mercurial since bitbucket will drop support of mercurial repositories.
* Fix some potential reference leaks.


#### 0.12.0.1

* Fix missing .h files.

#### 0.12

* `clsconfig` now become the main decorator for tuning dataobject-based classes.
* Fix concatenation of mutabletuples (issue `#10`).

#### 0.11.1:

* `dataobject` instances may be deallocated faster now.

#### 0.11:

* Rename `memoryslots` to `mutabletuple`.
* `mutabletuple` and `immutabletuple` dosn't participate in cyclic garbage collection.
* Add `litelist` type for list-like objects, which doesn't participate in cyglic garbage collection.

#### 0.10.3:

* Introduce DataclassStorage and RecordclassStorage.
  They allow cache classes and used them without creation of new one.
* Add `iterable` decorator and argument. Now dataobject with fields isn't iterable by default.
* Move `astuple` to `dataobject.c`.

#### 0.10.2

* Fix error with dataobject's `__copy__`.
* Fix error with pickling of recordclasses and structclasses, which was appeared since 0.8.5
  (Thanks to Connor Wolf).

#### 0.10.1

* Now by default sequence protocol is not supported by default if dataobject has fields,
  but iteration is supported.
* By default argsonly=False for usability reasons.

#### 0.10

* Invent new factory function `make_class` for creation of different kind of dataobject classes
  without GC support by default.
* Invent new metaclass `datatype` and new base class `dataobject` for creation dataobject class using
  `class` statement.
  It have disabled GC support, but could be enabled by decorator `dataobject.enable_gc`.
  It support type hints (for python >= 3.6) and default values.
  It may not specify sequence of field names in `__fields__` when type hints are applied to all
  data attributes (for python >= 3.6).
* Now `recordclass`-based classes may not support cyclic garbage collection too.
  This reduces the memory footprint by the size of `PyGC_Head`.
  Now by default recordclass-based classes doesn't support cyclic garbage collection.

#### 0.9

* Change version to 0.9 to indicate a step forward.
* Cleanup `dataobject.__cinit__`.

#### 0.8.5

* Make `arrayclass`-based objects support setitem/getitem and `structclass`-based objects able
  to not support them. By default, as before `structclass`-based objects support setitem/getitem protocol.
* Now only instances of `dataobject` are comparable to 'arrayclass'-based and `structclass`-based instances.
* Now generated classes can be hashable.


#### 0.8.4

* Improve support for readonly mode for structclass and arrayclass.
* Add tests for arrayclass.

#### 0.8.3

* Add typehints support to structclass-based classes.


#### 0.8.2

* Remove `usedict`, `gc`, `weaklist` from the class `__dict__`.

#### 0.8.1

* Remove Cython dependence by default for building `recordclass` from the sources [Issue #7].

#### 0.8

* Add `structclass` factory function. It's analog of `recordclass` but with less memory
  footprint for it's instances (same as for instances of classes with `__slots__`) in the camparison
  with `recordclass` and `namedtuple`
  (it currently implemented with `Cython`).
* Add `arrayclass` factory function which produce a class for creation fixed size array.
  The benefit of such approach is also less memory footprint
  (it currently currently implemented with `Cython`).
* `structclass` factory has argument `gc` now. If `gc=False` (by default) support of cyclic garbage collection
  will switched off for instances of the created class.
* Add function `join(C1, C2)` in order to join two `structclass`-based classes C1 and C2.
* Add `sequenceproxy` function for creation of immutable and hashable proxy object from class instances,
  which implement access by index
  (it currently currently implemented with `Cython`).
* Add support for access to recordclass object attributes by idiom: `ob['attrname']` (Issue #5).
* Add argument `readonly` to recordclass factory to produce immutable namedtuple.
  In contrast to `collection.namedtuple` it use same descriptors as for
  regular recordclasses for performance increasing.

#### 0.7

* Make mutabletuple objects creation faster. As a side effect: when number of fields >= 8
  recordclass instance creation time is not biger than creation time of instaces of
  dataclasses with `__slots__`.
* Recordclass factory function now create new recordclass classes in the same way as namedtuple in 3.7
  (there is no compilation of generated python source of class).

#### 0.6

* Add support for default values in recordclass factory function in correspondence
  to same addition to namedtuple in python 3.7.

#### 0.5

* Change version to 0.5

#### 0.4.4

* Add support for default values in RecordClass (patches from Pedro von Hertwig)
* Add tests for RecorClass (adopted from python tests for NamedTuple)

#### 0.4.3

* Add support for typing for python 3.6 (patches from Vladimir Bolshakov).
* Resolve memory leak issue.

#### 0.4.2

* Fix memory leak in property getter/setter
