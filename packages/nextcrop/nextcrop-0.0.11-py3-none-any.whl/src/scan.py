import subprocess
import sys
import cv2
import os
import numpy as np
import threading
from PySide2.QtCore import QThread, QObject, Signal, Slot
from queue import Queue
import time


class Worker(QObject):
    finished = Signal()

    def __init__(self, ):
        super(Worker, self).__init__()

    @Slot()
    def scan(self, scanner, images):
        print('Start scanning')
        image = scanner.scan()
        images.put(image)
        print('Scanning done')
        self.finished.emit()


class BufferedScan(QObject):
    finished = Signal()

    def __init__(self, scanner):
        super(BufferedScan, self).__init__()
        self.scanner = scanner
        self.images = Queue()

    def __iter__(self):
        return self

    def __next__(self):
        return self.images.get()

    def next(self):
        return self.images.get()

    @staticmethod
    def scan_done(cb):
        """call function which is not inherited from QObject"""
        cb()

    def scan(self, scan_done_cb):
        thread = QThread(self)
        worker = Worker()
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.scan(self.scanner, self.images))
        worker.finished.connect(lambda: self.scan_done(scan_done_cb))
        thread.start()

    def scan_thread(self, scan_done_cb):
        print('Start scanning')
        image = self.scanner.scan()
        self.images.put(image)
        print('Scanning done')
        self.finished.emit()

    def image_count(self):
        return self.images.qsize()


class Scan:
    def __init__(self, dpi):
        self.dpi = dpi

    def scan(self, device=None):
        args = ['scanimage']
        if device:
            if isinstance(device, (list, tuple)):
                device = device[1]
            args.extend(['-d', device])
        args.extend(['--resolution', str(self.dpi), '--mode', 'Color'])
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        output = process.communicate()[0]
        if process.returncode > 0:
            sys.exit(1)

        np_img = np.fromstring(output, np.uint8)
        return cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    @staticmethod
    def detect_scanners():
        process = subprocess.Popen(['scanimage', '-L'], stdout=subprocess.PIPE)
        scanners = []
        for line in process.stdout.readlines():
            line = line.decode('utf-8')
            if not line.startswith('device `'):
                continue
            line = line.strip()
            device, name = line[8:].split("' is a ", 1)
            name = '%s (%s)' % (name, device)
            scanners.append((name, device))
        return scanners

    def get_default_scanner(self):
        if 'SANE_DEFAULT_DEVICE' in os.environ:
            return os.environ['SANE_DEFAULT_DEVICE']
        scanners = self.detect_scanners()
        if not scanners:
            sys.stderr.write('No scanners found.\n')
            sys.exit(1)
        return scanners[0]

    @staticmethod
    def get_scanner_base_name(device):
        if isinstance(device, (list, tuple)):
            device = device[0]

        name = device.partition('(')[0].strip()
        print(name)
        return name

    def list_all_scanners(self):
        # List all scanners.
        for name, device in self.detect_scanners():
            print(name)




