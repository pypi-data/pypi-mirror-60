from PySide2.QtWidgets import QLabel, QApplication, QWidget, QVBoxLayout, QSizePolicy
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt
import sys


class ImageWidget(QWidget):
    def __init__(self):
        super(ImageWidget, self).__init__(None)
        self.qlabel = QLabel()
        # self.qlabel.setSizePolicy(QSizePolicy.Policy. , QSizePolicy.Policy.Expanding)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.qlabel)
        self.setLayout(self.layout)
        # label.setScaledContents(True)
        self.pixmap = QPixmap("data/heidi.jpg")

    def resizeEvent(self, resize_event):
        print('-------------')
        print('old:           {}'.format(resize_event.oldSize()))
        print('new:           {}'.format(resize_event.size()))
        print('qlabel before: {}'.format(self.qlabel.size()))
        # if resize_event.oldSize() == self.qlabel.size():
        #     return
        pm = self.pixmap.scaled(resize_event.size(),
                                Qt.KeepAspectRatio,
                                Qt.SmoothTransformation)
        self.qlabel.setPixmap(pm)
        print('qlabel after:  {}'.format(self.qlabel.size()))


def main():
    app = QApplication(sys.argv)
    widget = ImageWidget()
    widget.show()

    sys.exit(app.exec_())


main()