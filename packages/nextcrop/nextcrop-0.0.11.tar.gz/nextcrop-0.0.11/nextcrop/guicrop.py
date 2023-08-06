from PySide2.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QCheckBox
from PySide2.QtCore import Qt


class MySlider:
    def __init__(self, lower, upper, step, text, value, value_changed_cb):
        self.value_changed_cb = value_changed_cb
        self.text = text
        self.label = QLabel(f"{self.text}: {value}")
        self.label.setMinimumWidth(350)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(lower)
        self.slider.setMaximum(upper)
        self.slider.setSingleStep(step)
        self.slider.setTickInterval(step)
        self.slider.setValue(value)
        self.slider.valueChanged.connect(self.value_changed)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slider)

    def value_changed(self, val):
        self.label.setText(f"{self.text}: {val}")
        self.value_changed_cb(val)


class GuiCrop:
    def __init__(self, params, gui_params, ui_crop):
                 # border_margin_changed_cb,
                 # gauss_changed_cb,
                 # show_contour_cb,
                 # show_bounding_box_cb,
                 # minimal_edge_length_cb,
                 # spread_value_cb,
                 # crop_frame_cb):
        self.border_margin_slider = MySlider(0, 150, 1, "Border Margin", params.border_margin_value, ui_crop.change_margin)
        self.gauss_slider = MySlider(0, 50, 2, "Gaussian Filter Width", params.gauss_value, ui_crop.change_gauss)
        self.minimal_edge_length_slider = MySlider(0, 300, 10, "Min image edge length",
                                                   params.minimal_edge_length, ui_crop.minimal_edge_length_changed)
        self.spread_slider = MySlider(0, 50, 1, "Background color spread", params.spread_value, ui_crop.spread_changed)

        contour_checkbox = QCheckBox("Show contour")
        contour_checkbox.setChecked(gui_params.show_contours)
        contour_checkbox.toggled.connect(lambda: ui_crop.contours_toggled(contour_checkbox.isChecked()))

        bounding_box_checkbox = QCheckBox("Show bounding box")
        bounding_box_checkbox.setChecked(gui_params.show_bounding_boxes)
        bounding_box_checkbox.toggled.connect(lambda: ui_crop.bounding_boxes_toggled(bounding_box_checkbox.isChecked()))

        # crop_frame_checkbox = QCheckBox("Crop image frame")
        # crop_frame_checkbox.setChecked(True)
        # crop_frame_checkbox.toggled.connect(lambda: crop_frame_cb(crop_frame_checkbox.isChecked()))

        self.layout = QVBoxLayout()
        self.layout.addWidget(contour_checkbox)
        self.layout.addWidget(bounding_box_checkbox)
        # self.layout.addWidget(crop_frame_checkbox)
        self.layout.addLayout(self.minimal_edge_length_slider.layout)
        self.layout.addLayout(self.border_margin_slider.layout)
        self.layout.addLayout(self.gauss_slider.layout)
        self.layout.addLayout(self.spread_slider.layout)

    def set_callbacks(self):
        pass

    @staticmethod
    def close_app():
        QApplication.closeAllWindows()

