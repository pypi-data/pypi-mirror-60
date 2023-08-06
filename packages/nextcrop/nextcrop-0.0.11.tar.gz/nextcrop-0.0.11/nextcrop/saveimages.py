import cv2
import time
from string import ascii_lowercase
import os


class SaveImages:
    def __init__(self, output_folder):
        self.output_folder = output_folder

    def save_images(self, images):
        date_name = time.strftime(
            '%Y-%m-%d-%H%M%S-',
            time.localtime(time.time())
        )

        for image, letter in zip(images, ascii_lowercase):
            if not os.path.isdir(self.output_folder):
                os.mkdir(self.output_folder)

            fn = os.path.join(self.output_folder, date_name + letter + '.jpg')
            cv2.imwrite(fn, image)

