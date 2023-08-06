from nextcrop import (
    Config, CLI, UiFiles, Files, Crop, SaveImages, BufferedScan, MockScan, UiScan, ManualCrop, UiCropImage, Scan,
    CropImages, CropImagesWithFrame, CropParams, CropWithFrameParams, GuiCropParams, GuiCrop, GuiImage, CropWidget,
    GuiScan, GuiFiles, AnnotateImage, AnnotateFrame, UiCropFrame)

from nextcrop import gui
from PySide2.QtWidgets import QApplication
import sys
from dependency_injector import containers, providers


class QApplicationRunner:
    """
    QApplication() must be run before any other Qt invocations
    """
    def __init__(self):
        self.app = QApplication()

    def run(self):
        sys.exit(self.app.exec_())


class GuiMode:
    def __init__(self, q_application_runner, ui_images, gui):
        # TODO ui_images needed?
        self.ui_images = ui_images
        self.gui = gui
        q_application_runner.run()


class CliMode:
    def __init__(self, cli, crop_frame):
        cli.run(crop_frame)


class CroppedImages:
    def __init__(self):
        self.images = None  # cropped images: listnumpy.ndarray [h x w x 3]
        self.images_wo_frame = None  # cropped frame: list
        self.transforms = None

    def get_cropped_images(self):
        if self.images_wo_frame is None:
            return self.images
        else:
            return self.images_wo_frame


def composition(config):
    crop_factory = providers.Factory(Crop,
                                     spread=config.spread,
                                     border_margin=config.shrink,
                                     dpi=config.dpi,
                                     minimal_edge_length=config.minimal_edge_length)

    # crop_images_factory = providers.Factory(CropImages, crop_core_factory)
    # crop_images_with_frame_factory = providers.Factory(CropImagesWithFrame, crop_core_factory)


    manual_crop_singleton = providers.Singleton(ManualCrop)
    files_factory = providers.Factory(Files,
                                      config.filename)

    mocked_scanner_factory = providers.Factory(MockScan,
                                               dpi=config.dpi)
    real_scanner_factory = providers.Factory(Scan,
                                             dpi=config.dpi)

    scanner_factories = dict(real=real_scanner_factory, mocked=mocked_scanner_factory)

    buffered_scan_factory = providers.Factory(BufferedScan,
                                              scanner=scanner_factories[config.mock_scanning])

    image_loader_factories = dict(files=files_factory,
                                  scan=buffered_scan_factory)
    image_loader_factory = image_loader_factories[config.input_mode]

    image_saver_factory = providers.Factory(SaveImages,
                                            config.output_folder)

    crop_params_factory = providers.Factory(CropParams, config)
    crop_frame_params_factory = providers.Factory(CropWithFrameParams, config)
    gui_crop_params_factory = providers.Factory(GuiCropParams, config)

    crop_widget_singleton = providers.Singleton(CropWidget, manual_crop_singleton)
    gui_image_singleton = providers.Factory(GuiImage, crop_widget_singleton)
    annotate_image_singleton = providers.Factory(AnnotateImage, crop_widget_singleton)

    cropped_images_singleton = providers.Singleton(CroppedImages)

    annotate_frame_singleton = providers.Factory(AnnotateFrame, crop_widget_singleton)
    ui_crop_frame_singleton = providers.Singleton(UiCropFrame,
                                                  crop=crop_factory,
                                                  crop_widget=crop_widget_singleton,
                                                  annotate_frame=annotate_frame_singleton,
                                                  crop_params=crop_params_factory,
                                                  gui_crop_params=gui_crop_params_factory,
                                                  cropped_images=cropped_images_singleton)

    ui_crop_image_singleton = providers.Singleton(UiCropImage,
                                                  ui_crop_frame=ui_crop_frame_singleton,
                                                  crop=crop_factory,
                                                  manual_crop=manual_crop_singleton,
                                                  crop_widget=crop_widget_singleton,
                                                  annotate_image=annotate_image_singleton,
                                                  crop_params=crop_params_factory,
                                                  gui_crop_params=gui_crop_params_factory,
                                                  cropped_images=cropped_images_singleton)

    gui_crop_singleton = providers.Singleton(GuiCrop,
                                             crop_params_factory,
                                             gui_crop_params_factory,
                                             ui_crop_image_singleton)
    gui_crop_frame_singleton = providers.Singleton(GuiCrop,
                                                   crop_params_factory,
                                                   gui_crop_params_factory,
                                                   ui_crop_frame_singleton)
    gui_scan_singleton = providers.Singleton(GuiScan)
    gui_files_singleton = providers.Singleton(GuiFiles)
    gui_images_singletons = dict(scan=gui_scan_singleton,
                                 files=gui_files_singleton)
    gui_images_singleton = gui_images_singletons[config.input_mode]

    # same as ui_scan_factory TODO rename

    ui_scan_factory = providers.Factory(UiScan,
                                        ui_crop_image_singleton,
                                        gui_scan_singleton,
                                        image_loader_factory,
                                        image_saver_factory)

    ui_files_factory = providers.Factory(UiFiles,
                                         ui_crop_image_singleton,
                                         gui_files_singleton,
                                         image_loader_factory,
                                         image_saver_factory)

    ui_images_factories = dict(scan=ui_scan_factory,
                               files=ui_files_factory)
    ui_images_factory = ui_images_factories[config.input_mode]

    gui_factory = providers.Factory(gui.Main,
                                    crop_widget_singleton,
                                    gui_crop_singleton,
                                    gui_crop_frame_singleton,
                                    gui_images_singleton)

    q_application_runner_factory = providers.Factory(QApplicationRunner)
    gui_mode_factory = providers.Factory(GuiMode,
                                         q_application_runner_factory,
                                         ui_images_factory,
                                         gui_factory)

    cli_factory = providers.Factory(CLI,
                                    crop_factory,
                                    image_loader_factory,
                                    image_saver_factory)

    cli_mode_factory = providers.Factory(CliMode,
                                         cli=cli_factory,
                                         crop_frame=config.crop_frame)

    mode_factories = dict(gui=gui_mode_factory,
                          cli=cli_mode_factory)
    return mode_factories[config.ui_mode]


class Control:
    @staticmethod
    def get_params(cfg: Config):
        config_file = cfg.get_config_file()
        config_params = cfg.get_config_params(config_file)
        return cfg.parse_commandline_options(config_params)

    def run(self):
        params = self.get_params(Config())

        main_factory = composition(params)
        main = main_factory()
