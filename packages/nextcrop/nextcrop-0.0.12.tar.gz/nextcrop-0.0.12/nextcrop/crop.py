import cv2
import numpy as np
from collections import namedtuple


class Crop:
    def __init__(self, spread, border_margin, dpi, minimal_edge_length):
        self.gaussian_filter = 15
        self.spread = spread
        self.border_margin = border_margin
        self.dpi = dpi
        self.minimal_edge_length = minimal_edge_length

    def calc_contours(self, im_input, bkg_color, spread):
        im = cv2.GaussianBlur(im_input, (self.gaussian_filter, self.gaussian_filter), 0, 0)
        lower = np.array(tuple(col - spread for col in bkg_color))
        upper = np.array(tuple(col + spread for col in bkg_color))
        mask = cv2.bitwise_not(cv2.inRange(im, lower, upper))
        im_out = cv2.bitwise_and(im_input, im_input, mask=mask)
        contours_unsorted, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # cv2.imshow('mask', mask)

        CA = namedtuple('CA', 'contour area')
        ca = [CA(c, cv2.contourArea(c)) for c in contours_unsorted]

        # cv2.drawContours(im_input, contours_unsorted, -1, (0, 255, 255), 2)

        return ca

    def crop_images(self, im_input):
        """
        :param im_input:
        :return: cropped_images:
        :returns: tuple(cropped_images, bounding_boxes)
           - cropped_images - list of ndarray
           - bounding_boxes - unaligned rects in original image

        """
        # If im_input is altered, the changes will be made visible since the image is shown only after cropping
        # cv2.imshow('debug', im_input)
        assert im_input is not None

        ca = self.calc_contours(im_input, bkg_color=(249, 237, 221), spread=self.spread)

        # Minimal edge length of image. Everything below this threshold is considered noise
        minimal_area_px = (self.dpi / 25.4 * self.minimal_edge_length) ** 2

        ca_filtered = list(filter(lambda c: c.area > minimal_area_px, ca))
        ca_sorted = sorted(ca_filtered, key=lambda c: c.area, reverse=True)
        contours = [ca.contour for ca in ca_sorted]

        cropped_images = []
        bounding_boxes = []
        xfs = []

        for contour in contours:
            vertices = self.calc_vertices(contour)
            i, b, xf = self.crop_by_vertices(vertices, im_input)
            cropped_images.append(i)
            bounding_boxes.append(b)
            xfs.append(xf)

        return cropped_images, bounding_boxes, contours, xfs

    def crop_frame(self, image, xf_image):
        """
        :param image: axis aligned
        :param xf_image: ndarray 3x3
        :return:
        """

        # 1945.jpg bkg mu=(248, 224, 204) / (gimp rgb)
        #              std=(1.8, 2.5, 3.1)
        b = 16
        image_wo_shadow = image[b:-b, b:-b]
        contour_area = self.calc_contours(image_wo_shadow, bkg_color=(204, 224, 248), spread=4)
        # cv2.imshow('image with coutour', image_wo_shadow)

        largest_contour_area = max(contour_area, key=lambda c: c.area)
        contour = largest_contour_area.contour
        vertices = self.calc_vertices(contour)

        # cv2.drawContours(image_wo_shadow, largest_contour_area.contour, -1, (100, 100, 255), 2)
        # cv2.drawContours(image_wo_shadow, vertices, -1, (100, 255, 255), 20)
        # cv2.imshow('image_wo_shadow', image_wo_shadow)
        # cv2.waitKey(0)

        cropped_image, bb_border, xf_border = self.crop_by_vertices(vertices, image_wo_shadow)

        # self.draw_polyline(image_wo_shadow, bb_border.squeeze())

        # cv2.imshow('image with bb', image_wo_shadow)
        # cv2.waitKey(0)

        # TODO rename
        xf_shadow_trans = np.eye(3)
        xf_shadow_trans[:2, 2:3] = np.array([[b], [b]])
        # xf = xf_image @ np.linalg.inv(xf_shadow_trans)
        xf = xf_image @ xf_shadow_trans

        # xf = xf_image * xf_border
        bb = cv2.transform(bb_border, self.mat_3x3_to_2x3(xf))
        return cropped_image, bb, contour

    def crop_frames(self, images, transforms):
        # cropped_images, bbs, contours, xfs = self.crop.crop_images(image)
        images_wo_frame = []

        bounding_boxes = []
        contours = []
        for image, xf in zip(images, transforms):
            img, bb, c = self.crop_frame(image, xf)
            # self.draw_polyline(image, b.squeeze())
            # cv2.namedWindow('image with bb wo border', cv2.WINDOW_NORMAL)
            # cv2.imshow('image with bb wo border', image)
            # cv2.waitKey(0)
            images_wo_frame.append(img)
            bounding_boxes.append(bb)
            contours.append(c)

        return images_wo_frame, bounding_boxes, contours

    @staticmethod
    def calc_vertices(contour):
        _, _, h, w = cv2.boundingRect(contour)
        epsilon = min(h, w) * 0.5
        o_vertices = cv2.approxPolyDP(contour, epsilon, True)
        return cv2.convexHull(o_vertices, clockwise=True)

    def crop_by_vertices(self, vertices: np.ndarray, im_input, border_margin=None):
        """
        :param vertices:
        :param im_input:
        :param border_margin:
        :return: cropped_image: ndarray with shape (h, w, 3)
                 bounding_box: ndarray with shape (4, 1, 2)
        """
        if border_margin is None:
            border_margin = self.border_margin

        # cv2.drawContours(im_input, vertices, -1, (100, 255, 255), 20)

        # todo: convexityDefects
        # angle: The rotation angle in a clockwise direction
        center, size, angle = cv2.minAreaRect(vertices)
        # box = cv2.boxPoints((center, size, angle))
        # box = np.int0(box)
        # cv2.drawContours(im_out, [box], 0, (0, 0, 255), 40)
        # cv2.circle(im_out, tuple(np.int0(p1)), 5, (100, 100, 255), 30)

        if angle < -45:
            angle = angle + 90
        elif angle > 45:
            angle = angle - 90
        print(f"angle={angle}")
        rot_mat = cv2.getRotationMatrix2D(center, angle, scale=1.0)
        result = cv2.warpAffine(im_input, rot_mat, im_input.shape[1::-1], flags=cv2.INTER_CUBIC)

        # https://stackoverflow.com/questions/43157092/applying-transformation-matrix-to-a-list-of-points-in-opencv-python
        q = cv2.transform(vertices, rot_mat)
        vu = q.squeeze()

        # drawPolyline(result, vu, color=(255, 0, 0))

        # identify upper left vertex, closest to the origin
        idx = np.logical_and(vu[:, 0] < center[0], vu[:, 1] < center[1])
        assert sum(idx) == 1, "could not find first vertex"

        # start contour at upper left vertex, which is the origin
        v = np.roll(vu, -np.where(idx)[0], axis=0)

        # self.draw_polyline(result, v, color=(200, 200, 255))

        # interior maximal bounding box
        # image: y horizontal, x vertical, 0 upper left
        # vertices: x horizontal, y vertical, 0 upper left
        # only works if vertices are CCW
        # TODO add umlaufsinn check
        x1 = max(v[0][0], v[1][0]) + border_margin
        x2 = min(v[2][0], v[3][0]) - border_margin
        y1 = max(v[0][1], v[3][1]) + border_margin
        y2 = min(v[1][1], v[2][1]) - border_margin
        v_interior = np.array([[x1, y1], [x1, y2], [x2, y2], [x2, y1]])

        trans = np.array([[x1], [y1]])

        # self.draw_polyline(result, v_interior, color=(0, 0, 255))

        # cv2.imshow('result', result)

        # Crop image
        cropped_image = result[y1:y2, x1:x2]
        # cv2.imshow('cropped_image', cropped_image)

        # Draw crop area on original image
        rot_mat_33 = self.mat_2x3_to_3x3(rot_mat)
        xf_bb_33 = np.linalg.inv(rot_mat_33)
        xf_bb_23 = self.mat_3x3_to_2x3(xf_bb_33)
        # xf_rot_inv = cv2.invertAffineTransform(rot_mat)
        bounding_box = cv2.transform(v_interior.reshape(4, 1, 2), xf_bb_23)
        # self.draw_polyline(im_input, bounding_box.squeeze())

        xf_trans = np.eye(3)
        xf_trans[:2, 2:3] = trans
        xf = xf_bb_33 @ xf_trans
        return cropped_image, bounding_box, xf

    @staticmethod
    def mat_2x3_to_3x3(xf23):
        assert xf23.shape == (2, 3)
        xf33 = np.eye(3)
        xf33[:2, :3] = xf23
        return xf33

    @staticmethod
    def mat_3x3_to_2x3(xf33):
        assert xf33.shape == (3, 3)
        return xf33[:2, :3]

    @staticmethod
    def draw_polyline(img, vertices, color=(200, 100, 0)):
        assert vertices.shape[1] == 2
        assert len(vertices.shape) == 2
        vertices_int = vertices.astype(int)
        cv2.polylines(img, [vertices_int], isClosed=True, color=color, thickness=3)

    @staticmethod
    def resize_window(img, window_name):
        screen_res = 500, 500
        scale_width = screen_res[0] / img.shape[1]
        scale_height = screen_res[1] / img.shape[0]
        scale = min(scale_width, scale_height)

        # resized window width and height
        window_width = int(img.shape[1] * scale)
        window_height = int(img.shape[0] * scale)
        cv2.resizeWindow(window_name, window_width, window_height)

    def set_minimal_edge_length(self, v):
        self.minimal_edge_length = v

    def set_spread(self, v):
        self.spread = v

    def set_border_margin(self, v):
        self.border_margin = v

    def set_gaussian_filter(self, v):
        self.gaussian_filter = v