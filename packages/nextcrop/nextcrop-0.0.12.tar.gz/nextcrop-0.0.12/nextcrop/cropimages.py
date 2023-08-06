class CropImages:
    def __init__(self, crop):
        self.crop = crop

    def run(self, image):
        cropped_img, bb, contours, xfs = self.crop.crop_images(image)
        return cropped_img, bb, contours, xfs

    def set_minimal_edge_length(self, v):
        self.crop.minimal_edge_length = v

    def set_spread(self, v):
        self.crop.spread = v

    def set_border_margin(self, v):
        self.crop.border_margin = v

    def set_gaussian_filter(self, v):
        self.crop.gaussian_filter = v