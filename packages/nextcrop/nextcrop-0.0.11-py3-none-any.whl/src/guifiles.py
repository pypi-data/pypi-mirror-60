from PySide2.QtWidgets import QVBoxLayout, QPushButton



class GuiFiles:
    """
    Gui for "next image" button
    """
    def __init__(self, next_image_cb):
        next_image_cb = next_image_cb
        next_button = QPushButton('Next image')
        next_button.clicked.connect(next_image_cb)

        self.layout = QVBoxLayout()
        self.layout.addWidget(next_button)


