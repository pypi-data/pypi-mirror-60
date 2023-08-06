import simple_config
import os
import argparse
import sys


class CropParams:
    def __init__(self, c):
        self.border_margin_value = c.shrink
        self.gauss_value = 15
        self.minimal_edge_length = c.minimal_edge_length
        self.spread_value = c.spread


class CropWithFrameParams:
    def __init__(self, c):
        self.border_margin_value = c.shrink
        self.gauss_value = 15
        self.minimal_edge_length = c.minimal_edge_length
        self.spread_value = c.spread


class GuiCropParams:
    def __init__(self, c):
        self.show_bounding_boxes = True
        self.show_contours = True


class Config:
    @staticmethod
    def parse_commandline_options(defaults):
        translate_bool = {False: 'store_true', True: 'store_false'}
        parser = argparse.ArgumentParser(
            description='A utility to crop multiple photos out of a scanned image.'
        )
        parser.add_argument(
            '-u', '--ui-mode',
            choices=['cli', 'gui'],
            default=defaults.ui_mode,
            help=(
                'ui mode'
            )
        )
        parser.add_argument(
            '-i', '--input-mode',
            choices=['files', 'scan'],
            default=defaults.input_mode,
            help=(
                'input mode'
            )
        )
        parser.add_argument(
            '-b', '--blank',
            action='store_true',
            help=(
                'Make a blank scan (with no photos in the scanner) '
                'for calibration.'
            )
        )
        parser.add_argument(
            '-l', '--list',
            action='store_true',
            help="List available scanning devices."
        )
        parser.add_argument(
            '-d', '--dpi',
            nargs='?',
            type=int,
            default=defaults.resolution,
            help=(
                'The resolution, in dots per inch, to use while '
                'scanning (default: 300).'
            )
        )
        parser.add_argument(
            '-e', '--minimal-edge-length',
            nargs='?',
            type=int,
            default=defaults.minimal_edge_length,
            help=(
                'Image is recognized if its area is above the area of the square with minimal edge length [mm]'
                '(default: 10).'
            )
        )
        parser.add_argument(
            '-s', '--scanner',
            nargs='?',
            default='',
            help=(
                'The scanner to use. If not specified, '
                'the system default is used.'
            )
        )
        parser.add_argument(
            '-f', '--filename',
            nargs='*',
            default='',
            help='Do not scan. Instead, load the image from the given file(s).'
        )
        parser.add_argument(
            '-k', '--shrink',
            nargs='?',
            type=int,
            default=defaults.shrink,
            help=(
                'Number of pixels to shrink the area to be cropped. Avoid a possible small '
                'white border at the cost of a slightly smaller image (default: 3)'
            )
        )
        parser.add_argument(
            '-p', '--spread',
            nargs='?',
            type=int,
            default=defaults.spread,
            help=(
                'How much to deviate from the mean background color (default: 27)'
            )
        )
        parser.add_argument(
            '-t', '--filetype',
            nargs='?',
            type=str,
            choices=['png', 'jpg'],
            default=defaults.filetype,
            help=(
                'Filetype of the cropped images (default: png)'
            )
        )
        parser.add_argument(
            '-M', '--mock-scanning',
            action='store_const',
            const='mocked',
            default='real',
            help=(
                'Mock scanning (for development only)'
            )
        )
        parser.add_argument('--crop-frame', dest='crop_frame', action='store_true',
                            help=(
                                'Crop frame of image. Old images used to have a white frame around the actual image.'
                            )
                            )
        parser.add_argument('--no-crop-frame', dest='crop_frame', action='store_false')
        parser.set_defaults(crop_frame=defaults.crop_frame)

        parser.add_argument(
            '-o', '--output-folder',
            nargs='?',
            type=str,
            default=defaults.output_folder,
            help=(
                'Cropped images are copied to the specified folder (default: output)'
            )
        )
        parser.add_argument(
            'target',
            nargs='?',
            default=os.getcwd(),
            help=(
                'The destination directory of the cropped photos '
                '(default: the current working directory).'
            )
        )
        options = parser.parse_args()
        return options

    @staticmethod
    def get_config_params(config_file):
        default_params = {
            "resolution": 300,
            "shrink": 0,
            "contrast": 5,
            "precision": 50,
            "filetype": "png",
            "framed_crop": False,
            "minimal_edge_length": 80,
            "ui_mode": "gui",
            "input_mode": "scan",
            "output_folder": "output",
            "spread": 27,
            "crop_frame": True
        }
        return simple_config.Config(os.path.join(config_file), defaults=default_params)

    @staticmethod
    def get_config_dir():
        if 'APPDATA' in os.environ:
            config_root = os.environ['APPDATA']
        elif 'XDG_CONFIG_HOME' in os.environ:
            config_root = os.environ['XDG_CONFIG_HOME']
        else:
            config_root = os.path.join(os.environ['HOME'], '.config')

        config_dir = os.path.join(config_root, 'nextcrop')
        os.makedirs(config_dir, mode=0o700, exist_ok=True)
        return config_dir

    def get_config_file(self):
        return os.path.join(self.get_config_dir(), 'config.json')

