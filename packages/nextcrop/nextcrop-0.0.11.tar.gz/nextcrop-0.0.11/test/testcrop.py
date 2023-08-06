import unittest
import cv2
from nextcrop import Crop
from collections import namedtuple
from nextcrop import Control, Files, SaveImages, CLI, CropImages
import tempfile, shutil
import os


class TestCrop(unittest.TestCase):
    def test_run(self):
        image = cv2.imread('../data/1945.jpg')
        Params = namedtuple('Params',
                            ('spread', 'shrink', 'dpi', 'minimal_edge_length'))

        params = Params(27, 0, 300, 80)
        crop_images = CropImages(Crop(*params))
        cropped_images, bounding_boxes, contours = crop_images.run(image)

        self.assertEqual(cropped_images[0].shape, (1290, 946, 3))
        self.assertEqual(cropped_images[1].shape, (943, 1291, 3))
        self.assertEqual(cropped_images[2].shape, (1290, 930, 3))
        self.assertEqual(cropped_images[3].shape, (940, 1287, 3))

    def test_cli_files(self):
        # Setup
        out_dir = tempfile.mkdtemp()

        Params = namedtuple('Params',
                            ('spread', 'border_margin', 'dpi', 'minimal_edge_length'))
        params = Params(27, 0, 300, 80)
        crop_images = CropImages(Crop(*params))
        image_loader = Files(['../data/1945.jpg'])
        image_saver = SaveImages(out_dir)

        # Run
        cli = CLI(crop_images, image_loader, image_saver)
        cli.run(crop_border=False)

        # Test
        files = os.listdir(out_dir)
        self.assertEqual(files.__len__(), 4)

        # Check the first file
        data = cv2.imread(os.path.join(out_dir, files[0]))
        self.assertEqual(data.shape, (1290, 946, 3))


if __name__ == '__main__':
    unittest.main()
