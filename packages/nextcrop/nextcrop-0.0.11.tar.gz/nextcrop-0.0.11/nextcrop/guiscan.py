from PySide2.QtWidgets import QVBoxLayout, QPushButton


class GuiScan:
    """
    Gui for "next image/scan" button
    """
    def __init__(self):
        self.button_scan = None
        self.button_next = None
        self.layout = None

    def setup(self, next_image_cb, scan_cb):
        # Button's visibility change depending on the fsm, therefore class member
        self.button_scan = QPushButton('Scan')
        self.button_scan.clicked.connect(scan_cb)

        self.button_next = QPushButton('Next image')
        self.button_next.clicked.connect(next_image_cb)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.button_scan)
        self.layout.addWidget(self.button_next)

    # def setup(self, manual_crop: ManualCrop, next_image_cb, margin_changed_cb, border_margin, scan_cb):
    #
    #     scene = QGraphicsScene()
    #     self.crop_widget = self.gui.get_crop_widget(scene, manual_crop)
    #     self.button_next = self.gui.get_next_button(next_image_cb)
    #     border_margin_spinbox = self.gui.get_border_margin_spinbox(border_margin, margin_changed_cb)
    #
    #     self.button_scan = QPushButton('Scan')
    #     self.button_scan.clicked.connect(scan_cb)
    #
    #     next_button = self.gui.get_next_button(next_image_cb)
    #     border_margin_spinbox = self.gui.get_border_margin_spinbox(border_margin, margin_changed_cb)
    #
    #
    #     crop_controls_layout = QVBoxLayout()
    #     crop_controls_layout.addWidget(border_margin_spinbox)
    #
    #     crop_control_group = QGroupBox("Crop control")
    #     crop_control_group.setLayout(crop_controls_layout)
    #
    #
    #
    #     images_group = QGroupBox("Images")
    #     images_group.setLayout(images_layout)
    #
    #     controls_layout = QHBoxLayout()
    #     controls_layout.addWidget(crop_control_group)
    #     controls_layout.addWidget(images_group)
    #
    #     layout = QVBoxLayout()
    #     layout.addWidget(self.crop_widget)
    #     layout.addLayout(controls_layout)
    #
    #     widget = QWidget()
    #     widget.setLayout(layout)
    #     widget.show()
    #
    #     # https://machinekoder.com/how-to-not-shoot-yourself-in-the-foot-using-python-qt/
    #     timer = QTimer()
    #     timer.timeout.connect(lambda: None)
    #     timer.start(100)
    #
    #     sys.exit(app.exec_())


    def set_button_scan(self, state, txt):
        self.button_scan.setDisabled(not state)
        self.button_scan.setText(txt)

    def set_button_next(self, state, txt):
        self.button_next.setDisabled(not state)
        self.button_next.setText(txt)