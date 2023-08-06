from nextcrop import GuiFiles, UiCropImage


class UiFiles:
    def __init__(self, ui_crop: UiCropImage, gui: GuiFiles, image_loader, image_saver):
        """
        :param ui_crop: UiCrop
        :param image_loader: Files or BufferedScan
        :param image_saver:
        """
        self.image_loader = image_loader
        self.image_saver = image_saver
        self.gui = gui
        self.gui.setup(next_image_cb=self.next_image)
        self.ui_crop = ui_crop

        # load first image
        self.next_image()

    def get_layout(self):
        return self.gui.layout

    def next_image(self):
        # save previously cropped images
        self.image_saver.save_images(self.ui_crop.cropped_images)

        # load next image
        self.ui_crop.image = self.image_loader.next()
        if self.ui_crop.image is None:
            self.ui_crop.close_app()
        else:
            self.ui_crop.crop_and_show()

