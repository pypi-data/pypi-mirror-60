from nextcrop import Gui, UiCropImage


class Ui:
    def __init__(self, ui_scan, ui_crop: UiCropImage, gui_images, gui_crop):
        self.ui_scan = ui_scan # TODO pointless, but need instance
        self.ui_crop = ui_crop
        self.gui_crop = gui_crop
        self.gui_images = gui_images
        self.gui = Gui(self.ui_crop.get_image_widget(), gui_crop, gui_images)

    # def save_images(self):
    #     self.image_saver.save(self.ui_crop.cropped_images)

    def change_margin(self, val):
        self.ui_crop.change_margin(val)

    def crop_and_show(self):
        self.ui_crop.crop_and_show()
