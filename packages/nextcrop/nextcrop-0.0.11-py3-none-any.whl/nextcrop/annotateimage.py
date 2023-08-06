import numpy as np
from PySide2.QtGui import QImage, QPolygonF
from PySide2.QtCore import QPointF


# TODO unify helpers in module/class
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


class AnnotateImage:
    def __init__(self, crop_widget):
        # self.annotate = AnnotateCore()
        self.crop_widget = crop_widget
        self.contour_scene_items = []
        self.bounding_box_scene_items = []

    def draw_bounding_boxes(self, bounding_boxes, delete_image_cb):
        self.clear_bounding_boxes()
        for (bounding_box, idx) in zip(bounding_boxes, range(0, bounding_boxes.__len__())):
            # bounding_box.shape = (4, 1, 2)
            center = np_to_qpointf(np.mean(bounding_box, axis=0))
            poly = np_to_qpolygonf(bounding_box)
            item = self.crop_widget.draw_bounding_box(poly)
            self.crop_widget.add_image_number(center, idx, delete_image_cb)
            self.bounding_box_scene_items.append(item)

    def draw_contours(self, contours):
        for contour in contours:
            poly = np_to_qpolygonf(contour)
            item_poly = self.crop_widget.draw_contour(poly)
            self.contour_scene_items.append(item_poly)

    def clear_contours(self):
        for scene_item in self.contour_scene_items:
            self.crop_widget.remove_item(scene_item)

        self.contour_scene_items = []

    def clear_bounding_boxes(self):
        # TODO move to AnnotateCore
        for scene_item in self.bounding_box_scene_items:
            self.crop_widget.remove_item(scene_item)

        self.bounding_box_scene_items = []