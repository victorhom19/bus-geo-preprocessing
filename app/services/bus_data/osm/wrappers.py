import dataclasses
from typing import Dict, Any, List

from overpy import Node as OSMNode
from sklearn.neighbors._kd_tree import KDTree


@dataclasses.dataclass
class OSMWayWrapper:
    """ Класс-обёртка над OSM Way для обеспечения возможности модификации геометрии дороги """

    id: int
    tags: Dict[str, Any]
    nodes: List[OSMNode]


class KDTreeWrapper:
    """ Класс-обёртка над Sklearn KDTree """

    # Необходимость создания обёртки над Sklearn KDTree вызвана тем, что исходный класс создаёт исключение
    # при попытке инициировать дерево пустым набором точек. Попытка обрабатывать такие случаи "на месте" загромождает
    # код условными конструкциями

    def __init__(self, X, leaf_size=2):
        """ Инициализация kd-дерева """

        if len(X) > 0:
            # Если передана непустая последовательность точек - инициализируется исходный объект Sklearn KDTree
            self.kd_tree = KDTree(X, leaf_size)
        else:
            # Иначе поле инициализируется None'ом, а не вызывается исключение
            self.kd_tree = None

    def query_radius(self, X, r, return_distance=False, sort_results=False):
        """ Запрос на поиск точек в радиусе """

        # В зависимости от того, было ли создано kd-дерево при инициализации, запрос либо перенаправляется этому
        # дереву, либо формируется пустой результат требуемой размерности (в зависимости от флагов)
        if self.kd_tree is not None:
            return self.kd_tree.query_radius(X, r, return_distance=return_distance, sort_results=sort_results)
        elif return_distance:
            return [[] for _ in X], [[] for _ in X]
        else:
            return [[] for _ in X]