# Recordclass library

**Recordclass** is [MIT Licensed](http://opensource.org/licenses/MIT) python library.
It was started as a "proof of concept" for the problem of fast "mutable"
alternative of `namedtuple` (see [question](https://stackoverflow.com/questions/29290359/existence-of-mutable-named-tuple-in-python) on stackoverflow).
It implements the type `mutabletuple`, which supports assignment operations, and factory function `recordclass` in order to create record-like classes &ndash; subclasses of the `mutabletuple`. The function `recordclass` is a variant of `collection.namedtuple`. It produces classes with the same API. It was evolved further in order to provide more memory saving, fast and flexible types for representation of data objects.

Later **recordclass** started providing tools for creating data classes that do not participate in cyclic *garbage collection* (GC) mechanism, but support only *reference counting*.
The instances of such classes have not `PyGC_Head` prefix in the memory, which decrease their size. For CPython 3.8 it saves 16 bytes, for CPython 3.4-3.7 it saves 24-32 bytes.
This may make sense in cases where it is necessary to limit the size of objects as much as possible, provided that they will never be part of circular references in the application.
For example, when an object represents a record with fields that represent simple values by convention (`int`, `float`, `str`, `date`/`time`/`datetime`, `timedelta`, etc.).
Another examples are non-recursive data structures in which all leaf elements represent simple values.
Of course, in python, nothing prevents you from “shooting yourself in the foot" by creating the reference cycle in the script or application code.
But in some cases, this can still be avoided provided that the developer understands
what he is doing and uses such classes in the code with care.

**First** ``` recodeclass` library provide the base class `dataobject`. The type of `dataobject` is special metaclass `datatype`. It control creation of subclasses of `dataobject`, which  doesn't participate in cyclic GC by default (type flag `Py_TPFLAGS_HAVE_GC=0`). As the result the instance of such class need less memory. The difference is equal to the size of `PyGC_Head`. It also tunes `basicsize` of the instances, creates descriptors for the fields and etc. All `dataobject`-based classes doesn't support `namedtuple`-like API, but rather `attrs`/`dataclasses`-like API.

**Second** it provide another one base class `datatuple` (special subclass of `dataobject`). It creates variable sized instance like subclasses of the `tuple`.

**Third** it provide factory function `make_dataclass` for creation of subclasses of `dataobject` or ``datatuple` with the specified field names.

**Four** it provide factory function `structclass` for creation of subclasses of `dataobject` with `namedtuple`-like API.

**Six** it provide the class `lightlist`, which considers as list-like *light* container in order to save memory.

Main repository for `recordclass`is on [bitbucket](https://bitbucket.org/intellimath/recordclass). 

> Note that starting from  0.13 it is a git-based repository. The old hg-based repository is [here](https://bitbucket.org/intellimath/recordclass_old).  

Here is also a simple [example](http://nbviewer.ipython.org/urls/bitbucket.org/intellimath/recordclass/raw/master/examples/what_is_recordclass.ipynb).


## Quick start

### Installation

#### Installation from directory with sources

Install:

    >>> python setup.py install

Run tests:

    >>> python test_all.py

#### Installation from PyPI

Install:

    >>> pip install recordclass

Run tests:

    >>> python -c "from recordclass.test import *; test_all()"

### Quick start with recordclass

First load inventory:

    >>> from recordclass import recordclass

Example with `recordclass`:

    >>> Point = recordclass('Point', 'x y')
    >>> p = Point(1,2)
    >>> print(p)
    Point(1, 2)
    >>> print(p.x, p.y)
    1 2             
    >>> p.x, p.y = 10, 20
    >>> print(p)
    Point(10, 20)
    >>> sys.getsizeof(p) # the output below is for 64bit cpython3.7
    40

Example with `RecordClass` and typehints::

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
    >>> p.x, p.y = 10, 20
    >>> print(p)
    Point(10, 20)
    

Now by default `recordclass`-based class instances doesn't participate in cyclic GC and therefore  they are smaller than `namedtuple`-based ones. If one want to use in it scenarios with reference cycles then one have to use option `gc=``:

    >>> Node = recordclass('Node', 'root, children', gc=1)
    
or decorator ``@enable_gc` for `RecordClass`-based classes:

    @recordclass.enable_gc
    class Node(RecordClass):
         root: 'Node'
         chilren: list

### Quick start with dataobject

First load inventory::

    >>> from recordclass import dataobject, asdict

    class Point(dataobject):
        x: int
        y: int

    >>> print(Point.__annotations__)
    {'x': <class 'int'>, 'y': <class 'int'>}

    >>> p = Point(1,2)
    >>> print(p)
    Point(x=1, y=2)

    >>> sys.getsizeof() # the output below is for 64bit python
    32
    >>> p.__sizeof__() == sys.getsizeof(p) # no additional space for cyclic GC support
    True    

    >>> p.x, p.y = 10, 20
    >>> print(p)
    Point(x=10, y=20)
    >>> for x in p: print(x)
    1
    2
    >>> asdict(p)
    {'x':1, 'y':2}
    >>> tuple(p)
    (1, 2)

Another way &ndash; factory function `make_dataclass`:

    >>> from recordclass import make_dataclass

    >>> Point = make_dataclass("Point", [("x",int), ("y",int)])

Default values are also supported::

    class CPoint(dataobject):
        x: int
        y: int
        color: str = 'white'

or

    >>> Point = make_dataclass("Point", [("x",int), ("y",int), ("color",str)], defaults=("white",))

    >>> p = CPoint(1,2)
    >>> print(p)
    Point(x=1, y=2, color='white')

Recordclasses and dataobject-based classes may be cached in order to reuse them without duplication::

    from recordclass import RecordclassStorage

    >>> rs = RecordclassStorage()
    >>> A = rs.recordclass("A", "x y")
    >>> B = rs.recordclass("A", ["x", "y"])
    >>> A is B
    True

    from recordclass import DataclassStorage

    >>> ds = DataclassStorage()
    >>> A = ds.make_dataclass("A", "x y")
    >>> B = ds.make_dataclass("A", ["x", "y"])
    >>> A is B
    True


## Comparisons

The following table explain memory footprints of `recordclass`-, `recordclass2`-base objects:

| namedtuple    |  class/\_\_slots\_\_  |  recordclass   | dataclass  |
| ------------- | ----------------- | -------------- | ------------- |
|   $b+s+n*p$     |     $b+n*p$         |  $b+s+n*p$       |     $b+n*p-g$     |

where:

 * b = sizeof(`PyObject`)
 * s = sizeof(`Py_ssize_t`)
 * n = number of items
 * p = sizeof(`PyObject*`)
 * g = sizeof(PyGC_Head)

This is useful in that case when you absolutely sure that reference cycle isn't possible.
For example, when all field values are instances of atomic types.
As a result the size of the instance is decreased by 24-32 bytes (for cpython 3.4-3.7) and by 16 bytes for cpython 3.8::

    class S:
        __slots__ = ('a','b','c')
        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c

    R_gc = recordclass('R_gc', 'a b c', gc=1)
    R_nogc = recordclass('R_nogc', 'a b c')

    s = S(1,2,3)
    r_gc = R_gc(1,2,3)
    r_nogc = R_nogc(1,2,3)
    for o in (s, r_gc, r_nogc):
        print(sys.getsizeof(o))
    64 64 40

Here are also table with some performance counters:

|         | namedtuple    |  class/\_\_slots\_\_  |  recordclass   | dataobject  |
| ------- | ------------- | ----------------- | -------------- | ------------- |
|   `new`   |    320±6 ns  |     411±8 ns    |   406±8 ns   |    113±1 ns  |
| `getattr` |   35.6±0.7 ns |    20.8±0.4 ns   |   26.8±1.8 ns |   27.7±2.3 ns |
| `setattr` |               |     24.2±0.3 ns  |   30.9±1.1 ns |   31.5±1.8 ns |


### Changes:

#### 0.14.3:

* Subclasses of `dataobject` now support iterable and hashable protocols by default.

#### 0.14.2:

* Fix compilation issue for python 3.9.

#### 0.14.1:

* Fix issue with __hash__ when subclassing recordclass-based classes.

#### 0.14:

* Add __doc__ to generated `dataobject`-based class in order to support `inspect.signature`.
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
