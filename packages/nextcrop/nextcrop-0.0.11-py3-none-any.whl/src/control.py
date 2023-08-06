from config import Config
from cli import CLI
from uifiles import UiFiles
from files import Files
from crop import Crop
from saveimages import SaveImages
from scan import Scan, BufferedScan
from mockscan import MockScan
from uiscan import UiScan
from manualcrop import ManualCrop
from ui import Ui
from uicrop import UiCrop
from PySide2.QtWidgets import QApplication
import sys


def cli_factory(params, crop, image_loader, image_saver):
    cli = CLI(crop, image_loader, image_saver)
    cli.run()


def gui_factory(params, crop, image_loader, image_saver):
    manual_crop = ManualCrop()

    ctrl_images_cls = {'files': UiFiles,
                       'scan': UiScan}
    ctrl_images = ctrl_images_cls[params.input_mode]

    app = QApplication()
    ui_crop = UiCrop(crop, manual_crop,
                     show_bounding_boxes=True,
                     show_contours=True,
                     minimal_edge_length=params.minimal_edge_length)
    ui = Ui(ui_crop, ctrl_images(ui_crop, image_loader, image_saver))
    sys.exit(app.exec_())


class Control:
    @staticmethod
    def get_params(cfg: Config):
        config_file = cfg.get_config_file()
        config_params = cfg.get_config_params(config_file)
        return cfg.parse_commandline_options(config_params)

    def run(self):
        params = self.get_params(Config())

        # common Dependencies
        crop = Crop(params)

        scan_cls = {False: Scan, True: MockScan}

        # Image loaders: Files or BufferedScan
        image_loaders = {'files': Files(params.filename),
                         'scan': BufferedScan(scan_cls[params.mock_scanning](params.dpi))}
        image_loader = image_loaders[params.input_mode]

        # Image saver
        image_saver = SaveImages()

        ui_modes = {'cli': cli_factory, 'gui': gui_factory}
        ui_modes[params.ui_mode](params, crop, image_loader, image_saver)

