from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox


class Main:
    def __init__(self, crop_widget, gui_crop, gui_crop_frame, gui_images):
        self.crop_widget = crop_widget
        self.crop_controls_layout = gui_crop.layout
        self.crop_frame_controls_layout = gui_crop_frame.layout
        self.images_layout = gui_images.layout
        self.gui_images = gui_images

        images_group = QGroupBox("Images")
        images_group.setLayout(self.images_layout)

        crop_control_group = QGroupBox("Crop Image")
        crop_control_group.setLayout(self.crop_controls_layout)

        crop_frame_control_group = QGroupBox("Crop Frame")
        crop_frame_control_group.setLayout(self.crop_frame_controls_layout)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(crop_control_group)
        controls_layout.addWidget(crop_frame_control_group)
        controls_layout.addWidget(images_group)

        layout = QVBoxLayout()
        layout.addWidget(self.crop_widget)
        layout.addLayout(controls_layout)

        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.show()



