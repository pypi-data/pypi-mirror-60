# from .control import CroppedImages


class CropImagesWithFrame:
    def __init__(self, crop):
        self.crop = crop

    def run(self, cropped_images):  # CroppedImages):
        '''
        :param cropped_images: CroppedImages with properties
        - images: list of axis aligned cropped images
        - transform: list of xf from cropped aa image to position in input image

        :return:
        '''
        # TODO rename crop_images_wo_border to crop_images_with_frame
        return self.crop_with_frame(cropped_images)

    def crop_with_frame(self, cropped_images):
        # cropped_images, bbs, contours, xfs = self.crop.crop_images(image)
        cropped_img_wo_border = []

        bbs = []
        for cropped_image, xf in zip(cropped_images.images, cropped_images.transforms):
            i, b = self.crop.crop_frame(cropped_image, xf)
            # self.draw_polyline(image, b.squeeze())
            # cv2.namedWindow('image with bb wo border', cv2.WINDOW_NORMAL)
            # cv2.imshow('image with bb wo border', image)
            # cv2.waitKey(0)

            cropped_img_wo_border.append(i)
            bbs.append(b)

        return cropped_img_wo_border, bbs

    def set_minimal_edge_length(self, v):
        self.crop.minimal_edge_length = v

    def set_spread(self, v):
        self.crop.spread = v

    def set_border_margin(self, v):
        self.crop.border_margin = v

    def set_gaussian_filter(self, v):
        self.crop.gaussian_filter = v
