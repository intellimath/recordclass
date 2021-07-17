cimport cython

@cython.no_gc
cdef public class linkeditem[object LinkedItem, type LinkedItemType]:
    cdef object val
    cdef linkedlist next

cdef public class linkedlist[object LinkedList, type LinkedListType]:
    cdef linkeditem start
    cdef linkeditem end
    #
    cpdef append(self, val):
        cdef linkeditem item
        
        item = linkeditem.__new__(linkeditem)
        item.val = val
        item.next = None
        if self.start is None:
            self.start = item
            self.end = item
        else:
            self.end.next = item
    #
    cpdef extend(self, vals):
        for val in vals:
            self.append(val)
    #
    def __dealloc__(self):
        cdef linkeditem curr
        cdef linkeditem next
        
        curr = self.start
        while curr is not None:
            next = curr.next                
            del curr
            curr = next
        
        
    