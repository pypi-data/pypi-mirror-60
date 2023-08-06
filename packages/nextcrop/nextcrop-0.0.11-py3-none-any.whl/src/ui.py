from gui import Gui
from uicrop import UiCrop


class Ui:
    def __init__(self, ui_crop: UiCrop, ui_images):
        self.ui_crop = ui_crop
        self.ui_images = ui_images
        self.gui = Gui(self.ui_crop.get_image_widget(), self.ui_crop.get_layout(), self.ui_images.get_layout())

    # def save_images(self):
    #     self.image_saver.save(self.ui_crop.cropped_images)

    def change_margin(self, val):
        self.ui_crop.change_margin(val)

    def crop_and_show(self):
        self.ui_crop.crop_and_show()
