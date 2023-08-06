from nextcrop import ManualCrop, CropWidget, CropImagesWithFrame
from PySide2.QtGui import QImage


def np_to_qimage(image):
    height, width, channel = image.shape
    bytes_per_line = 3 * width
    img = image
    return QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()


class UiCropImage:
    '''
    Controller for image crop

    '''
    def __init__(self,
                 ui_crop_frame,  # UiCropFrame
                 crop,  # Crop
                 manual_crop: ManualCrop,
                 crop_widget: CropWidget,
                 annotate_image,  # AnnotateImage  TODO rename
                 crop_params,  # TODO remove
                 gui_crop_params,
                 cropped_images):  # CroppedImages: struct with images, images2, transforms
        self.ui_crop_frame = ui_crop_frame
        print(f"UiCropImage: {crop}")
        self.crop = crop
        self.manual_crop = manual_crop
        self.manual_crop.done_callback = self.manual_crop_done
        self.bounding_boxes = []
        self.contours = []
        self.image = None  # Set by image loader  numpy.ndarray [h x w x 3]
        self.crop_widget = crop_widget
        self.annotate_image = annotate_image
        self.show_contours = gui_crop_params.show_contours
        self.show_bounding_boxes = gui_crop_params.show_bounding_boxes
        self.cropped_images = cropped_images

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
        image = self.image.copy()
        self.cropped_images.images, self.bounding_boxes, self.contours, self.cropped_images.transforms = \
            self.crop.crop_images(image)

        self.set_image(image)
        self.draw_bounding_boxes()
        self.draw_contours()

        self.ui_crop_frame.crop_and_show()

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

    def manual_crop_done(self, manual_bounding_box):
        """
        Callback for ManualCrop after finishing the manual cropping
        :param manual_bounding_box: np.ndarray, shape=(4,1,2)
        :return:
        """
        # bounding_box is non-aligned, non-rectangular
        image = self.image.copy()
        cropped_image, bounding_box = self.crop.crop_by_vertices(manual_bounding_box, image, border_margin=0)
        self.cropped_images.images.append(cropped_image)
        self.bounding_boxes.append(bounding_box)
        self.draw_bounding_boxes()

    def delete_image(self, idx):
        del self.cropped_images.images[idx]
        del self.bounding_boxes[idx]
        self.draw_bounding_boxes()

    def set_image(self, image):
        self.image = image
        self.crop_widget.set_image(image)

    def draw_bounding_boxes(self):
        self.annotate_image.clear_bounding_boxes()
        if self.show_bounding_boxes:
            self.annotate_image.draw_bounding_boxes(self.bounding_boxes, delete_image_cb=self.delete_image)

    def draw_contours(self):
        self.annotate_image.clear_contours()
        if self.show_contours:
            self.annotate_image.draw_contours(self.contours)

    def close_app(self):
        pass
        # self.gui_crop.close_app()
