# Recordclass library

**Recordclass** is [MIT Licensed](http://opensource.org/licenses/MIT) python library.
It was started as a "proof of concept" for the problem of fast "mutable"
alternative of `namedtuple` (see [question](https://stackoverflow.com/questions/29290359/existence-of-mutable-named-tuple-in-python) on [stackoverflow](https://stackoverflow.com)).
It implements a factory function `recordclass` (a variant of `collection.namedtuple`) in order to create record-like classes with the same API as  `collection.namedtuple`.
It was evolved further in order to provide more memory saving, fast and flexible types.

Later **recordclass** library started to provide record-like classes that do not participate in *cyclic garbage collection* (CGC) mechanism, but support only *reference counting* mechanism for garbage collection.
The instances of such classes havn't `PyGC_Head` prefix in the memory, which decrease their size.
This may make sense in cases where it is necessary to limit the size of objects as much as possible, provided that they will never be part of circular references in the application.
For example, when an object represents a record with fields that represent simple values by convention (`int`, `float`, `str`, `date`/`time`/`datetime`, `timedelta`, etc.).

For example, consider a class with type hints:

    class Point:
        x: int
        y: int

By contract instances of the class `Point` have attributes `x` and `y` with values of `int` type.
Assigning of values of a different types should be considered as a violation of the contract.

Another examples are non-recursive data structures in which all leaf elements represent a value of an atomic type.
Of course, in python, nothing prevent you from “shooting yourself in the foot" by creating the reference cycle in the script or application code.
But in many cases, this can still be avoided provided that the developer understands what he is doing and uses such classes in the code with care.
Another option is a use of static analyzers together with type annotations.

**First**, `recodeclass` library provide the base class `dataobject`. The type of `dataobject` is special metaclass `datatype`. It control creation of subclasses of `dataobject`, which  will not participate in CGC by default. As the result the instance of such class need less memory. It's memory footprint is similar to memory footprint of instances of the classes with `__slots__`. The difference is equal to the size of `PyGC_Head`. It also tunes `basicsize` of the instances, creates descriptors for the fields and etc. All subclasses of `dataobject` created by `class statement` support `attrs`/`dataclasses`-like API.

**Second**, it provide a factory function `make_dataclass` for creation of subclasses of `dataobject` with the specified field names. These subclasses support `attrs`/`dataclasses`-like API.
For example:

    >>> Point = make_dataclass('Point', 'x y')
    >>> p = Point(1, 2)
    >>> p.y = -1
    >>> print(p.x, p.y)
    1 -1

**Three**, it provide a factory function `make_arrayclass` in order to create subclass of `dataobject` wich can consider as array of simple values.
For example:

    >>> Pair = make_arrayclass(2)
    >>> p = Pair(2, 3)
    >>> p[1] = -1
    >>> print(p)
    Pair(2, -1)

**Four**, it provide the class `lightlist`, which considers as list-like *light* container in order to save memory.

Main repository for `recordclass`is on [bitbucket](https://bitbucket.org/intellimath/recordclass). 

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
    >>> p.x, p.y = 1, 2
    >>> print(p)
    Point(1, 2)
    >>> sys.getsizeof(p) # the output below is for 64bit cpython3.9
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
    >>> p.x, p.y = 1, 2
    >>> print(p)
    Point(1, 2)

Now by default `recordclass`-based class instances doesn't participate in CGC and therefore they are smaller than `namedtuple`-based ones. If one want to use it in scenarios with reference cycles then one have to use option `gc=True` (`gc=False` by default):

    >>> Node = recordclass('Node', 'root children', gc=True)
    
or decorator:

    @clsconfig(gc=True)
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
    >>> p.__sizeof__() == sys.getsizeof(p) # no additional space for CGC support
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
    
### Using dataobject-based classes for recursive data without recursive links

There is option `deep_dealloc` (default value is `True`) for deallocation of recursive datastructures. Let consider simple example:

    class LinkedItem(dataobject, fast_new=True):
        val: object
        next: 'LinkedItem'

    @clsconfig(deep_dealloc=True)
    class LinkedList(dataobject):
        start: LinkedItem = None
        end: LinkedItem = None

        def append(self, val):
            link = LinkedItem(val, None)
            if self.start is None:
                self.start = link
            else:
                self.end.next = link
            self.end = link

Without `deep_dealloc=True` deallocation of the instance of `LinkedList` will be failed.
But it can be resolved with `__dell__` method:

    def __del__(self):
        curr = self.start
        while curr is not None:
            next = curr.next
            curr.next = None
            curr = next

There is default more fast deallocation method (finalization mechanizm is used) when  `deep_dealloc=True`.

> Note that for classes with `gc=True` (cyclic GC is used) this method is disabled: the python's cyclic GC is used.

For more detailed examples see notebook [example_datatypes](examples/example_datatypes.ipynb).


## Memory footprint

The following table explain memory footprints of `recordclass`-base and `dataobject`-base objects:

| namedtuple    |  class with \_\_slots\_\_  |  recordclass   | dataobject |
| ------------- | ----------------- | -------------- | ------------- |
|   $g+b+s+n*p$     |     $g+b+n*p$         |  $b+s+n*p$       |     $b+n*p$     |

where:

 * b = sizeof(`PyObject`)
 * s = sizeof(`Py_ssize_t`)
 * n = number of items
 * p = sizeof(`PyObject*`)
 * g = sizeof(PyGC_Head)

This is useful in that case when you absolutely sure that reference cycle isn't supposed.
For example, when all field values are instances of atomic types.
As a result the size of the instance is decre	ased by 24-32 bytes (for cpython 3.4-3.7) and by 16 bytes for cpython 3.8::

    class S:
        __slots__ = ('a','b','c')
        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c

    R_gc = recordclass('R_gc', 'a b c', gc=True)
    R_nogc = recordclass('R_nogc', 'a b c')
    DO = make_dataclass('R_do', 'a b c')

    s = S(1,2,3)
    r_gc = R_gc(1,2,3)
    r_nogc = R_nogc(1,2,3)
    do = DO(1,2,3)
    for o in (s, r_gc, r_nogc, do):
        print(sys.getsizeof(o), end=' ')
    print
    56 64 48 32

Here are also table with some performance counters (python 3.9, debian linux, x86-64):

|         | namedtuple    |  class with \_\_slots\_\_  |  recordclass   | dataobject  |
| ------- | ------------- | ----------------- | -------------- | ------------- |
|   `new`   |    299±6 ns  |     420±9 ns    |   287±10 ns   |    106±4 ns  |
| `getattr` |   23.6±0.3 ns |    24.7±0.9 ns   |   23.0±0.2 ns |   23.1±0.7 ns |
| `setattr` |               |     27.6±0.8 ns  |   26.8±0.4 ns |   26.57±0.4 ns |

### Changes:

### 0.15

* Now library supports only Python >= 3.6
* 'gc' and 'fast_new' options now can be specified as kwargs in class statement.
* Add a function `astuple` to dataclass.py for transformation instances of dataobject-based subclasses to a tuple.
* Drop datatuple based classes.
* Define the mutabletuple type on top of litetuple types.
* Make structclass an alias of make_dataclass.
* Add option 'deep_dealloc' for deallocation of instances of dataobject-based recursive subclasses.

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
