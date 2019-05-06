#!/usr/bin/env python

import argparse
from PIL import Image, ImageChops
import StringIO
import subprocess
import sys

from palette import palettes
import tiq

class ImageWiz(object):
    """"""

    def __init__(self, img, layers=None):
        if '.xcf' in img:
            img = self._xcf_to_png(img, layers)
        self.img = Image.open(img)

    def _xcf_to_png(self, img, layers):
        """Convert xcf file to png with xcf2png"""
        args = ['xcf2png', '--autocrop', '{0}'.format(img)]
        if layers:
            args.extend(layers)
        print args
        img = subprocess.Popen(args, stdout=subprocess.PIPE)
        img = img.stdout.read()
        img = StringIO.StringIO(img)
        return img

    def autocrop(self):
        """Autocrop transparency from image, return offsets."""
        bbox = self.img.getbbox()
        self.img = self.img.crop(bbox)
        # Only the coordinates from top left corner are needed for ttd offset
        # purposes
        return bbox[0:2]

    def composite(self, img2, mode='over'):
        """
        Various alpha compositing methods.

        Over: paste img2 over the current image.
        In: multiply the alpha values of the current image and img2, set this
        alpha for the current image.
        """
        img2 = Image.open(img2)
        if mode == 'over':
            self.img = Image.alpha_composite(self.img, img2)
        elif mode == 'in':
            alpha_1 = self.img.split()[3]
            alpha_2 = img2.split()[3]
            alpha_1 = ImageChops.multiply(alpha_1, alpha_2)
            self.img.putalpha(alpha_1)
        else:
            print "Unknown mode: {0}".format(mode)
            sys.exit()

    def resize(self, size, mode='aa'):
        """Resize image."""
        modes = {'nearest': Image.NEAREST,
                 'bilinear': Image.BILINEAR,
                 'bicubic': Image.BICUBIC,
                 'aa': Image.ANTIALIAS}
        try:
            size = float(size)
            size = (int(round(self.img.size[0]*size)),
                    int(round(self.img.size[1]*size)))
        except ValueError:
            if 'x' in size:
                size = size.split('x')
                if not size[0]:
                    pct = int(size[1]) / float(self.img.size[1])
                    size[0] = int(round(self.img.size[0]*pct))
                elif not size[1]:
                    pct = int(size[0]) / float(self.img.size[0])
                    size[1] = int(round(self.img.size[1]*pct))
                size = map(int, size)
                    
        # Resize method returns a copy
        self.img = self.img.resize(size, modes[mode])


    def reduce_alpha(self, value):
        """
        For every pixel with an alpha value higher than or equal to the
        parameter value, increase alpha to 255. For every other pixel reduce
        alpha to 0.
        """
        if self.img.mode == 'RGBA':
            value = int(value)
            # Get alpha band
            alpha = self.img.split()[3]
            alpha = alpha.point(lambda x: x >= value and 255)
            self.img.putalpha(alpha)
            # Transparent pixels still have color data. Change them to black.
            alpha = alpha.convert('RGBA')
            self.img = ImageChops.multiply(self.img, alpha)
        else:
            print "Image mode was not RGBA, no alpha reduced."

    def to_8bpp(self, palette, ignored_colors=None):
        """Convert to 8bpp ttd paletted image"""
        self.img = tiq.main(self.img, palette, ignored_colors)

    def save(self, name):
        """Save image as optimized png"""
        self.img.save(name, 'PNG', options='optimize')

def parse_arguments():

    palette_options = palettes.keys()
    palette_options.sort()

    # Various amounts of wtf is required to properly parse some options
    class SizeAction(argparse.Action):
        """Custom action for size argument"""
        def __call__(self, parser, namespace, values, option_string=None):
            valid_filters = ('nearest', 'bilinear', 'bicubic', 'aa')
            if len(values) == 1:
                filter_ = 'aa'
            else:
                filter_ = values[1]
                if filter_ not in valid_filters:
                    raise ValueError('Invalid filter: {0}'.format(filter_))
            setattr(namespace, self.dest, (values[0], filter_))

    class CompositeAction(argparse.Action):
        """Custom action for size argument"""
        def __call__(self, parser, namespace, values, option_string=None):
            valid_modes = ('over', 'in')
            if len(values) == 1:
                mode = 'over'
            else:
                mode = values[1]
                if mode not in valid_modes:
                    raise ValueError('Invalid mode: {0}'.format(mode))
            setattr(namespace, self.dest, (values[0], mode))

    class PaletteAction(argparse.Action):
        """Custom action for palette argument"""
        def __call__(self, parser, namespace, values, option_string=None):
            valid_palettes = palette_options
            flags = []
            if len(values) > 0:
                if values[0] not in valid_palettes:
                    palette = 'dos'
                    flags = values[0:]
                else:
                    palette = values[0]
                    flags = values[1:]
            else:
                palette = 'dos'
            setattr(namespace, self.dest, (palette, flags))

    """Command-line argument parsing"""
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter, description=
            'Various image manipulation functions for (O)TTD purposes.')

    parser.add_argument('infile', help="The input file")
    parser.add_argument('outfile', help=
            ("The output file, saved as png regardless of file\nextension."))
    
    parser.add_argument('-l', '--layers', metavar=('layer', 'layers'),
    nargs='+', help=(
            "For XCF files, the default action is to merge all\n"
            "layers. Use this argument to only merge the specified\n"
            "layers."))
    
    parser.add_argument('-c', '--composite', action=CompositeAction,
            nargs='+', metavar=('image', 'mode'), help=(
            "Composites two images together.\n\n"
            "Available modes:\n"
            "over (default)\n"
            "in"))

    parser.add_argument('-s', '--resize', metavar=('size', 'filter'),
            nargs='+', action=SizeAction,
            help=("Resize image. Optionally, set a resizing filter.\n\n"
                    "Available filters:\n"
                    "nearest\n"
                    "bilinear\n"
                    "bicubic\n"
                    "antialias"))

    parser.add_argument('-a', '--reduce-alpha', metavar='threshold',
            help="Reduce alpha")

    parser.add_argument('-r', '--autocrop', action='store_true',
            help="Crop transparent areas around the image.")

    parser.add_argument('-p', '--palette-8bpp', action=PaletteAction,
            nargs='*', metavar=('palette', 'flags'), help=
            ("Convert to 8bpp. Default palette is dos.\n\n"
            "Available palettes:\n"
            "dos (default), win, dos_toyland, win_toyland\n\n"
            "Additional flags:\n"
            "noact (no action colors)\n"
            "nocc (no cc colors)")
            .format(', '.join(palette_options)))
    args = parser.parse_args()

    img = ImageWiz(args.infile, args.layers)
    print args
    if args.composite:
        img.composite(args.composite[0], args.composite[1])
    if args.resize:
        img.resize(args.resize[0], args.resize[1])
    if args.reduce_alpha:
        img.reduce_alpha(args.reduce_alpha)
    if args.autocrop:
        img.autocrop()
    if args.palette_8bpp:
        pal = palettes[args.palette_8bpp[0]]
        # Parse optional arguments for 8bpp conversion
        ignored_colors = []
        if args.palette_8bpp[1]:
            for i in args.palette_8bpp[1]:
                if i == 'noact':
                    ignored_colors.extend(pal.act)
                elif i == 'nocc':
                    ignored_colors.extend(pal.onecc)
                else:
                    raise Exception('Unknown option: {0}'.format(i))
        img.to_8bpp(pal, ignored_colors)
    img.save(args.outfile)
        

if __name__ == '__main__':
    # Do tests if only 'test' argument is given
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            tester = 'tester.png'
            tester2 = 'tester2.png'

            # Test image reading
            opening = ImageWiz(tester)
            print('Opening "{0}" successful!').format(tester)

            # Test autocrop
            cropped = ImageWiz(tester)
            offsets = cropped.autocrop()
            cropped.save('tester_cropped.png')
            print('Autocropping "{0}"successful! Offsets are: {1}')\
                    .format(tester, offsets)

            # Test alpha flattening
            val = 100
            alphareduce = ImageWiz(tester)
            alphareduce.reduce_alpha(val)
            alphareduce.save('tester_reduce_alpha.png')
            print('Alpha flattening "{0}" with value {1} successful!')\
                    .format(tester, val)
                
            # Test resizing
            size = 0.5
            resized = ImageWiz(tester)
            resized.resize(size)
            resized.save('tester_resize_float.png')
            print('Resizing "{0}" to size {1} successful!').format(tester, size)

            size = 'x50'
            resized = ImageWiz(tester)
            resized.resize(size)
            resized.save('tester_resize_const.png')
            print('Resizing "{0}" to size {1} successful!').format(tester, size)

            # Test compositing
            over = ImageWiz(tester)
            over.composite(tester2, 'over')
            over.save('tester_composite_over.png')
            print('Alpha compositing {1} over {0} successful!').format(
                    tester, tester2)

            in_ = ImageWiz(tester)
            in_.composite(tester2, 'in')
            in_.save('tester_composite_in.png')
            print('Alpha compositing {1} in {0} successful!').format(
                    tester, tester2)

            # Test 8bpp
            olden_dos = ImageWiz(tester)
            olden_dos.to_8bpp(palettes['dos'])
            olden_dos.save('tester_8bpp_dos.png')
            print('Conversion of {0} to dos 8bpp successful!').format(tester)

            # Test 8bpp
            olden_win = ImageWiz(tester)
            olden_win.to_8bpp(palettes['win'])
            olden_win.save('tester_8bpp_win.png')
            print('Conversion of {0} to win 8bpp successful!').format(tester)

        else:
            parse_arguments()
