import bpy
import os
import sys

# For now, assume we will only use the first scene of the file. We don't have
# files using multiple scenes anyway. This might change in the future.
scene = bpy.data.scenes[0]

# Get all args after -- from command line
script_args = sys.argv[sys.argv.index('--')+1:]
scene.cycles.samples = int(script_args[0])
