# coding: utf-8

# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: nonecheck=False
# cython: embedsignature=True
# cython: initializedcheck=False
 
# The MIT License (MIT)

# Copyright (c) «2020-2023» «Shibzukhov Zaur, szport at gmail dot com»

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software - recordclass library - and associated documentation files 
# (the "Software"), to deal in the Software without restriction, including 
# without limitation the rights to use, copy, modify, merge, publish, distribute, 
# sublicense, and/or sell copies of the Software, and to permit persons to whom 
# the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

cimport cython

@cython.no_gc
@cython.final
cdef public class linkeditem[object LinkedItem, type LinkedItemType]:
    cdef object val
    cdef linkeditem next
    
@cython.final
cdef public class linkedlist[object LinkedList, type LinkedListType]:
    cdef public linkeditem start
    cdef public linkeditem end
    #
    cpdef append(self, val):
        cdef linkeditem item

        item = linkeditem.__new__(linkeditem)
        item.val = val
        item.next = None
        if self.start is None:
            self.start = item
        else:
            self.end.next = item
        self.end = item
    #
    cpdef extend(self, vals):
        cdef linkeditem item

        for val in vals:
            item = linkeditem.__new__(linkeditem)
            item.val = val
            item.next = None
            if self.start is None:
                self.start = item
                self.end = item
            else:
                self.end.next = item
    #
    cpdef pop(self):
        cdef linkeditem start

        start = self.start
        if start is None:
            raise TypeError("linkedlist is empty")

        self.start = start.next
        if start is self.end:
            self.end = None
        return start
    #
    def __dealloc__(self):
        cdef linkeditem curr
        cdef linkeditem next

        curr = self.start
        while curr is not None:
            next = curr.next
            curr.next = None
            curr = next
    #
    def __iter__(self):
        return iterlinkedlist(self)
        
@cython.final
cdef class iterlinkedlist:
    cdef linkeditem node
    
    def __init__(self, linkedlist ll):
        self.node = ll.start
    
    def __next__(self):
        cdef linkeditem node

        node =  self.node
        if node is None:
            raise StopIteration

        val = node.val
        self.node = node.next
        return val

@cython.no_gc
@cython.final
cdef public class dlinkeditem[object DLinkedItem, type DLinkedItemType]:
    cdef object val
    cdef linkeditem next
    cdef linkeditem prev

@cython.final
cdef public class dlinkedlist[object DLinkedList, type DLinkedListType]:
    cdef public dlinkeditem start
    cdef public dlinkeditem end
    #
    @cython.nonecheck(False)
    cpdef append(self, val):
        cdef dlinkeditem item
        cdef dlinkeditem end

        item = dlinkeditem.__new__(linkeditem)
        item.val = val
        item.next = None
        item.prev = None
        if self.start is None:
            self.start = item
            self.end = item
        else:
            end = self.end
            end.next = item
            item.prev = end
        self.end = item
    #
#     cpdef extend(self, vals):
#         cdef linkeditem item

#         for val in vals:
#             item = linkeditem.__new__(linkeditem)
#             item.val = val
#             item.next = None
#             if self.start is None:
#                 self.start = item
#                 self.end = item
#             else:
#                 self.end.next = item
    #
#     @cython.nonecheck(False)
#     cpdef pop(self):
#         cdef linkeditem start

#         start = self.start
#         if start is None:
#             raise TypeError("list is empty")

#         self.start = start.next
#         if start is self.end:
#             self.end = None
#         return start
    #
    @cython.nonecheck(False)
    def __dealloc__(self):
        cdef dlinkeditem curr
        cdef dlinkeditem next

        curr = self.start
        while curr is not None:
            next = curr.next
            curr.next = None
            curr.prev = None
            curr = next

    def __iter__(self):
        return iterdlinkedlist(self.start)
    
@cython.final
cdef class iterdlinkedlist:
    cdef dlinkeditem node
    #
    def __init__(self, dlinkeditem node):
        self.node = node
    #
    @cython.nonecheck(False)
    def __next__(self):
        cdef dlinkeditem node

        node =  self.node
        if node is None:
            raise StopIteration

        val = node.val
        self.node = node.next
        return val
    #
