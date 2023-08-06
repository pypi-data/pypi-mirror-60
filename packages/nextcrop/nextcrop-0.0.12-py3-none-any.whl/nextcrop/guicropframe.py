from PySide2.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QCheckBox
from PySide2.QtCore import Qt


class GuiCropFrame:
    def __init__(self, gui_crop, gui_params):
        self.gui_crop = gui_crop

        crop_frame_checkbox = QCheckBox("Crop Frame")
        crop_frame_checkbox.setChecked(gui_params.crop_frame)
        # crop_frame_checkbox.toggled.connect(lambda: ui_crop.bounding_boxes_toggled(crop_frame_checkbox.isChecked()))

        self.gui_crop.layout.insertWidget(0, crop_frame_checkbox)