import os
import sys

# Parse paths
buildpath = ''
srcpath = ''
with open('src/Makefile.path', 'r') as f:
    for line in f:
        if 'BUILDPATH :=' in line:
            l = line.split(':=')
            buildpath = l[1].strip()
        elif 'SRCPATH :=' in line:
            l = line.split(':=')
            srcpath = l[1].strip()

print(buildpath)
print(srcpath)

class Item(object):
    """The base class for every item (grf replacement) in this set"""
    def __init__(self, src=None, frames=[]):
        blendpath = os.path.join(srcpath, 'blend')
        self.name = os.path.basename(__file__)
        self.src = os.path.join(blendpath, src)
        self.frames = frames

        if len(sys.argv) == 3 and sys.argv[2] == 'print_dep':
            self.print_dep()

    def print_dep(self):
        outname = sys.argv[1]

        with open(outname, 'w') as f:

            if '.blend' in self.src:
                suff = {'rendered': 'rendered',
                        'zoom_4x': '4x',
                        'zoom_2x': '2x',
                        'zoom_1x': '1x',
                        'olden': '8bpp'}
                blender_args = (
                'blender --factory-startup --threads 1 --background {0} '
                '--engine CYCLES --render-output {1}_{2} --render-format PNG '
                '--render-frame {3} --use-extension 1 >> /dev/null'
                )
                depname = os.path.basename(self.src)
                depname = os.path.splitext(depname)[0] + '.blenddep'
                depname = os.path.join(buildpath, depname)
                blender_deps = open(depname, 'r').read()


                for i in self.frames:
                    rendername = os.path.join(buildpath, str(i))
                    these_args = blender_args.format(
                            self.src, rendername, suff['rendered'],
                            self.frames[i])
                    
                    f.write('full-render: {0}_{1}.png {0}_{2}.png {0}_{3}.png '
                    '{0}_{4}.png\n'.format(rendername,
                                           suff['zoom_4x'],
                                           suff['zoom_2x'],
                                           suff['zoom_1x'],
                                           suff['olden']))
                    # 4x zoom
                    f.write((
                            '{0}_{1}.png: {0}_{2}.png\n'
                            '\t$(_V) cp {0}_{2}.png {0}_{1}.png\n'
                            ).format(rendername,
                                     suff['zoom_4x'],
                                     suff['rendered']))
                    # 2x zoom
                    f.write((
                            '{0}_{1}.png: {0}_{2}.png\n'
                            '\t$(_V) convert {0}_{2}.png -resize 50% '
                            '{0}_{1}.png\n').format(rendername,
                                                    suff['zoom_2x'],
                                                    suff['rendered']))
                    # 1x zoom
                    f.write((
                            '{0}_{1}.png: {0}_{2}.png\n'
                            '\t$(_V) convert {0}_{2}.png -resize 25% '
                            '{0}_{1}.png\n').format(rendername,
                                                    suff['zoom_1x'],
                                                    suff['rendered']))
                    # 8bpp
                    f.write((
                            '{0}_{1}.png: {0}_{2}.png\n'
                            '\t$(_V) convert {0}_{2}.png -resize 25% '
                            '{0}_{1}.png\n').format(rendername,
                                                    suff['olden'],
                                                    suff['rendered']))
                    # Source png which we will modify
                    f.write((
                            '{0}_{1}.png: {2} {3}\n'
                            '\t$(_V) {4}\n').format(
                            rendername, suff['rendered'], self.src,
                            blender_deps, these_args))
                    # Remove frame number, which blender forces
                    f.write('\t$(_V) mv {0}_{1}*.png {0}_{1}.png\n\n'.format(
                            rendername, suff['rendered']))
