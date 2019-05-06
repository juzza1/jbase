import bpy
print('BEGIN BLENDER DEPENCIES')
for i in bpy.utils.blend_paths():
    print(bpy.path.abspath(i))
print('END BLENDER DEPENCIES')
