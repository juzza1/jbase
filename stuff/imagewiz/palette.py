from PIL import Image

from ttd_palette_data import ttd_palette_data as ttd_palettes

class Palette(object):
    """Palette object"""
    def __init__(self, palette, bg, neutral, onecc, twocc, act, white):
        """Initialize useful palette properties."""
        self.full = palette
        self.raw = self.flatten_palette(palette)
        self.bg = palette[bg]
        self.neutral = self.get_range(palette, neutral)
        self.onecc = self.get_range(palette, onecc)
        self.twocc = self.get_range(palette, twocc)
        self.act = self.get_range(palette, act)
        self.white = palette[white]

    def flatten_palette(self, palette):
        """Flatten the palette from a list of 3-tuples to a list of ints."""
        return [i[j] for i in palette for j in range(len(i))]

    def get_range(self, palette, args):
        """Define a range, or combine ranges from the palette"""
        pal_out = []
        # Since python a:b slice notation does not include b, add +1 to the end
        # range because we want to give precise palette indices as arguments.
        if isinstance(args[0], tuple):
            for arg in args:
                pal_out.extend(palette[arg[0]:arg[1]+1])
        else:
            pal_out.extend(palette[args[0]:args[1]+1])
        return pal_out

dos = Palette(palette=ttd_palettes['dos'],
                 bg=0,
                 neutral=((1, 197), (206, 214)),
                 twocc=(80, 87),
                 onecc=(198, 205),
                 act=(227, 254),
                 white=255)

win = Palette(palette=ttd_palettes['win'],
                 bg=0,
                 neutral=((10, 197), (206, 216), (245, 245)),
                 twocc=(80, 87),
                 onecc=(198, 205),
                 act=(217, 244),
                 white=255)

dos_toyland = Palette(palette=ttd_palettes['dos_toyland'],
                 bg=0,
                 neutral=((1, 197), (206, 214)),
                 twocc=(80, 87),
                 onecc=(198, 205),
                 act=(227, 254),
                 white=255)

win_toyland = Palette(palette=ttd_palettes['win_toyland'],
                 bg=0,
                 neutral=((10, 197), (206, 216), (245, 245)),
                 twocc=(80, 87),
                 onecc=(198, 205),
                 act=(217, 244),
                 white=255)

palettes = {'dos': dos, 'win': win,
            'dos_toyland': dos_toyland, 'win_toyland': win_toyland}

if __name__=='__main__':
    print dos.full
    print
    print dos.raw
    print
    print dos.bg
    print
    print dos.neutral
    print
    print dos.cc
    print
    print dos.act
    print
    print dos.white
    
    # Save all palettes as pngs
    for name, pal in palettes.items():
        img = Image.new('P', (16, 16))
        img.putdata(range(256))
        img.putpalette(pal.raw)
        img.save('pal_{0}.png'.format(name))
