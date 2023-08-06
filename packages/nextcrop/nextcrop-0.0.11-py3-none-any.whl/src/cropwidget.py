""" QtImageViewer.py: PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.

"""

import os.path
from PySide2.QtCore import Qt, QRectF, Signal, QPointF
from PySide2.QtGui import QImage, QPixmap, QPainterPath, QPolygonF, QPen
from PySide2.QtWidgets import QGraphicsView, QFileDialog, QGraphicsPolygonItem, QGraphicsTextItem, QGraphicsSceneMouseEvent
from manualcrop import ManualCrop


class CropWidget(QGraphicsView):
    """ PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.

    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).
    To display any other image format, you must first convert it to a QImage or QPixmap.

    Some useful image format conversion utilities:
        qimage2ndarray: NumPy ndarray <==> QImage    (https://github.com/hmeine/qimage2ndarray)
        ImageQt: PIL Image <==> QImage  (https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)

    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.
    """

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    left_mouse_button_pressed = Signal(float, float)
    right_mouse_button_pressed = Signal(float, float)
    left_mouse_button_released = Signal(float, float)
    right_mouse_button_released = Signal(float, float)
    left_mouse_button_double_clicked = Signal(float, float)
    right_mouse_button_double_clicked = Signal(float, float)

    def __init__(self, scene, manual_crop: ManualCrop):
        QGraphicsView.__init__(self, scene)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None
        self.bounding_box_scene_items = []
        self.contour_scene_items = []

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspect_ratio_mode = Qt.KeepAspectRatio

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoom_stack = []

        # Flags for enabling/disabling mouse interaction.
        self.can_zoom = True
        self.can_pan = True

        self.manual_crop = manual_crop

    def has_image(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None

    def clear_image(self):
        """ Removes the current image pixmap from the scene if it exists.
        """
        if self.has_image():
            self.scene().removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def clear_bounding_boxes(self):
        for scene_item in self.bounding_box_scene_items:
            self.scene().removeItem(scene_item)

        self.bounding_box_scene_items = []

    def clear_contours(self):
        for scene_item in self.contour_scene_items:
            self.scene().removeItem(scene_item)

        self.contour_scene_items = []

    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.has_image():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.has_image():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def set_image(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")
        if self.has_image():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene().addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))  # Set scene size to image size.
        self.update_viewer()

    def load_image_from_file(self, file_name=""):
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if len(file_name) == 0:
            file_name, dummy = QFileDialog.getOpenFileName(self, "Open image file.")
        if len(file_name) and os.path.isfile(file_name):
            image = QImage(file_name)
            self.set_image(image)

    def update_viewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.has_image():
            return
        if len(self.zoom_stack) and self.sceneRect().contains(self.zoom_stack[-1]):
            self.fitInView(self.zoom_stack[-1], self.aspect_ratio_mode)  # Show zoomed rect
        else:
            self.zoom_stack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspect_ratio_mode)  # Show entire image

    def draw_bounding_box(self, poly: QPolygonF, center: QPointF, idx: int, delete_image_cb):
        item_poly = QGraphicsPolygonItem(poly)
        item_poly.setPen(QPen(Qt.blue))
        self.scene().addItem(item_poly)
        self.bounding_box_scene_items.append(item_poly)

        # Add image number to the scene
        ti = CropNumberTextItem(idx, delete_image_cb)
        ti.setTransformOriginPoint(8, 15)
        ti.setScale(10)
        ti.setPos(center)
        self.scene().addItem(ti)
        self.bounding_box_scene_items.append(ti)

    def draw_contour(self, poly: QPolygonF):
        item_poly = QGraphicsPolygonItem(poly)
        item_poly.setPen(QPen(Qt.red))
        self.scene().addItem(item_poly)
        self.contour_scene_items.append(item_poly)

    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        self.update_viewer()

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        scene_pos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton and event.modifiers() == Qt.NoModifier:
            if self.can_pan:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.left_mouse_button_pressed.emit(scene_pos.x(), scene_pos.y())

        elif event.button() == Qt.LeftButton and event.modifiers() == Qt.ShiftModifier:
            self.manual_crop.add_point(self.scene(), scene_pos)
            self.manual_crop.draw(self.scene())

        elif event.button() == Qt.RightButton:
            if self.can_zoom:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            self.right_mouse_button_pressed.emit(scene_pos.x(), scene_pos.y())
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """
        QGraphicsView.mouseReleaseEvent(self, event)
        scene_pos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.left_mouse_button_released.emit(scene_pos.x(), scene_pos.y())
        elif event.button() == Qt.RightButton:
            if self.can_zoom:
                view_b_box = self.zoom_stack[-1] if len(self.zoom_stack) else self.sceneRect()
                selection_b_box = self.scene().selectionArea().boundingRect().intersected(view_b_box)
                self.scene().setSelectionArea(QPainterPath())  # Clear current selection area.
                if selection_b_box.isValid() and (selection_b_box != view_b_box):
                    self.zoom_stack.append(selection_b_box)
                    self.update_viewer()
            self.setDragMode(QGraphicsView.NoDrag)
            self.right_mouse_button_released.emit(scene_pos.x(), scene_pos.y())

    def mouseDoubleClickEvent(self, event):
        """ Show entire image.
        """
        scene_pos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.left_mouse_button_double_clicked.emit(scene_pos.x(), scene_pos.y())
        elif event.button() == Qt.RightButton:
            if self.can_zoom:
                self.zoom_stack = []  # Clear zoom stack.
                self.update_viewer()
            self.right_mouse_button_double_clicked.emit(scene_pos.x(), scene_pos.y())
        QGraphicsView.mouseDoubleClickEvent(self, event)


class CropNumberTextItem(QGraphicsTextItem):
    def __init__(self, idx, double_clicked_cb):
        super().__init__(str(idx + 1))
        self.idx = idx
        self.double_clicked_cb = double_clicked_cb

    def mouseDoubleClickEvent(self, event:QGraphicsSceneMouseEvent):
        self.double_clicked_cb(self.idx)