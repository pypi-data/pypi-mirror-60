from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox


class Gui:
    def __init__(self, crop_widget, crop_controls_layout, images_layout):
        self.crop_widget = crop_widget
        self.crop_controls_layout = crop_controls_layout
        self.images_layout = images_layout

        images_group = QGroupBox("Images")
        images_group.setLayout(images_layout)

        crop_control_group = QGroupBox("Crop control")
        crop_control_group.setLayout(self.crop_controls_layout)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(crop_control_group)
        controls_layout.addWidget(images_group)

        layout = QVBoxLayout()
        layout.addWidget(self.crop_widget)
        layout.addLayout(controls_layout)

        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.show()



