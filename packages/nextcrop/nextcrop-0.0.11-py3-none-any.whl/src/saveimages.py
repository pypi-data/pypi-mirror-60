import cv2
import time
from string import ascii_lowercase
import os


class SaveImages:
    @staticmethod
    def save_images(images):
        date_name = time.strftime(
            '%Y-%m-%d-%H%M%S-',
            time.localtime(time.time())
        )

        for image, letter in zip(images, ascii_lowercase):
            fn = os.path.join('output', date_name + letter + '.jpg')
            cv2.imwrite(fn, image)

