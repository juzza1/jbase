#!/usr/bin/env python3

from PIL import Image

maskpath = 'build'
buildpath = 'build/masks'

def create_masks(imgs, suffix, bg):
    """
    Automated mask generation from input files.
    """

    # Info about each tile corner in OpenTTD. Order is NW, SW, NE, SE
    # Each tile can be constructed from three different kinds of corners.
    # In this array, 0 means small corner, 1 medium, and 2 big.
    # Second to last value is the actual sprite offset OpenTTD uses internally
    # Also a few masks need to be aligned differently for 3d purposes.
    # They will get a separate "bounding box" for aligment. Its will be
    # determined by the highest corner of this tile.
    # Default alignment is to center the mask on top of the square canvas.
    spr = (
           (1, 1, 1, 1, "0000"),
           (0, 2, 1, 1, "0001"),
           (1, 0, 1, 0, "0002", "top"),
           (0, 1, 1, 0, "0003"),
           (1, 1, 0, 2, "0004"),
           (0, 2, 0, 2, "0005"),
           (1, 0, 0, 1, "0006"),
           (0, 1, 0, 1, "0007", "bottom"),
           (2, 1, 2, 1, "0008", "top"),
           (1, 2, 2, 1, "0009"),
           (2, 0, 2, 0, "0010", "top"),
           (1, 1, 2, 0, "0011"),
           (2, 1, 1, 2, "0012"),
           (1, 2, 1, 2, "0013", "bottom"),
           (2, 0, 1, 1, "0014"),
           (2, 2, 2, 2, "0015"),
           (0, 0, 0, 0, "0016"),
           (0, 2, 2, 0, "0017"),
           (2, 0, 0, 2, "0018")
          )

    # Convert the array to a list we are going to modify
    sprite_array = []
    for i in spr:
        sprite_array.append(list(i))
    # Replace these numbers with the actual images from imgs-param
    for i, sprite in enumerate(sprite_array):
        for j, pos in enumerate(sprite):
            if pos == 0:
                sprite_array[i][j] = Image.open(imgs[0])
            elif pos == 1:
                sprite_array[i][j] = Image.open(imgs[1])
            elif pos == 2:
                sprite_array[i][j] = Image.open(imgs[2])
            else:
                continue

    # Loop through the sprite list, creating masks for each tile
    for i, sprite in enumerate(sprite_array):
        # Width is always the width of any corner sprite * 2, since in OpenTTD
        # all tiles are the same width
        width = 2 * sprite[0].size[0]

        # Height is the sum of the heights of NW and SW corner, minus one,
        # because a tile in OpenTTD is one pixel "too short".
        height = sprite[0].size[1] + sprite[1].size[1] - 1

        # Create the empty canvas on which to paste the corners
        bbox = Image.new('RGBA', (width, height))
        # Paste the corners
        bbox.paste(sprite[0], (0, 0))
        sprite[1] = sprite[1].transpose(Image.FLIP_TOP_BOTTOM)
        bbox.paste(sprite[1], (0, sprite[0].size[1]-1))
        sprite[2] = sprite[2].transpose(Image.FLIP_LEFT_RIGHT)
        bbox.paste(sprite[2], (width/2, 0))
        sprite[3] = sprite[3].transpose(Image.ROTATE_180)
        bbox.paste(sprite[3], (width/2, sprite[2].size[1]-1))
       
        # Output canvas will be square, so width = height 
        canvas = Image.new('RGBA', (width, width), color=bg) 
        # Add alpha channel for transparent background, otherwise output image
        # might have garbage
        if not bg:
            canvas.putalpha(1)
        else:
            pass

        # If an additional argument is given, calculate a new temporary canvas
        # for 3d centering purposes
        if len(sprite) == 6:
            max_height = 0
            for spr in sprite[0:4]:
                h = spr.size[1]
                if h > max_height:
                    max_height = h
                else:
                    continue
            max_height *= 2
            temp_canvas = Image.new('RGBA', (width, max_height))
            if sprite[5] == 'top':
                temp_canvas.paste(bbox, (0, 0))
            elif sprite[5] == 'bottom':
                temp_canvas.paste(bbox, (0, max_height-height-1))
            else:
                pass
            canvas.paste(temp_canvas, (0, (width-max_height)/2), temp_canvas)
        else:
            canvas.paste(bbox, (0, (width-height)/2), bbox)

        canvas.save('{0}/{1}{2}.png'.format(buildpath, suffix, sprite[4]))

# Initialize the locations of corner sprites
c1s = '{0}/{1}'.format(maskpath, 'tile_corner_small_1x.png')
c1m = '{0}/{1}'.format(maskpath, 'tile_corner_med_1x.png')
c1b = '{0}/{1}'.format(maskpath, 'tile_corner_big_1x.png')
c2s = '{0}/{1}'.format(maskpath, 'tile_corner_small_2x.png')
c2m = '{0}/{1}'.format(maskpath, 'tile_corner_med_2x.png')
c2b = '{0}/{1}'.format(maskpath, 'tile_corner_big_2x.png')
c4s = '{0}/{1}'.format(maskpath, 'tile_corner_small_4x.png')
c4m = '{0}/{1}'.format(maskpath, 'tile_corner_med_4x.png')
c4b = '{0}/{1}'.format(maskpath, 'tile_corner_big_4x.png')

# Image tuples for zoom levels and possible future stuff
corners_1x = (c1s, c1m, c1b)
corners_2x = (c2s, c2m, c2b)
corners_4x = (c4s, c4m, c4b)

# Send the zoom-tuples to the function, creating masks
# zoom-tuple -- image suffix -- background color
create_masks(corners_1x, 'mask_8bpp_1x_', 'blue')
create_masks(corners_1x, 'mask_32bpp_1x_', None)
create_masks(corners_2x, 'mask_32bpp_2x_', None)
create_masks(corners_4x, 'mask_32bpp_4x_', None)
