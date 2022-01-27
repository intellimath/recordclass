# Recordclass library

**Recordclass** is [MIT Licensed](http://opensource.org/licenses/MIT) python library.
It was started as a "proof of concept" for the problem of fast "mutable"
alternative of `namedtuple` (see [question](https://stackoverflow.com/questions/29290359/existence-of-mutable-named-tuple-in-python) on [stackoverflow](https://stackoverflow.com)).
It implements a factory function `recordclass` (a variant of `collection.namedtuple`) in order to create record-like classes with the same API as  `collection.namedtuple`.
It was evolved further in order to provide more memory saving, fast and flexible types.

**Recordclass** library provide record-like classes that by default do not participate in *cyclic garbage collection* (CGC) mechanism, but support only *reference counting* mechanism for garbage collection.
The instances of such classes havn't `PyGC_Head` prefix in the memory, which decrease their size and have a little faster path for the instance allocation and deallocation.
This may make sense in cases where it is necessary to limit the size of the objects as much as possible, provided that they will never be part of references cycles in the application.
For example, when an object represents a record with fields with values of simple types by convention (`int`, `float`, `str`, `date`/`time`/`datetime`, `timedelta`, etc.).

In order to illustrate this, consider a simple class with type hints:

    class Point:
        x: int
        y: int

By tacit agreement instances of the class `Point` is supposed to have attributes `x` and `y` with values of `int` type.
Assigning other types of values, which are not subclass of `int`, should be considered as a violation of the agreement.

Other examples are non-recursive data structures in which all leaf elements represent a value of an atomic type.
Of course, in python, nothing prevent you from “shooting yourself in the foot" by creating the reference cycle in the script or application code.
But in many cases, this can still be avoided provided that the developer understands what he is doing and uses such classes in the codebase with care.
Another option is to use static code analyzers along with type annotations to monitor compliance with typehints.

The `recodeclass` library provide the base class `dataobject`. The type of `dataobject` is special metaclass `datatype`. 
   It control creation  of subclasses of `dataobject`, which  will not participate in CGC by default. 
   As the result the instance of such class need less memory. 
   It's memory footprint is similar to memory footprint of instances of the classes with `__slots__`. 
   The difference is equal to the size of `PyGC_Head`. 
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

The `recordclass` factory create dataobject-based subclass with specified fields and support `namedtuple`-like API. 
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

It also provide a factory function `make_arrayclass` in order to create subclass of `dataobject` wich can consider as array of simple values.
   For example:

        >>> Pair = make_arrayclass(2)
        >>> p = Pair(2, 3)
        >>> p[1] = -1
        >>> print(p)
        Pair(2, -1)

It provide in addition the classes `lightlist` and `litetuple`, which considers as list-like and tuple-like *light* containers in order to save memory. They do not supposed to participate in CGC too.  Mutable variant of litetuple is called by `mutabletuple`. 
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

### Memory footprint

The following table explain memory footprints of the  `dataobject`-based objects and litetuples:

| tuple/namedtuple   |  class with \_\_slots\_\_  |  recordclass/dataobject |  litetuple/mutabletuple  |
|:------------------:|:--------------------------:|:-----------------------:|:------------------------:|
|     g+b+s+n\*p     |     g+b+n\*p              |         b+n\*p         |     b+s+n\*p            |

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

Here is the table with performance counters (python 3.9, debian linux, x86-64), which was measured using `tools/perfcounts.py` script:

| id                      |   size |   new | getattr   | setattr   | getitem   | setitem   | getkey   | setkey   | iterate   | copy   |
|:------------------------|-------:|------:|:----------|:----------|:----------|:----------|:---------|:---------|:----------|:-------|
| litetuple               |     48 |  0.8  |           |           | 0.69      |           |          |          | 1.14      | 0.60   |
| mutabletuple            |     48 |  0.78 |           |           | 0.69      | 0.72      |          |          | 1.14      | 0.60   |
| tuple                   |     64 |  0.51 |           |           | 0.63      |           |          |          | 1.09      | 0.53   |
| namedtuple              |     64 |  2.4  | 0.69      |           | 0.62      |           |          |          | 1.09      | 0.67   |
| class+slots             |     56 |  1.95 | 0.72      | 0.81      |           |           |          |          |           |        |
| dataobject              |     40 |  1.84 | 0.68      | 0.79      | 0.65      | 0.67      |          |          | 1.09      | 0.64   |
| dataobject+fast_new     |     40 |  0.81 | 0.68      | 0.79      | 0.65      | 0.66      |          |          | 1.09      | 0.64   |
| dataobject+gc           |     56 |  1.92 | 0.68      | 0.79      | 0.65      | 0.66      |          |          | 1.09      | 0.71   |
| dataobject+fast_new+gc  |     56 |  0.94 | 0.68      | 0.79      | 0.65      | 0.66      |          |          | 1.09      | 0.72   |
| dict                    |    232 |  0.99 |           |           |           |           | 0.67     | 0.78     | 1.24      | 0.80   |
| dataobject+fast_new+map |     40 |  0.81 |           |           |           |           | 0.95     | 0.98     | 1.09      | 0.66   |

Main repository for `recordclass` is on [bitbucket](https://bitbucket.org/intellimath/recordclass). 

Here is also a simple [example](http://nbviewer.ipython.org/urls/bitbucket.org/intellimath/recordclass/raw/master/examples/what_is_recordclass.ipynb).

More examples can be found in the folder [examples](https://bitbucket.org/intellimath/recordclass/examples).

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

By default `recordclass`-based class instances doesn't participate in CGC and therefore they are smaller than `namedtuple`-based ones. If one want to use it in scenarios with reference cycles then one have to use option `gc=True` (`gc=False` by default):

    >>> Node = recordclass('Node', 'root children', gc=True)
    
or

    class Node(RecordClass, gc=True):
         root: 'Node'
         chilren: list

The `recordclass` factory can also specify type of the fields:

    >>> Point = recordclass('Point', [('x',int), ('y',int)])
    
or

    >>> Point = recordclass('Point', {'x':int, 'y':int})

### Quick start with dataobject

`Dataobject` is the base class for creation of data classes with fast instance creation and small memory footprint. They don't provide `namedtuple`-like API. The classes created by `recrdclass` factory are subclasses of the `dataobject` too, but in addition provide `nametuple`-like API.

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

One can't remove attributes from the class:

    >>> del Point.x
    . . . . . . . .
    AttributeError: Attribute x of the class Point can't be deleted
    
Annotations of the fields are defined as a dict in `__annotations__`:

    >>> print(Point.__annotations__)
    {'x': <class 'int'>, 'y': <class 'int'>}

Default text representation:

    >>> p = Point(1, 2)
    >>> print(p)
    Point(x=1, y=2)

One can't remove field's value:

    >>> del p.x
    . . . . . . . . 
    AttributeError: The value can't be deleted

The instances has a minimum memory footprint that is possible for CPython objects, which consist only of Python objects:

    >>> sys.getsizeof(p) # the output below for python 3.8+ (64bit)
    32
    >>> p.__sizeof__() == sys.getsizeof(p) # no additional space for cyclic GC support
    True    

The instance is mutable by default:

    >>> p.x, p.y = 10, 20
    >>> print(p)
    Point(x=10, y=20)
    
Functions `asdict` and `astuple` for converting to `dict` and `tuple`:

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

By default subclasses of dataobject are not iterable by default. If one want make it iterable then there is the option `iterable=True`:

    class Point(dataobject, iterable=True):
        x: int
        y: int

    >>> p = Point(1,2)
    >>> for x in p: print(x)
    1
    2

Another way to create subclasses of dataobject &ndash; factory function `make_dataclass`:

    >>> from recordclass import make_dataclass

    >>> Point = make_dataclass("Point", [("x",int), ("y",int)])
    
or even

    >>> Point = make_dataclass("Point", {"x":int, "y":int})

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
    
There is the options `fast_new=True`. It allows faster creation path of the instances. Here is an example:

    class FastPoint(dataobject, fast_new=True):
        x: int
        y: int
    
The followings timings explain (in jupyter notebook) boosting effect of `fast_new` option:

    %timeit l1 = [Point(i,i) for i in range(100000)]
    %timeit l2 = [FastPoint(i,i) for i in range(100000)]
    # output with python 3.9 64bit
    25.6 ms ± 2.4 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
    10.4 ms ± 426 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
    
The downside of `fast_new=True` option is less options for inspection of the instance.
    
### Using dataobject-based classes for recursive data without reference cycles

There is the option `deep_dealloc` (default value is `True`) for deallocation of recursive datastructures. 
Let consider simple example:

    class LinkedItem(dataobject, fast_new=True):
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

There is builtin more fast deallocation method using finalization mechanizm when `deep_dealloc=True`. In such case one don't need `__del__`  method for clearing the list.

> Note that for classes with `gc=True` (cyclic GC is used) this method is disabled: the python's cyclic GC is used in these cases.

For more details see notebook [example_datatypes](examples/example_datatypes.ipynb).

### Changes:

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
