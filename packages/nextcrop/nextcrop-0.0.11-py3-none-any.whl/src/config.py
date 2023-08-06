import simple_config
import os
import argparse
import sys


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
            default='cli',
            help=(
                'ui mode'
            )
        )
        parser.add_argument(
            '-i', '--input-mode',
            choices=['files', 'scan'],
            default='files',
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
            action='store_true',
            help=(
                'Mock scanning (for development only)'
            )
        )
        parser.add_argument(
            '-x', '--framed-crop',
            action=translate_bool[defaults.framed_crop],
            help=(
                'Create a framed-crop-<name>.jpg, which frames the cropped area on the original'
                'input image or scan with a rectangle. If the image is provided by the scanner'
                '(not by -f <file>), an additional file original-<name>.jpg is created (default: False)'
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
            "minimal_edge_length": 80
        }
        return simple_config.Config(os.path.join(config_file), defaults=default_params)

    @staticmethod
    def get_config_dir():
        if os.name == 'posix':
            config_root = os.environ.get(
                'XDG_DATA_HOME',
                os.path.join(os.environ['HOME'], '.config', 'nextcrop')
            )
            os.makedirs(config_root, mode=0o700, exist_ok=True)
            return config_root

        else:
            sys.stderr.write('Not a supported platform.\n')
            sys.exit(1)

    def get_config_file(self):
        return os.path.join(self.get_config_dir(), 'config.json')

