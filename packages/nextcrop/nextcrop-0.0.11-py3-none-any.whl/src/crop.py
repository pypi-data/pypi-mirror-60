import cv2
import numpy as np
from collections import namedtuple


class Crop:
    def __init__(self, params):
        self.gaussian_filter = 15
        self.spread = 27
        self.border_margin = params.shrink
        self.dpi = params.dpi
        self.minimal_edge_length = params.minimal_edge_length

    def run(self, im_input):
        # If im_input is altered, the changes will be made visible since the image is shown only after cropping
        # cv2.imshow('debug', im_input)
        im = cv2.GaussianBlur(im_input, (self.gaussian_filter, self.gaussian_filter), 0, 0)
        mean = (249, 237, 221)
        lower = np.array(tuple(col - self.spread for col in mean))
        upper = np.array(tuple(col + self.spread for col in mean))
        mask = cv2.bitwise_not(cv2.inRange(im, lower, upper))
        im_out = cv2.bitwise_and(im_input, im_input, mask=mask)
        contours_unsorted, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        CA = namedtuple('CA', 'contour area')
        ca = [CA(c, cv2.contourArea(c)) for c in contours_unsorted]

        # Minimal edge length of image. Everything below this threshold is considered noise
        minimal_area_px = (self.dpi / 25.4 * self.minimal_edge_length) ** 2

        ca_filtered = list(filter(lambda c: c.area > minimal_area_px, ca))
        ca_sorted = sorted(ca_filtered, key=lambda c: c.area, reverse=True)
        contours = [ca.contour for ca in ca_sorted]

        cropped_images = []
        bounding_boxes = []

        for contour in contours:
            i, b = self.crop_by_contour(contour, im_input, im_out)
            cropped_images.append(i)
            bounding_boxes.append(b)

        return cropped_images, bounding_boxes, contours

    def crop_by_contour(self, contour, im_input, im_out=None):
        _, _, h, w = cv2.boundingRect(contour)
        epsilon = min(h, w) * 0.7
        o_vertices = cv2.approxPolyDP(contour, epsilon, True)
        vertices = cv2.convexHull(o_vertices, clockwise=True)
        return self.crop_by_vertices(vertices, im_input, im_out)

    def crop_by_vertices(self, vertices: np.ndarray, im_input, im_out=None, border_margin=None):
        if border_margin is None:
            border_margin = self.border_margin

        # cv2.drawContours(im_out, vertices, -1, (0, 255, 255), 20)

        # todo: convexityDefects
        center, size, angle = cv2.minAreaRect(vertices)
        # box = cv2.boxPoints((center, size, angle))
        # box = np.int0(box)
        # cv2.drawContours(im_out, [box], 0, (0, 0, 255), 40)
        # cv2.circle(im_out, tuple(np.int0(p1)), 5, (100, 100, 255), 30)
        # # cv2.circle(im_out, r2, 5, (100, 100, 255), 30)
        #
        #
        # return im_out
        # angle = 0
        # angle = 20
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

        # self.draw_polyline(result, v_interior, color=(0, 0, 255))

        # cv2.imshow('result', result)

        # Crop image
        cropped_image = result[y1:y2, x1:x2]
        # cv2.imshow('cropped_image', cropped_image)

        # Draw crop area on original image
        xf_rot_inv = cv2.invertAffineTransform(rot_mat)
        bounding_box = cv2.transform(v_interior.reshape(4, 1, 2), xf_rot_inv)
        # self.draw_polyline(im_input, bounding_box.squeeze())

        return cropped_image, bounding_box

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

