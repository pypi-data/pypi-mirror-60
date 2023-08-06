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
    def __init__(self,
                 border_margin_value, border_margin_changed_cb,
                 gauss_value, gauss_changed_cb,
                 show_contour, show_contour_cb,
                 show_bounding_box, show_bounding_box_cb,
                 minimal_edge_length, minimal_edge_length_cb):
        self.border_margin_slider = MySlider(0, 150, 1, "Border Margin", border_margin_value, border_margin_changed_cb)
        self.gauss_slider = MySlider(0, 50, 2, "Gaussian Filter Width", gauss_value, gauss_changed_cb)
        self.minimal_edge_length_slider = MySlider(0, 300, 10, "Minimal square image edge length [mm]",
                                                   minimal_edge_length, minimal_edge_length_cb)

        contour_checkbox = QCheckBox("Show contour")
        contour_checkbox.setChecked(show_contour)
        contour_checkbox.toggled.connect(lambda: show_contour_cb(contour_checkbox.isChecked()))

        bounding_box_checkbox = QCheckBox("Show bounding box")
        bounding_box_checkbox.setChecked(show_bounding_box)
        bounding_box_checkbox.toggled.connect(lambda: show_bounding_box_cb(bounding_box_checkbox.isChecked()))

        self.layout = QVBoxLayout()
        self.layout.addWidget(contour_checkbox)
        self.layout.addWidget(bounding_box_checkbox)
        self.layout.addLayout(self.minimal_edge_length_slider.layout)
        self.layout.addLayout(self.border_margin_slider.layout)
        self.layout.addLayout(self.gauss_slider.layout)

    @staticmethod
    def close_app():
        QApplication.closeAllWindows()

