#!/usr/bin/env python3

from PIL import Image
import sys

def tiler(imgs, bg=None):
    """ Composite tiles from three cornerpieces """
    corner_sizes = {
            'z1': {
                    'xs': (64, 16),
                    's': (64, 24),
                    'm': (64, 32),
                    'l': (64, 40),
                    'xl': (64, 48)
                    },
            'z2': {
                    'xs': (128, 32),
                    's': (128, 48),
                    'm': (128, 64),
                    'l': (128, 80),
                    'xl': (128, 96)
                    },
            'z4': {
                    'xs': (256, 64),
                    's': (256, 96),
                    'm': (256, 128),
                    'l': (256, 160),
                    'xl': (256, 192)
                    },
            }

    tile_def = [
            (1, 1, 1, 1, 'm'),
            (0, 2, 1, 1, 'm'),
            (1, 0, 1, 0, 's'),
            (0, 1, 1, 0, 's'),
            (1, 1, 0, 2, 'm'),
            (0, 2, 0, 2, 'm'),
            (1, 0, 0, 1, 's'),
            (0, 1, 0, 1, 's'),
            (2, 1, 2, 1, 'l'),
            (1, 2, 2, 1, 'l'),
            (2, 0, 2, 0, 'm'),
            (1, 1, 2, 0, 'm'),
            (2, 1, 1, 2, 'l'),
            (1, 2, 1, 2, 'l'),
            (2, 0, 1, 1, 'm'),
            (2, 2, 2, 2, 'xl'),
            (0, 0, 0, 0, 'xs'),
            (0, 2, 2, 0, 'm'),
            (2, 0, 0, 2, 'm')
            ]

    def check_input():
        """Make sure the images are in correct format"""
        if len(imgs) != 3:
            raise Exception("Need 3 images instead of {}".format(len(imgs)))
        else:
            corners = [Image.open(c) for c in imgs]
        valid_widths = [64, 128, 256]
        cor_widths = [im.size[0] for im in corners]
        if cor_widths.count(cor_widths[0]) != len(corners):
            raise Exception("All input images need to be of the same width.")
        elif cor_widths[0] not in valid_widths:
            raise Exception("Width not in range {}.".format(valid_widths))
        else:
            pass
        # Make sure to return rgba
        return [im.convert('RGBA') for im in corners]

    tile_bitmaps = check_input()

    def create_tiles():
        """Composite the tiles according to rules defined earlier"""
        width = tile_bitmaps[0].size[0]
        if width == 32:
            zlevel = corner_sizes['z1']
        elif width == 64:
            zlevel = corner_sizes['z2']
        elif width == 128:
            zlevel = corner_sizes['z4']
        else:
            raise Exception("Something broke horribly.")

        tiles = []
        for tile_elev in tile_def:
            corner_types = tile_elev[:4]
            output_size = tile_elev[4]
            size = zlevel[output_size]
            tile_out = Image.new('RGBA', size=size)
            tile_out.putalpha(0)

            offsets = [
                    (0, 0),
                    (0, tile_bitmaps[corner_types[0]].size[1]-1),
                    (size[0]//2, 0),
                    (size[0]//2, tile_bitmaps[corner_types[2]].size[1]-1)
                    ]

            for i, cor_type in enumerate(corner_types):
                offset = offsets[i]
                im = tile_bitmaps[cor_type]

                # Flip corners
                if i == 1:
                    im = im.transpose(Image.FLIP_TOP_BOTTOM)
                elif i == 2:
                    im = im.transpose(Image.FLIP_LEFT_RIGHT)
                elif i == 3:
                    im = im.transpose(Image.ROTATE_180)

                tile_out.paste(im, box=offset, mask=im)
            tiles.append(tile_out)
        return tiles

    tiles = create_tiles()
    print(tiles)

    def align_tiles():
        """Align the tiles properly on a rectangular canvas"""
        alignment = {
                2: 'top',
                5: 'bottom',
                7: 'bottom',
                8: 'top',
                10: 'top',
                13: 'bottom',
                }
        max_height = tiles[0].size[0]//8*5
        size = (tiles[0].size[0], max_height)
        aligned_tiles = []
        for i, tile in enumerate(tiles):
            canvas = Image.new('RGBA', size=size)
            canvas.putalpha(1)
            height = tile.size[1]
            try:
                if alignment[i] == 'top':
                    top = 0
                elif alignment[i] == 'bottom':
                    top = max_height - height
            except KeyError:
                top = (max_height - height) // 2
            canvas.paste(tile, box=(0, top), mask=tile)
            aligned_tiles.append(canvas)
        return aligned_tiles

    aligned_tiles = align_tiles()
    for i, im in enumerate(aligned_tiles):
        im.save('im_{}.png'.format(i))

tiler(sys.argv[1:])
