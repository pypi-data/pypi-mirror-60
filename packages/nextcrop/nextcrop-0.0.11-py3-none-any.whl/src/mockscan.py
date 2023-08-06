from scan import Scan
import time
import cv2


class MockScan(Scan):
    def __init__(self, dpi):
        super().__init__(dpi)
        self.images = ['data/heidi.jpg', 'data/image2.jpg']
        self.idx = -1

    def scan(self, device=None):
        self.idx += 1
        time.sleep(1)
        return cv2.imread(self.images[self.idx % 2])

