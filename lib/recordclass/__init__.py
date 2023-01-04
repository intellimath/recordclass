# The MIT License (MIT)
# 
# Copyright (c) <2015-2022> <Shibzukhov Zaur, szport at gmail dot com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from .datatype import datatype
from ._dataobject import dataobject, astuple, asdict, clone, update, make
from ._litelist import litelist, litelist_fromargs
from ._litetuple import litetuple, mutabletuple
from .recordclass import recordclass
from .typing import RecordClass
from .dataclass import make_dataclass, make_class, join_dataclasses
# from .dataclass import make
from .dictclass import make_dictclass
from .arrayclass import make_arrayclass
from .adapter import as_dataclass

structclass = make_dataclass

__version__ = '0.18.2'
