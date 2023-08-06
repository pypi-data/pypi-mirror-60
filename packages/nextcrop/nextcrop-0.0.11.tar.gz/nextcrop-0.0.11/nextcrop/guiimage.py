from nextcrop import CropWidget
from PySide2.QtWidgets import QGraphicsScene
from PySide2.QtGui import QImage, QPolygonF
from PySide2.QtCore import Qt, QPointF
import numpy as np


def np_to_qimage(image):
    height, width, channel = image.shape
    bytes_per_line = 3 * width
    img = image
    return QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()


def qpolygon_to_np(poly):
    return poly


def np_to_qpolygonf(np_arr):
    """
    :param np_arr: np_arr.shape = (N, 1, 2)
    :return: QPolygonF
    """
    poly = QPolygonF()
    for xy in np_arr.squeeze():
        poly.append(QPointF(*xy))
    return poly


def np_to_qpointf(np_arr):
    """
    :param np_arr: np_arr.shape = (1, 1, 2)
    :return: QPointF
    """
    xy = np_arr.squeeze()
    return QPointF(*xy)


class GuiImage:
    # TODO kill class and move to CropWidget
    def __init__(self, crop_widget):
        self.crop_widget = crop_widget
        # self.crop_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.crop_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def set_image(self, image):
        self.crop_widget.set_image(np_to_qimage(image))

    def draw_bounding_boxes(self, bounding_boxes, delete_image_cb):
        self.crop_widget.clear_bounding_boxes()
        for (bounding_box, idx) in zip(bounding_boxes, range(0, bounding_boxes.__len__())):
            # bounding_box.shape = (4, 1, 2)
            center = np_to_qpointf(np.mean(bounding_box, axis=0))
            poly = np_to_qpolygonf(bounding_box)
            self.crop_widget.draw_bounding_box(poly, center, idx, delete_image_cb)

    def draw_contours(self, contours):
        for contour in contours:
            poly = np_to_qpolygonf(contour)
            self.crop_widget.draw_contour(poly)

    def clear_contours(self):
        self.crop_widget.clear_contours()

    def clear_bounding_boxes(self):
        self.crop_widget.clear_bounding_boxes()
