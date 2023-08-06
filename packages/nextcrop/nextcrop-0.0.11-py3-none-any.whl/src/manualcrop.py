from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGraphicsPolygonItem, QGraphicsScene
from PySide2.QtGui import QPen, QPolygonF
import numpy as np


def qpolygon_to_np(poly):
    """
    :param poly:  QPolygonF
    :return: np.shape = (N, 1, 2)
    """
    n = None
    for p in poly:
        a = np.round(np.array(p.toTuple()))
        b = a.reshape((-1, 1, 2))
        if n is None:
            n = b
        else:
            n = np.append(n, b, axis=0)
    return n.astype(int)


class ManualCrop:
    def __init__(self):
        self.polygon = QPolygonF()
        self.polygon_item = None
        self.done_callback = None

    def add_point(self, scene, pos):
        self.polygon.append(pos)
        if self.polygon.count() == 4:
            self.done_callback(qpolygon_to_np(self.polygon))
            self.clear(scene)

    def clear(self, scene):
        scene.removeItem(self.polygon_item)
        self.polygon_item = None
        self.polygon = QPolygonF()

    def draw(self, scene: QGraphicsScene):
        item = QGraphicsPolygonItem(self.polygon)
        item.setPen(QPen(Qt.red))
        scene.addItem(item)
        if self.polygon_item is not None:
            scene.removeItem(self.polygon_item)
        self.polygon_item = item


