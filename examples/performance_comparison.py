from __future__ import print_function
    
import time
import sys
import random
import datetime
from datetime import date
from typing import NamedTuple, Dict
from dataclasses import dataclass
from recordclass import RecordClass, dataobject
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass

import pandas as pd
import numpy as np

import gc

def total_size(o, handlers={}, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                   }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    default_size = sys.getsizeof(0)       # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = sys.getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=sys.stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)


##### NamedTuple #####
class PricesNamedTuple(NamedTuple("Prices", 
                         [('open', float), 
                          ('high', float), 
                          ('low', float), 
                          ('close', float)])):
    pass

class TradeDayNamedTuple(NamedTuple("TradeDay", 
                          (("symbol", str), 
                           ("dt", date), 
                           ("prices", PricesNamedTuple)))):

    def return_change(self):
        return int((self.prices.close - self.prices.open) / self.prices.open)

    def update_symbol(self, symb):
        self = self._replace(symbol = symb)



##### DataClass #####
@dataclass
class PricesDataClass: 
    open: float
    high: float
    low: float
    close: float

@dataclass
class TradeDayDataClass:
    symbol: str
    dt: date
    prices: PricesDataClass

    def return_change(self):
        return int((self.prices.close - self.prices.open) / self.prices.open)

    def update_symbol(self, symb):
        self.symbol = symb


##### RecordClass #####        
class PricesRecordClass(RecordClass):
    open: float
    high: float
    low: float
    close: float

class TradeDayRecordClass(RecordClass):
    symbol: str
    dt: date
    prices: PricesRecordClass

    def return_change(self):
        return round((self.prices.close - self.prices.open) / self.prices.open, 2)

    def update_symbol(self, symb):
        self.symbol = symb

##### dataobject #####        
class PricesDataobject(dataobject, fast_new=True):
    open: float
    high: float
    low: float
    close: float

class TradeDayDataobject(dataobject, fast_new=True):
    symbol: str
    dt: date
    prices: PricesDataobject

    def return_change(self):
        return round((self.prices.close - self.prices.open) / self.prices.open, 2)

    def update_symbol(self, symb):
        self.symbol = symb

##### Regular Python class #####
class PricesClass():
    open: float
    high: float
    low: float
    close: float

    def __init__(self, _open, _high, _low, _close):
        self.open = _open
        self.high = _high
        self.low = _low
        self.close = _close

class TradeDayClass():
    symbol: str
    dt: date
    prices: PricesRecordClass

    def __init__(self, _symbol, _dt, _prices):
        self.symbol = _symbol
        self.dt = _dt
        self.prices = _prices

    def return_change(self):
        return round((self.prices.close - self.prices.open) / self.prices.open, 2)

    def update_symbol(self, symb):
        self.symbol = symb


##### Regular Python class with slots #####
class PricesClassSlots():
    __slots__ = 'open', 'high', 'low', 'close'
    open: float
    high: float
    low: float
    close: float

    def __init__(self, _open, _high, _low, _close):
        self.open = _open
        self.high = _high
        self.low = _low
        self.close = _close

class TradeDayClassSlots():
    __slots__ = 'symbol', 'dt', 'prices'
    symbol: str
    dt: date
    prices: PricesRecordClass

    def __init__(self, _symbol, _dt, _prices):
        self.symbol = _symbol
        self.dt = _dt
        self.prices = _prices

    def return_change(self):
        return round((self.prices.close - self.prices.open) / self.prices.open, 2)

    def update_symbol(self, symb):
        self.symbol = symb


##### Python dict #####
def PricesDict(_open, _high, _low, _close):
    return {"open": _open, "high": _high, "low": _low, "close": _close}


def TradeDayDict(symbol, dt, prices):
    return {"symbol": symbol, "dt": dt, "prices": prices}

stats = {}
def run_test(objType):
    gc.collect()
    tstats = stats[objType] = {}
    print("====== %s Performance Report ======" % objType)
    print("Time it takes to create 'day' object is: ")
    TradeDay = eval("TradeDay%s" % objType)
    Prices = eval("Prices%s" % objType)
    data: Dict[str, TradeDay] = {}
    obj_count = 100000
#     stats['obj_count'] = obj_count

    st = time.time()
    for i in range(0, obj_count):
        data[i] = TradeDay("MA", datetime.date.today(), Prices(random.random(), 30.0, 5.0, 20.0))
    tstats['created'] = obj_count / (time.time() - st)
    print("%s day %s created     at: %8s per second" % (obj_count, objType, int(tstats['created'])))

    st = time.time()
    for k, v in data.items():
        d = v
    tstats['top_read'] = obj_count / (time.time() - st)
    print("%s day %s top-read    at: %8s per second" % (obj_count, objType, int(tstats['top_read'])))

    st = time.time()
    if objType == 'Dict':
        for k, v in data.items():
            d = v['prices']['open']
    else:
        for k, v in data.items():
            d = v.prices.open
    tstats['sub_read'] = obj_count / (time.time() - st)
    print("%s day %s sub-read    at: %8s per second" % (obj_count, objType, int(tstats['sub_read'])))

    st = time.time()
    if objType == 'Dict':
        for k, v in data.items():
            vprices = v['prices'] 
            d = int((vprices['close'] - vprices['open']) / vprices['open'])
    else:
        for k, v in data.items():
            vprices = v.prices
            d = int((vprices.close - vprices.open) / vprices.open)
    tstats['change'] = obj_count / (time.time() - st)
    print("%s day %s change      at: %8s per second" % (obj_count, objType, int(tstats['change'])))

    st = time.time()
    if objType == 'Dict':
        for k, v in data.items():
            v['symbol'] = "AAA"
    elif objType == 'NamedTuple':
        for k, v in data.items():
            v = v._replace(symbol="AAA")
    else:
        for k, v in data.items():
            v.symbol = "AAA"
    tstats['mutate'] = obj_count / (time.time() - st)
    print("%s day %s mutate      at: %8s per second" % (obj_count, objType, int(tstats['mutate'])))

    st = time.time()
    if objType == 'Dict':
        for k, v in data.items():
            vprices = v['prices'] 
            d = int((vprices['close'] - vprices['open']) / vprices['open'])
    else:
        for k, v in data.items():
            d = v.return_change()
    tstats['class_read'] = obj_count / (time.time() - st)
    print("%s day %s class_read      at: %8s per second" % (obj_count, objType, int(tstats['class_read'])))

    st = time.time()
    if objType == 'Dict':
        for k, v in data.items():
            v['symbol'] = "AAA"
    else:
        for k, v in data.items():
            v.update_symbol("AAA")
    tstats['class_update'] = obj_count / (time.time() - st)
    print("%s day %s class_update      at: %8s per second" % (obj_count, objType, int(tstats['class_update'])))

    tstats['size'] = total_size(data) / obj_count
    print("The size of single {}:{}: bytes".format(objType, int(tstats['size'])))


if __name__ == '__main__':
    run_test('Dict')
    run_test('Class')
    run_test('ClassSlots')
    run_test('DataClass')
    run_test('RecordClass')
    run_test('Dataobject')
    run_test('NamedTuple')
    
    pd.set_option("float_format", lambda x: "%.0f" % x)
    df = pd.DataFrame(stats)
    print(df)
    for tn in df.index:
        maxval = np.max([df[key][tn] for key in df.keys()])
        maxval = float(maxval)
        for key in df.keys():
            df[key][tn] = round(df[key][tn] / maxval, 2)
    pd.set_option("float_format", lambda x: "%.2f" % x)
    print(df)
