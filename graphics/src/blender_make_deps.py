import bpy
import os
import sys

# For now, assume we will only use the first scene of the file. We don't have
# files using multiple scenes anyway. This might change in the future.
scene = bpy.data.scenes[0]

# Use the file name for command line for the blend file
# Assumes file name is given after -b or --background
for i, arg in enumerate(sys.argv):
    if arg == '-b' or arg == '--background':
        blend_file = sys.argv[i+1]

# Get all args after -- from command line
script_args = sys.argv[sys.argv.index('--')+1:]

def blend_paths_to_rel(blend_paths, relative_to_path=os.curdir):
    """
    Convert any relative blender paths (// prefix) to paths relative to the
    param path.
    """
    def convert(path):
        abs_path = bpy.path.abspath(path)
        norm_path = os.path.normpath(abs_path)
        rel_path = os.path.relpath(norm_path, start=relative_to_path)
        return rel_path
    return [convert(p) for p in blend_paths]

def get_deps():
    """Get depencies (also known as libraries) for the current blend file."""
    libs = bpy.utils.blend_paths()
    return blend_paths_to_rel(libs)

def get_output_paths():
    """
    Get all the output names for this blend file. First index is the name 
    in render settings, the rest are names from file output nodes.
    """
    output_paths = []
    # Get output path from render settings
    render_path = scene.render.filepath
    output_paths.append(render_path)
    # Get output path of each file output node
    nodes = scene.node_tree.nodes
    for n in nodes:
        if n.bl_idname == 'CompositorNodeOutputFile':
            file_subpath = n.file_slots[n.active_input_index].path
            node_output_path = os.path.join(n.base_path, file_subpath)
            output_paths.append(node_output_path)
    return blend_paths_to_rel(output_paths)

def get_path_map(deps, output_paths, wanted_dir):

    def get_stems():
        """
        To avoid confusion, we don't change any paths in the blend file when
        building with make. Instead, if the output paths are in wrong format,
        return an error. Currently all output paths in the blend files must
        point to the build folder specified when running this script, and must
        have the same filename as the blend file itself. Only expection to this
        is a mask file, where an entry from the valid_mask_names allowed to
        appear after the stem of the filename.
        """
        valid_mask_names = ['mask_']
        blend_file = bpy.path.display_name_from_filepath(bpy.data.filepath)

        wanted_stem = os.path.join(wanted_dir, blend_file + '_')
        wanted_mask_stems = [wanted_stem + m for m in valid_mask_names]
        stems_out = []

        error_string = ('Blend file output path "{0}" differs from the '
                        'wanted build path "{1}"!')

        # Send error code to make and exit, if paths are wrong
        if wanted_stem != output_paths[0]:
            print(error_string.format(
                    output_paths[0], wanted_stem), file=sys.stderr)
            sys.exit(1)
        else:
            stems_out.append(output_paths[0] + '%.png')
        # Also check additional file output nodes if necessary
        if len(output_paths) > 1:
            for p in output_paths[1:]:
                if p not in wanted_mask_stems:
                    print(error_string.format(
                            p, 'or '.join(wanted_mask_paths)), file=sys.stderr)
                    sys.exit(1)
                else:
                    stems_out.append(p + '%.png')
        return stems_out
                    
    def get_frame_paths(paths):
        """
        Append frame number and file extension to blend file output names. Map
        this to a dict where each frame number corresponds to output paths for
        that frame.
        """
        frame_range = range(scene.frame_start, scene.frame_end+1)
        frame_nums = [str(f).zfill(4) for f in frame_range]
        return ['{0}{1}.png'.format(name, f) for f in frame_nums for name in paths]

    deps = get_deps()
    stems = get_stems()
    frame_paths = get_frame_paths(output_paths)
    map_out = {
        'deps': ' '.join(deps),
        'stems': ' '.join(stems),
        'png_frame_outputs': ' '.join(frame_paths)
        }
    return map_out

def get_make_str(path_map):
    """Write make targets"""
    render_script = script_args[2]
    render_samples = script_args[3]
    threads = script_args[4]

    make_string = (
            'render : {targets}\n'
            '{targets_pat} : {prerequisites}\n'
            '\t$(_E) "[GRAPHICS] [BLENDER-RENDER] {file_} frame $* -> $@"\n'
            '\t$(_V) blender -noaudio --factory-startup --background {file_} '
            '--engine CYCLES --threads {threads} --python {render_script} '
            '--render-frame $* -- {samples} > /dev/null\n'
            ).format(
                    targets = path_map['png_frame_outputs'],
                    targets_pat = path_map['stems'],
                    prerequisites = '{0} {1}'.format(
                        blend_file, path_map['deps']),
                    file_= blend_file,
                    threads = threads,
                    render_script = render_script,
                    samples = render_samples
                    )
    return(make_string)

def main():
    dep_file = script_args[1]
    wanted_dir = os.path.dirname(dep_file)

    if script_args[0] == 'write_dep':
        deps = get_deps()
        output_paths = get_output_paths()

        path_map = get_path_map(deps, output_paths, wanted_dir)

        make_str = get_make_str(path_map)
        with open(dep_file, 'w') as f:
            f.write(make_str)

main()
