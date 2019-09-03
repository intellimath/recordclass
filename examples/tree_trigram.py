#!/usr/bin/env python
# coding: utf-8

# In[1]:


import random
import sys
from collections import deque
from recordclass import dataobject
import time
import matplotlib.pyplot as plt
import math
import gc
import numpy as np


# In[2]:


def random_strings(num_strings):
    random.seed(2)
    symbols = "abcdefghijklmnopqrstuvwxyz"

    for i in range(num_strings):
        length = random.randint(5, 15)
        yield "".join(random.choices(symbols, k=length))


# In[3]:


class Node:
    #__slots__ = ("char", "count", "lo", "eq", "hi")
    __slots__ = ("char", "lo", "eq", "hi")

    def __init__(self, char):
        self.char = char
#         self.count = 0

        self.lo = None
        self.eq = None
        self.hi = None

class TernarySearchTree():
    """Ternary search tree that stores counts for n-grams
    and their subsequences.
    """

    def __init__(self, splitchar=None):
        self.root = None
        self.splitchar = splitchar

    def insert(self, string):
        self.root = self._insert(string, self.root)

    def _insert(self, string, node):
        """Insert string at a given node.
        """
        if not string:
            return node

        char, *rest = string

        if node is None:
            node = Node(char)

        if char == node.char:
            if not rest:
#                 node.count += 1
                return node
            else:
#                 if rest[0] == self.splitchar:
#                     node.count += 1
                node.eq = self._insert(rest, node.eq)

        elif char < node.char:
            node.lo = self._insert(string, node.lo)

        else:
            node.hi = self._insert(string, node.hi)

        return node

def train(N):
    tree = TernarySearchTree("#")
    grams = deque(maxlen=4)

    for token in random_strings(N):
        grams.append(token)
        tree.insert("#".join(grams))
    return tree


# In[4]:


class Node2(dataobject):
#     __fields__ = ("char", "count", "lo", "eq", "hi")
    __fields__ = ("char", "lo", "eq", "hi")
    __options__ = {'argsonly':True}
#     lo = None
#     eq = None
#     hi = None

class TernarySearchTree2():
    """Ternary search tree that stores counts for n-grams
    and their subsequences.
    """

    def __init__(self, splitchar=None):
        self.root = None
        self.splitchar = splitchar

    def insert(self, string):
        self.root = self._insert(string, self.root)

    def _insert(self, string, node):
        """Insert string at a given node.
        """
        if not string:
            return node

        char, *rest = string

        if node is None:
            node = Node2(char)

        if char == node.char:
            if not rest:
#                 node.count += 1
                return node
            else:
#                 if rest[0] == self.splitchar:
#                     node.count += 1
                node.eq = self._insert(rest, node.eq)

        elif char < node.char:
            node.lo = self._insert(string, node.lo)

        else:
            node.hi = self._insert(string, node.hi)

        return node

def train2(N):
    tree = TernarySearchTree2("#")
    grams = deque(maxlen=4)

    for token in random_strings(N):
        grams.append(token)
        tree.insert("#".join(grams))
    return tree


# In[5]:


q2 = math.sqrt(2)


# In[12]:


import gc
gc.collect()


# In[13]:


gc.collect()
ns = []
times = []
times_del = []
n = 1024 * 32
n2 = 1024 * 1024 * 2
while n < n2 + 1:
    gc.collect()
    gc.disable()
    t0 = time.time()
    tree = train(n)
    dt = time.time() - t0
    t0 = time.time()
    gc.enable()
    del tree
    gc.collect()
    gc.collect()
    dt2 = time.time() - t0
    #g = [d['collected'] for d in gc.get_stats()]
    ns.append(n)
    times.append(dt)
    times_del.append(dt2)
    print(n, "%.2f %.2f" % (dt, dt2))
    n = int(n * q2)


# In[14]:


gc.collect()
ns2 = []
times2 = []
times2_del = []
n = 1024 * 32
n2 = 1024 * 1024 * 2
while n < n2+1:
    gc.collect()
    gc.disable()
    t0 = time.time()
    tree2 = train2(n)
    dt = time.time() - t0
    t0 = time.time()
    del tree2
    dt2 = time.time() - t0
    gc.enable()
    gc.collect()
    #g = [d['collected'] for d in gc.get_stats()]
    ns2.append(n)
    times2.append(dt)
    times2_del.append(dt2)
    print(n, "%.2f %.2f" % (dt, dt2))
    n = int(n * q2)


# In[15]:


import seaborn as sb
import statsmodels
x = np.log(ns)
y = np.log(np.array(times) - np.array(times2))
sb.regplot(x, y, robust=True, fit_reg=True)
dy = y[-1] - y[1]
dx = x[-1] - x[1]
print(dy, dx)
print(dy/dx)


# In[16]:


plt.figure(figsize=(10, 4))
plt.subplot(1,2,1)
plt.title('Create tree')
plt.loglog(ns, times, marker='s', label='slots')
plt.loglog(ns2, times2, marker='o', label='dataobject')
plt.xlabel("N")
plt.ylabel("time")
plt.legend()
plt.subplot(1,2,2)
plt.title('Delete tree')
plt.loglog(ns, times_del, marker='s', label='slots')
plt.loglog(ns2, times2_del, marker='o', label='dataobject')
plt.xlabel("N")
plt.ylabel("time")
plt.legend()
plt.show()


# In[ ]:




