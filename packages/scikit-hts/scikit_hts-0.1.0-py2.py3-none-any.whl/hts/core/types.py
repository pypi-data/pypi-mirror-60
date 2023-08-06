from __future__ import annotations
import abc
import weakref
from enum import Enum
from typing import List, Optional, Callable, NamedTuple, NewType, Union

import pandas

from hts import logger

try:
    from folium import Map
except ImportError:
    logger.waring('Folium not installed, not all visualization will work')


class ExtendedEnum(Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def names(cls):
        return list(map(lambda c: c.name, cls))


class Model(ExtendedEnum):
    prophet = 'prophet'
    holt_winters = 'holt-winters'
    auto_arima = 'auto-arima'
    varmax = 'varmax'
    sarimax = 'sarimax'


class UnivariateModel(ExtendedEnum):
    arima = 'arima'
    auto_arima = 'auto-arima'
    prophet = 'prophet'
    holt_winters = 'holt-winters'


class MultivariateModel(ExtendedEnum):
    varmax = 'varmax'
    sarimax = 'sarimax'


Models = NewType('Model', Model)


class Transform(NamedTuple):
    func: Callable
    inv_func: Callable


class HierarchyVisualizerT(metaclass=abc.ABCMeta):
    tree: NAryTreeT

    def create_map(self) -> Map:
        ...


class NAryTreeT(metaclass=abc.ABCMeta):
    """
    Type definition of an NAryTree
    """
    key: str
    item: Union[pandas.Series, pandas.DataFrame]
    exogenous: List[str] = None
    children: List[Optional[NAryTreeT]]
    _parent: Optional[weakref.ref[NAryTreeT]]
    visualizer: HierarchyVisualizerT

    @property
    def parent(self):
        if self._parent:
            return self._parent()

    def __iter__(self) -> NAryTreeT:
        yield self
        for child in self.children:
            yield child

    def __getstate__(self):
        self._parent = None
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state
        for child in self.children:
            child._parent = weakref.ref(self)

    def __str__(self):
        return '{} : {}'.format(self.key, self.item)

    def num_nodes(self) -> int:
        ...

    def is_leaf(self) -> bool:
        ...

    def value_at_height(self, level: int) -> List:
        ...

    def sum_at_height(self, level) -> int:
        ...

    def get_height(self) -> int:
        ...

    def level_order_traversal(self: NAryTreeT) -> List[List[int]]:
        ...

    def traversal_level(self) -> List[NAryTreeT]:
        ...

    def add_child(self, key=None, item=None, exogenous=None) -> NAryTreeT:
        ...

    def leaf_sum(self) -> int:
        ...

    def to_pandas(self) -> pandas.DataFrame:
        ...

    def get_node_height(self, key: str) -> int:
        ...


m = Model.prophet.name
print(UnivariateModel.names())