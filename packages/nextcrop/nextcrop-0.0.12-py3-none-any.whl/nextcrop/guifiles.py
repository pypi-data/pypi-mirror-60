from PySide2.QtWidgets import QVBoxLayout, QPushButton


class GuiFiles:
    """
    Gui for "next image" button
    """
    def __init__(self):
        print(self)
        self.next_button = None
        self.layout = None

    def setup(self, next_image_cb):
        self.next_button = QPushButton('Next image')
        self.next_button.clicked.connect(next_image_cb)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.next_button)


