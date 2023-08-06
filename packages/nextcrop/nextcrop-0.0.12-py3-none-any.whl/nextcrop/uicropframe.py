from nextcrop import ManualCrop, GuiCrop, GuiImage, CropWidget


class UiCropFrame:
    def __init__(self,
                 crop,
                 crop_widget: CropWidget,
                 annotate_frame,  # must be singleton, AnnotateFrame
                 crop_params,
                 gui_crop_params,
                 cropped_images):
        print(f"UiCropFrame: {crop}")
        self.crop = crop
        self.cropped_images = cropped_images
        self.cropped_images_and_frame = []
        self.bounding_boxes = []  # list of ndarray.shape=(4,1,2)
        self.contours = []
        self.crop_widget = crop_widget
        self.annotate_frame = annotate_frame
        self.show_contours = gui_crop_params.show_contours
        self.show_bounding_boxes = gui_crop_params.show_bounding_boxes

    def minimal_edge_length_changed(self, val):
        self.crop.set_minimal_edge_length(val)
        self.crop_and_show()

    def spread_changed(self, val):
        self.crop.set_spread(val)
        self.crop_and_show()

    def contours_toggled(self, state):
        self.show_contours = state
        self.draw_contours()

    def bounding_boxes_toggled(self, state):
        self.show_bounding_boxes = state
        self.draw_bounding_boxes()

    def get_image_widget(self):
        return self.crop_widget

    def crop_and_show(self):
        # return
        # image = self.image.copy()
        self.cropped_images.images_wo_frame, self.bounding_boxes, self.contours = \
            self.crop.crop_frames(self.cropped_images.images, self.cropped_images.transforms)
        # self.set_image(image)
        self.draw_bounding_boxes()
        self.draw_contours()

    def change_margin(self, val):
        print(f"border margin changed to {val}")
        self.crop.set_border_margin(val)
        self.crop_and_show()

    def change_gauss(self, val):
        if val % 2 == 0:
            val += 1
        print("border margin changed to {val}")
        self.crop.set_gaussian_filter(val)
        self.crop_and_show()

    # def delete_image(self, idx):
    #     del self.cropped_images[idx]
    #     del self.bounding_boxes[idx]
    #     self.draw_bounding_boxes()

    # def set_image(self, image):
    #     self.crop_widget.set_image(image)

    def draw_bounding_boxes(self):
        # self.annotate_frame.clear_bounding_boxes()
        if self.show_bounding_boxes:
            self.annotate_frame.draw_bounding_boxes(self.bounding_boxes)

    def draw_contours(self):
        # self.annotate_frame.clear_contours()
        if self.show_contours:
            self.annotate_frame.draw_contours(self.contours)

    def close_app(self):
        self.gui_crop.close_app()
