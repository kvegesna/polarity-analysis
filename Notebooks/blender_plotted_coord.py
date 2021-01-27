# This script will import Cytosim's filaments into Blender
# It must be run from within Blender, and will read "actin####.txt" files
# to generate a collection of Icosahedral-meshes
#
# The input files should be generated by Cytosim's tool "cymart"
# and copied to a local blender directory called 'cymart'
#
# Authors: Richard van der Oost, 08 -- 09.2017
#          Francois Nedelec, 28.01.2018 -- 06.02.2018

import bpy
import bmesh
from mathutils import Vector
import os.path

# Variables
file_path = "new_coords.txt"
root_name = "actin"

scale = 100
deltaZ = 0.030
origin = Vector((0,0,0))
radius = 0.00275 * 1.3
materials = (None, "BioShader-LightBlue", "BioShader-LightBlue", "BioShader-LightBlue", "BioShader-LightBlue")

# Shortcuts
bld = bpy.data
scene = bpy.context.scene

# build icosahedron mesh
ico = bmesh.new()
bmesh.ops.create_icosphere(ico, subdivisions=4, diameter=radius)


def remove_objects(name):
    """ Remove objects starting by 'name'"""
    for obj in scene.objects:
        if obj.name.startswith(name):
            bld.objects.remove(obj)


def hide_until(obj, atr, f):
    if(atr =='hide'):
        obj.hide_set(True)
    if(atr =='hide_render'):
        b=0
        obj.hide_set(True)
    #setattr(obj, atr, True)
    obj.keyframe_insert("location", frame=f-1)
    if(atr =='hide'):
        obj.hide_set(False)
    if(atr =='hide_render'):
        obj.hide_set(False)
    obj.keyframe_insert("location", frame=f)


def set_location(obj, pos, f):
    obj.location = pos
    obj.keyframe_insert("location", frame=f)


def import_frame(frame_id, frame_data):
    print('hi there')
    """ Import objects from one file"""
    filament_id = 0
    obj_id = 0
    # Go over all the line:
    for line in frame_data:

        data = line.split(" ")
        old_filament_id = filament_id
        filament_id = int(data[1])
        obj_type = int(data[2])
        position = Vector((float(data[3]), float(data[4]), float(data[5])+deltaZ))

        filament_name = root_name + "%04d" % filament_id

        if old_filament_id == filament_id:
            obj_id = obj_id + 1
        else:
            obj_id = 0;
            if filament_name in scene.objects:
                fil = scene.objects[filament_name]
            else:
                # create empty sphere as parent for all monomers:
                bpy.ops.object.empty_add(type='CUBE', radius=radius)
                fil = bpy.context.object
                fil.name = filament_name
                fil.scale = Vector((scale, scale, scale))
                fil.hide_render = True
                fil.keyframe_insert("hide_render", frame=0)
                set_location(fil, scale*position, frame_id)
                hide_until(fil, "hide", frame_id)

        obj = None
        obj_name = filament_name + "-%04d" % obj_id
        # Find the sphere object or create it
        if obj_name in scene.objects:
            # Just get a handle to the existing object
            obj = scene.objects[obj_name]
        else:
            # use a icosahedral mesh
            #mesh = bpy.ops.mesh.primitive_cube_add(radius=radius, location=origin)
            me = bld.meshes.new(obj_name)
            ico.to_mesh(me)
            obj = bld.objects.new(obj_name, me)
            obj.location = origin
            obj.parent = fil
            scene.collection.objects.link(obj)

            # Hide the object on the previous frames
            hide_until(obj, "hide", frame_id)
            hide_until(obj, "hide_render", frame_id)

        # Adjust material:
        if materials[obj_type] in bld.materials:
            obj.active_material = None
            obj.material_slots[obj.active_material_index].link = "OBJECT"
            obj.active_material = bld.materials[materials[obj_type]]
            obj.active_material.diffuse_color = (0, 255, 255)
        new_mat = bpy.data.materials.new(name="carpaint.NewRed")
        new_mat.diffuse_color = (1,0,0, 0.8)
        obj.active_material = new_mat
        #print(obj.active_material)
        # set current location
        
        set_location(obj, position - fil.location/scale, frame_id)
        print(fil.location)
        print('hi there')

def import_file(f):
    """ read file number 'f'"""
    print('hi there')
    print(type(file_path))
    file_name = file_path
    # Check if the frame file exists
    if os.path.isfile(file_name):
        #print("reading ", file_name)
        scene.frame_end = f+1
        # Read the frame file
        with open(file_name, 'r') as file:
            data = file.readlines()
        # Clean line breaks
        data = [line.strip() for line in data]
        print('hi there')
        import_frame(f+1, data)
    else:
        print("file " + file_name + " not found")
    print(file_name)

remove_objects(root_name);

# Specify the frames to import here [FIRST, LAST+1]:
for f in range(0, 1):
    print(f)
    print('hi there')
    import_file(f)


