from manualcrop import ManualCrop
from guicrop import GuiCrop
from guiimage import GuiImage


class UiCrop:
    def __init__(self, crop, manual_crop: ManualCrop, show_bounding_boxes, show_contours, minimal_edge_length):
        self.crop = crop
        self.manual_crop = manual_crop
        self.manual_crop.done_callback = self.manual_crop_done
        self.cropped_images = []
        self.bounding_boxes = []  # list of ndarray.shape=(4,1,2)
        self.contours = []
        self.image = None  # Set by image loader
        self.gui_crop = GuiCrop(border_margin_value=crop.border_margin, border_margin_changed_cb=self.change_margin,
                                gauss_value=crop.gaussian_filter, gauss_changed_cb=self.change_gauss,
                                show_bounding_box=show_bounding_boxes, show_bounding_box_cb=self.bounding_boxes_toggled,
                                show_contour=show_contours, show_contour_cb=self.contours_toggled,
                                minimal_edge_length=minimal_edge_length, minimal_edge_length_cb=self.minimal_edge_length_changed)
        self.gui_image = GuiImage(self.manual_crop)
        self.show_contours = show_contours
        self.show_bounding_boxes = show_bounding_boxes

    def minimal_edge_length_changed(self, val):
        self.crop.minimal_edge_length = val
        self.crop_and_show()

    def contours_toggled(self, state):
        self.show_contours = state
        self.draw_contours()

    def bounding_boxes_toggled(self, state):
        self.show_bounding_boxes = state
        self.draw_bounding_boxes()

    def get_image_widget(self):
        return self.gui_image.crop_widget

    def get_layout(self):
        return self.gui_crop.layout

    def crop_and_show(self):
        image = self.image.copy()
        self.cropped_images, self.bounding_boxes, self.contours = self.crop.run(image)
        self.set_image(image)
        self.draw_bounding_boxes()
        self.draw_contours()

    def change_margin(self, val):
        print(f"border margin changed to {val}")
        self.crop.border_margin = val
        self.crop_and_show()

    def change_gauss(self, val):
        if val % 2 == 0:
            val += 1
        print("border margin changed to {val}")
        self.crop.gaussian_filter = val
        self.crop_and_show()

    def manual_crop_done(self, manual_bounding_box):
        """
        Callback for ManualCrop after finishing the manual cropping
        :param manual_bounding_box: np.ndarray, shape=(4,1,2)
        :return:
        """
        # bounding_box is non-aligned, non-rectangular
        image = self.image.copy()
        cropped_image, bounding_box = self.crop.crop_by_vertices(manual_bounding_box, image, border_margin=0)
        self.cropped_images.append(cropped_image)
        self.bounding_boxes.append(bounding_box)
        self.draw_bounding_boxes()

    def delete_image(self, idx):
        del self.cropped_images[idx]
        del self.bounding_boxes[idx]
        self.draw_bounding_boxes()

    def set_image(self, image):
        self.gui_image.set_image(image)

    def draw_bounding_boxes(self):
        self.gui_image.clear_bounding_boxes()
        if self.show_bounding_boxes:
            self.gui_image.draw_bounding_boxes(self.bounding_boxes, delete_image_cb=self.delete_image)

    def draw_contours(self):
        self.gui_image.clear_contours()
        if self.show_contours:
            self.gui_image.draw_contours(self.contours)

    def close_app(self):
        self.gui_crop.close_app()
