# Recordclass library

## What is all about?

**Recordclass** is [MIT Licensed](http://opensource.org/licenses/MIT) python library.
It implements the type `mutabletuple` and factory function `recordclass`
in order to create record-like classes -- mutable variant of `collection.namedtuple` 
with the same API. Later more memory saving variants are added.

* **mutabletuple** is mutable variant of the `tuple`, which supports assignment operations. 
* **recordclass** is a factory function that create a "mutable" analog of 
  `collection.namedtuple`. It produces a subclass of `mutabletuple` with namedtuple-like API.
* **structclass** is an analog of `recordclass`. 
  It produces a class with less memory footprint (less than both recordclass-based class instances 
  and instances of class with `__slots__`) and
  `namedtuple`-like API. It's instances has no `__dict__`,
  `__weakref__` and don't support cyclic garbage collection by default (only reference counting).
  But `structclass`-created classes can support any of them.
* **arrayclass** is factory function.
  It also produces a class with same memory footprint as `structclass`-created class instances. 
  It implements an array of object. By default created class has no `__dict__`,
  `__weakref__` and don't support cyclic garbage collection. But it can add support any of them.
  
#### Since 0.10

* **dataobject** is new base class for creating subclasses, which are support the following
  properties by default 1) no `__dict__` and `__weakref__`; 2) cyclic GC support is disabled by default; 
  3) instances have less memory size than class instances with `__slots__`.
* **make_class** is a factory function for creation of `dataobject` subclasses described above.

The `dataobject`-based classes are not following `namedtuple`-like API, but `attrs`/`dataclasses`-like API.
By default, subclasses of `dataobject` doesn't support cyclic GC, but only reference counting.
As the result the instance of such class need less memory. 
The difference is equal to the size of `PyGC_Head`.

Subclasses of the `dataobject` are reasonable when reference cycles are not provided. 
For example, when all fields have values of atomic types (integer, float, strings, date and time, etc.).
The field's value also may be the instance of a subclass of `dataobject` (i.e. without GC support).
As an exception, the value of a field can be any object if our instance is not contained in this object
and in its sub-objects.

The `recordclass` library was started as a "proof of concept" for the problem of fast "mutable" 
alternative of `namedtuple` (see [question](https://stackoverflow.com/questions/29290359/existence-of-mutable-named-tuple-in-python) on stackoverflow). It was evolved further in order to provide more memory saving, fast and flexible types for representation of data objects.

Main repository for `recordclass` 
is on [bitbucket](https://bitbucket.org/intellimath/recordclass).

Here is also a simple [example](http://nbviewer.ipython.org/urls/bitbucket.org/intellimath/recordclass/raw/default/examples/what_is_recordclass.ipynb).

## Quick start:
    
### Quick start with recordclass

First load inventory:

    >>> from recordclass import recordclass, RecordClass

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
    
Example with `RecordClass` and typehints::

    class Point(RecordClass):
       x: int
       y: int

    >>> ptint(Point.__annotations__)
    {'x': <class 'int'>, 'y': <class 'int'>}
    >>> p = Point(1, 2)
    >>> print(p)
    Point(1, 2)
    >>> print(p.x, p.y)
    1 2
    >>> p.x, p.y = 10, 20
    >>> print(p)
    Point(10, 20)
    
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
    >>> p.__sizeof__() == sys.getsizeof(p) # no additional space used by GC
    True    

    >>> p.x, p.y = 10, 20
    >>> print(p)
    Point(x=10, y=20)

    >>> print(iter(p))
    [1, 2]
        
    >>> asdict(p)
    {'x':1, 'y':2}
    
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
    >>> print(p.x, p.y, p.color)
    1 2 'white'
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

## Recordclass

Recordclass was created as answer to [question](https://stackoverflow.com/questions/29290359/existence-of-mutable-named-tuple-in-python/29419745#29419745) on `stackoverflow.com`. 

`Recordclass` was designed and implemented as a type that, by api, memory footprint, and speed, would be almost identical to` namedtuple`, except that it would support assignments that could replace any element without creating a new instance, as in ` namedtuple` (support assignments ` __setitem__` / `setslice__`).

The effectiveness of a namedtuple is based on the effectiveness of the `tuple` type in python. In order to achieve the same efficiency, it was created the type `mutabletuple`. The structure (`PymutabletupleObject`) is identical to the structure of the `tuple` (`PyTupleObject`) and therefore occupies the same amount of memory as` tuple`.

`Recordclass` is defined on top of `mutabletuple` in the same way as `namedtuple` defined on top of `tuple`. Attributes are accessed via a descriptor (`itemgetset`), which provides quick access and assignment by attribute index.

The class generated by `recordclass` looks like::

    from recordclass import mutabletuple, itemgetset

    class C(mutabletuple, metaclass=recordobject):

        __fields__ = ('attr_1',...,'attr_m')

        attr_1 = itemgetset(0)
        ...
        attr_m = itemgetset(m-1)

        def __new__(cls, attr_1, ..., attr_m):
            'Create new instance of C(attr_1, ..., attr_m)'
            return mutabletuple.__new__(cls, attr_1, ..., attr_m)

etc. following the definition scheme of `namedtuple`.

As a result, `recordclass` takes up as much memory as `namedtuple`, supports fast access by `__getitem__` / `__setitem__` and by the name of the attribute through the descriptor protocol.

## Structclass

In the discussions, it was correctly noted that instances of classes with `__slots__` also support fast access to the object fields and take up less memory than` tuple` and instances of classes created using the factory function `recordclass`. This happens because instances of classes with `__slots__` do not store the number of elements, like` tuple` and others (`PyObjectVar`), but they store the number of elements and the list of attributes in their type (` PyHeapTypeObject`).

Therefore, a special class prototype was created from which, using a special metaclass `structclasstype`, classes can be created, instances of which can occupy as much in memory as instances of classes with` __slots__`, but do not use `__slots__` at all. Based on this, the factory function `structclass` can create classes, instances of which are all similar to instances created using `recordclass`, but taking up less memory space.

The class generated by `structclass` looks like::

    from recordclass import recordobjectgetset, structclasstype

    class C(recordobject, metaclass=structclasstype):

        __attrs__ = ('attr_1',...,'attr_m')

        attr_1 = recordobjectgetset(0)
        ...
        attr_m = recordobjectgetset(m-1)

        def __new__(cls, attr_1, ..., attr_m):
            'Create new instance of C(attr_1, ..., attr_m)'
            return recordobject.__new__(cls, attr_1, ..., attr_m)

etc. following the definition scheme of `recordclass`.

As a result, `structclass`-based objects takes up as much memory as `__slots__`-based instances and also have same functionality as `recordclass`-created instances.

## Comparisons

The following table explain memory footprints of `recordclass`-, `recordclass2`-base objects:

| namedtuple    |  class/\_\_slots\_\_  |  recordclass   | structclass  |
| ------------- | ----------------- | -------------- | ------------- |
|   b+s+n*p     |     b+n*p         |  b+s+n*p       |     b+n*p-g     |

where:

 * b = sizeof(`PyObject`)
 * s = sizeof(`Py_ssize_t`)
 * n = number of items
 * p = sizeof(`PyObject*`)
 * g = sizeof(PyGC_Head)

Special option `cyclic_gc=False` (by default) of `structclass` allows to disable support of the cyclic
garbage collection.
This is useful in that case when you absolutely sure that reference cycle isn't possible. 
For example, when all field values are instances of atomic types. 
As a result the size of the instance is decreased by 24 bytes::

    class S:
        __slots__ = ('a','b','c')
        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c
            
    R_gc = recordclass2('R_gc', 'a b c', cyclic_gc=True)
    R_nogc = recordclass2('R_nogc', 'a b c')
    
    s = S(1,2,3)
    r_gc = R_gc(1,2,3) 
    r_nogc = R_nogc(1,2,3)
    for o in (s, r_gc, r_nogc):
        print(sys.getsizeof(o))
    64 64 40

Here are also table with some performance counters:

|         | namedtuple    |  class/\_\_slots\_\_  |  recordclass   | structclass  |
| ------- | ------------- | ----------------- | -------------- | ------------- |
|   `new`   |    739±24 ns  |     915±35 ns    |   763±21 ns   |    889±34 ns  |
| `getattr` |   84.0±1.7 ns |    42.8±1.5 ns   |   39.5±1.0 ns |   41.7±1.1 ns |
| `setattr` |               |     50.5±1.7 ns  |   50.9±1.5 ns |   48.8±1.0 ns |


### Changes:

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


