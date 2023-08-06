from PySide2.QtWidgets import QLabel, QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QGraphicsScene, QCheckBox, QGraphicsView
from PySide2.QtGui import QPixmap, QImage, QPen, QFont
from PySide2.QtCore import Qt, Slot
import sys
from QtImageViewer import QtImageViewer
import cv2


def handle_left_click(x, y):
    row = int(y)
    column = int(x)
    print("Pixel (row="+str(row)+", column="+str(column)+")")


def main():
    # Create the QApplication.
    app = QApplication(sys.argv)

    scene = QGraphicsScene()

    # Create an image viewer widget.
    viewer = QtImageViewer(scene)

    # Set the viewer's scroll bar behaviour.
    #   Qt.ScrollBarAlwaysOff: Never show scroll bar.
    #   Qt.ScrollBarAlwaysOn: Always show scroll bar.
    #   Qt.ScrollBarAsNeeded: Show scroll bar only when zoomed.
    viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    # Load an image to be displayed.
    image = cv2.imread('data/heidi.jpg')
    height, width, channel = image.shape
    bytes_per_line = 3 * width
    img = image
    qt_image = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

    # Display the image in the viewer.
    viewer.set_image(qt_image)

    # button2 = QPushButton('asdf2')
    # scene.addWidget(button2)

    viewer.left_mouse_button_pressed.connect(handle_left_click)
    # pen = QPen(Qt.blue)
    # pen.setWidth(20)
    # scene.addRect(100, 100, 500, 500, pen)

    # add_checkbox(scene, 150, 72, 1070, 1360)
    # cb = QCheckBox('imageeee', viewer)
    # cb.setGeometry(500,500,cb.geometry().width(), cb.geometry().height())

    # add_checkbox(viewer, 150, 72, 1070, 1360)

    button = QPushButton('Next image')

    w = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(viewer)
    layout.addWidget(button)
    w.setLayout(layout)
    w.show()
    sys.exit(app.exec_())


def add_checkbox(view: QGraphicsView, x1, y1, x2, y2):
    cb = QCheckBox('imageeeeeeeeeeeeee')
    view.scene().addWidget(cb)
    # cb.setCheckState(Qt.CheckState)
    x = (x2 - x1) / 2
    y = (y2 - y1) / 2

    gs = view.mapToScene(cb.geometry().width(), cb.geometry().height())

    fs = view.mapToScene(30, 0)
    cb.setMinimumHeight(30)
    cb.setGeometry(x, y, int(gs.x()), int(gs.y()))
    font = QFont()
    font.setPointSizeF(30)
    cb.setFont(font)
    # cb.setGeometry()


main()
