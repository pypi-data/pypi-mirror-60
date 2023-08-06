from guiscan import GuiScan
from uicrop import UiCrop
from fsmscan import FsmScan
from scan import BufferedScan
from PySide2.QtWidgets import QApplication


class UiScan:
    # """
    # Scan controller
    # """
    def __init__(self, ui_crop: UiCrop, scanner_buffer, image_saver):
        """
        :param ui_crop:
        :param scanner_buffer: BufferedScan
        :param image_saver:
        """
        self.scanner_buffer: BufferedScan = scanner_buffer
        self.image_saver = image_saver
        self.fsm = FsmScan(self)
        self.gui = GuiScan(next_image_cb=self.fsm.next,
                           scan_cb=self.fsm.scan)
        self.ui_crop = ui_crop

    def get_layout(self):
        return self.gui.layout

    # def run(self):
    #     self.gui.run(self.ui_crop.manual_crop,
    #                  next_image_cb=self.fsm.next,
    #                  scan_cb=self.fsm.scan,
    #                  margin_changed_cb=self.change_margin,
    #                  border_margin=self.ui_crop.crop.border_margin)

    def set_button_scan(self, state, txt):
        self.gui.set_button_scan(state, txt)

    def set_button_next(self, state, txt):
        self.gui.set_button_next(state, txt)

    def next_image(self):
        self.ui_crop.image = self.scanner_buffer.next()

    def scan(self):
        self.scanner_buffer.scan(self.fsm.scan_done)

    def crop_and_show(self):
        self.ui_crop.crop_and_show()

    def change_margin(self, val):
        self.ui_crop.change_margin(val)

    def save_cropped_images(self):
        self.image_saver.save_images(self.ui_crop.cropped_images)

    @staticmethod
    def exit():
        QApplication.exit()


