import os
from subprocess import check_output
import sys

def get_blend_deps(blend_file):
    """Fetch all the depencies for the given blender file"""
    # Assume blender depency print code snippet is in the same folder as this
    # file
    current_path = os.path.dirname(__file__)
    blender_dep_print = os.path.join(current_path, 'blender_dep_print.py')
    blender_args = ['blender', '--factory-startup', '--background', blend_file,
                    '--python', blender_dep_print]
    output = check_output(blender_args)
    lines = output.splitlines()
    start = lines.index('BEGIN BLENDER DEPENCIES') + 1
    end = lines.index('END BLENDER DEPENCIES')
    deps = lines[start:end]
    # Get path relative to current path
    deps_formatted = [os.path.relpath(i) for i in deps]
    return deps_formatted

if __name__ == '__main__':
    out = ' '.join(get_blend_deps(sys.argv[1]))
    if len(sys.argv) == 2:
        print(out)
    elif len(sys.argv) == 3:
        with open(sys.argv[2], 'w') as f:
            f.write(out)
    else:
        print("Unknown arguments")

