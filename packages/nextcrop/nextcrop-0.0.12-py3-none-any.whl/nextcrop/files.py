import cv2
from glob import glob


class Files:
    def __init__(self, inp):
        # assert type(inp) is list

        file_names = []
        for f in inp:
            file_names += glob(f)
        self.file_iter = file_names.__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        file_name = self.file_iter.__next__()
        return cv2.imread(file_name, cv2.IMREAD_COLOR)

    def next(self):
        """
        :return: In contrast to the default iterator __next__, next() returns None if no files are available anymore,
                 instead of throwing StopIteration
        """
        try:
            file_name = self.file_iter.__next__()

        except StopIteration:
            return None

        return cv2.imread(file_name, cv2.IMREAD_COLOR)


