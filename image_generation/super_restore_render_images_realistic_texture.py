# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from __future__ import print_function
import math, sys, random, argparse, json, os, tempfile

from datetime import datetime as dt
from collections import Counter
import pdb
import gc
# random.seed(10)

import numpy as np
import subprocess
import kubric as kb

from tqdm import tqdm

import bpy
from mathutils import Vector
import utils

parser = argparse.ArgumentParser()

# Input options
parser.add_argument('--base_scene_blendfile', default='data/base_scene2.blend',
        help="Base blender file on which all scenes are based; includes " +
                    "ground plane, lights, and camera.")
parser.add_argument('--properties_json', default='data/properties.json',
        help="JSON file defining objects, materials, sizes, and colors. " +
                 "The \"colors\" field maps from CLEVR color names to RGB values; " +
                 "The \"sizes\" field maps from CLEVR size names to scalars used to " +
                 "rescale object models; the \"materials\" and \"shapes\" fields map " +
                 "from CLEVR material and shape names to .blend files in the " +
                 "--object_material_dir and --shape_dir directories respectively.")
parser.add_argument('--shape_dir', default='data/shapes',
        help="Directory where .obj files for object models are stored")
parser.add_argument('--model_dir', default='data/save_models_1/',
        help="Directory where .blend files for object models are stored")
parser.add_argument('--material_dir', default='data/materials',
    help="Directory where .blend files for materials are stored")

# Settings for objects
parser.add_argument('--min_objects', default=3, type=int,
        help="The minimum number of objects to place in each scene")
parser.add_argument('--max_objects', default=10, type=int,
        help="The maximum number of objects to place in each scene")
parser.add_argument('--min_dist', default=0.25, type=float,
        help="The minimum allowed distance between object centers")
parser.add_argument('--margin', default=0.4, type=float,
        help="Along all cardinal directions (left, right, front, back), all " +
                 "objects will be at least this distance apart. This makes resolving " +
                 "spatial relationships slightly less ambiguous.")
parser.add_argument('--min_pixels_per_object', default=200, type=int,
        help="All objects will have at least this many visible pixels in the " +
                 "final rendered images; this ensures that no objects are fully " +
                 "occluded by other objects.")
parser.add_argument('--min_pixels_per_part', default=20, type=int,
        help="All modified parts will have at least this many visible pixels in the " +
                 "final rendered images; this ensures that no objects are fully " +
                 "occluded by other objects.")
parser.add_argument('--max_retries', default=50, type=int,
        help="The number of times to try placing an object before giving up and " +
                 "re-placing all objects in the scene.")
parser.add_argument("--hdri_assets", type=str,
    default="gs://kubric-public/assets/HDRI_haven/HDRI_haven.json")
# Output settings
parser.add_argument('--start_idx', default=0, type=int,
        help="The index at which to start for numbering rendered images. Setting " +
                 "this to non-zero values allows you to distribute rendering across " +
                 "multiple machines and recombine the results later.")
parser.add_argument('--num_images', default=5, type=int,
        help="The number of images to render")
parser.add_argument('--filename_prefix', default='superCLEVR',
        help="This prefix will be prepended to the rendered images and JSON scenes")
parser.add_argument('--split', default='new',
        help="Name of the split for which we are rendering. This will be added to " +
                 "the names of rendered images, and will also be stored in the JSON " +
                 "scene structure for each image.")
parser.add_argument('--output_image_dir', default='../output/images/',
        help="The directory where output images will be stored. It will be " +
                 "created if it does not exist.")
parser.add_argument('--output_scene_dir', default='../output/scenes/',
        help="The directory where output JSON scene structures will be stored. " +
                 "It will be created if it does not exist.")
parser.add_argument('--output_scene_file', default='../output/CLEVR_scenes.json',
        help="Path to write a single JSON file containing all scene information")
parser.add_argument('--output_blend_dir', default='../output/blendfiles',
        help="The directory where blender scene files will be stored, if the " +
                 "user requested that these files be saved using the " +
                 "--save_blendfiles flag; in this case it will be created if it does " +
                 "not already exist.")
parser.add_argument('--save_blendfiles', type=int, default=1,
        help="Setting --save_blendfiles 1 will cause the blender scene file for " +
                 "each generated image to be stored in the directory specified by " +
                 "the --output_blend_dir flag. These files are not saved by default " +
                 "because they take up ~5-10MB each.")
parser.add_argument('--version', default='1.0',
        help="String to store in the \"version\" field of the generated JSON file")
parser.add_argument('--license',
        default="Creative Commons Attribution (CC-BY 4.0)",
        help="String to store in the \"license\" field of the generated JSON file")
parser.add_argument('--date', default=dt.today().strftime("%m/%d/%Y"),
        help="String to store in the \"date\" field of the generated JSON file; " +
                 "defaults to today's date")

# Rendering options
parser.add_argument('--use_gpu', default=0, type=int,
        help="Setting --use_gpu 1 enables GPU-accelerated rendering using CUDA. " +
                 "You must have an NVIDIA GPU with the CUDA toolkit installed for " +
                 "to work.")
parser.add_argument('--width', default=320, type=int,
        help="The width (in pixels) for the rendered images")
parser.add_argument('--height', default=240, type=int,
        help="The height (in pixels) for the rendered images")
parser.add_argument('--key_light_jitter', default=1.0, type=float,
        help="The magnitude of random jitter to add to the key light position.")
parser.add_argument('--fill_light_jitter', default=1.0, type=float,
        help="The magnitude of random jitter to add to the fill light position.")
parser.add_argument('--back_light_jitter', default=1.0, type=float,
        help="The magnitude of random jitter to add to the back light position.")
parser.add_argument('--camera_jitter', default=0.5, type=float,
        help="The magnitude of random jitter to add to the camera position")
parser.add_argument('--render_num_samples', default=512, type=int,
        help="The number of samples to use when rendering. Larger values will " +
                 "result in nicer images but will cause rendering to take longer.")
parser.add_argument('--render_min_bounces', default=8, type=int,
        help="The minimum number of bounces to use for rendering.")
parser.add_argument('--render_max_bounces', default=8, type=int,
        help="The maximum number of bounces to use for rendering.")
parser.add_argument('--render_tile_size', default=256, type=int,
        help="The tile size to use for rendering. This should not affect the " +
                 "quality of the rendered image but may affect the speed; CPU-based " +
                 "rendering may achieve better performance using smaller tile sizes " +
                 "while larger tile sizes may be optimal for GPU-based rendering.")
parser.add_argument('--clevr_scene_path', default=None,
        help="the path of CLEVR's scene file")

# dist files
parser.add_argument('--color_dist_pth', default=None,
        help="the dir to distribution files")
parser.add_argument('--mat_dist_pth', default=None,
        help="the dir to distribution files")
parser.add_argument('--shape_dist_pth', default=None,
        help="the dir to distribution files")
parser.add_argument('--shape_color_co_dist_pth', default=None,
        help="the dir to distribution files")
parser.add_argument('--is_part', default=1, type=int,
        help="need part or not")
parser.add_argument('--load_scene', default=1, type=int,
        help="when sclevr_scene_path is provided, 0 to only load xyz size, 1 to load the scene")

argv = utils.extract_args()
args = parser.parse_args(argv)
clevr_scene_path = args.clevr_scene_path
if clevr_scene_path is not None:
    print('Loading scenes from ', clevr_scene_path)
    clevr_scene = json.load(open(clevr_scene_path))
    clevr_scene = clevr_scene['scenes']
    

def main(args):
    global color_name_to_rgba, size_mapping, material_mapping, textures_mapping, obj_info
    # Load the property file
    color_name_to_rgba, size_mapping, material_mapping, textures_mapping, obj_info = utils.load_properties_json(args.properties_json, os.path.join(args.shape_dir, 'labels'))

    global shape_dist, mat_dist, color_dist, shape_color_co_dist
    shape_dist, mat_dist, color_dist, shape_color_co_dist = utils.load_dist(args.color_dist_pth, args.mat_dist_pth, args.shape_dist_pth, args.shape_color_co_dist_pth)

    num_digits = 6
    prefix = '%s_%s_' % (args.filename_prefix, args.split)
    img_template = '%s%%0%dd.png' % (prefix, num_digits)
    scene_template = '%s%%0%dd.json' % (prefix, num_digits)
    blend_template = '%s%%0%dd.blend' % (prefix, num_digits)
    img_template = os.path.join(args.output_image_dir, img_template)
    scene_template = os.path.join(args.output_scene_dir, scene_template)
    blend_template = os.path.join(args.output_blend_dir, blend_template)

    if not os.path.isdir(args.output_image_dir):
        os.makedirs(args.output_image_dir)
    if not os.path.isdir(args.output_scene_dir):
        os.makedirs(args.output_scene_dir)
    if args.save_blendfiles == 1 and not os.path.isdir(args.output_blend_dir):
        os.makedirs(args.output_blend_dir)
    
    all_scene_paths = []
    for i in tqdm(range(args.num_images)):
        
        # positive to render normally, else load the scene and only render the mask
        scene_idx = i + args.start_idx if args.clevr_scene_path is not None else -1
        image_idx = clevr_scene[scene_idx]['image_index'] if (scene_idx >= 0 and args.load_scene) else i+args.start_idx

        img_path = img_template % (image_idx)
        scene_path = scene_template % (image_idx)

        
        # all_scene_paths.append(scene_path)

        # if os.path.exists(img_path):
        #     print("Skip", img_path)
        #     continue

        blend_path = None
        if args.save_blendfiles == 1:
            blend_path = blend_template % (image_idx)
        num_objects = random.randint(args.min_objects, args.max_objects)
        
        # pdb.set_trace()
        render_scene(args,
            num_objects=num_objects,
            output_index=(image_idx),
            output_split=args.split,
            output_image=img_path,
            output_scene=scene_path,
            output_blendfile=blend_path,
            idx=scene_idx
        )
    # After rendering all images, combine the JSON files for each scene into a
    # single JSON file.
    all_scenes = []
    for scene_path in all_scene_paths:
        with open(scene_path, 'r') as f:
            all_scenes.append(json.load(f))
    output = {
        'info': {
            'date': args.date,
            'version': args.version,
            'split': args.split,
            'license': args.license,
        },
        'scenes': all_scenes
    }
    with open(args.output_scene_file, 'w') as f:
        json.dump(output, f)
        

def render_scene(args,
        num_objects=5,
        output_index=0,
        output_split='none',
        output_image='render.png',
        output_scene='render_json',
        output_blendfile=None,
        idx=-1
    ):
    random.seed(int(output_index))


    # Load the main blendfile
    bpy.ops.wm.open_mainfile(filepath=args.base_scene_blendfile)


    # Set render arguments so we can get pixel coordinates later.
    # We use functionality specific to the CYCLES renderer so BLENDER_RENDER
    # cannot be used.
    render_args = bpy.context.scene.render
    render_args.engine = "CYCLES" #BLENDER_RENDER, CYCLES
    render_args.filepath = output_image
    render_args.resolution_x = args.width
    render_args.resolution_y = args.height
    render_args.resolution_percentage = 100
    bpy.context.scene.cycles.tile_size = args.render_tile_size
    # render_args.tile_x = args.render_tile_size
    # render_args.tile_y = args.render_tile_size
    if args.use_gpu == 1:
        # Blender changed the API for enabling CUDA at some point
        bpy.context.scene.render.engine = 'CYCLES'
        cycles_prefs = bpy.context.preferences.addons['cycles'].preferences

        # cuda_devices, opencl_devices = cycles_prefs.get_devices()
        bpy.context.scene.cycles.device = 'GPU'
        cycles_prefs.compute_device_type = "CUDA"
        bpy.context.preferences.addons["cycles"].preferences.get_devices()
        devices_used = [d.name for d in bpy.context.preferences.addons["cycles"].preferences.devices
                        if d.use]
        print("Devices used:", devices_used)
 
        

    # # Some CYCLES-specific stuff
    # bpy.data.worlds['World'].cycles.sample_as_light = True
    # bpy.context.scene.cycles.blur_glossy = 2.0
    # bpy.context.scene.cycles.samples = args.render_num_samples
    # bpy.context.scene.cycles.transparent_min_bounces = args.render_min_bounces
    # bpy.context.scene.cycles.transparent_max_bounces = args.render_max_bounces
    if args.use_gpu == 1:
        bpy.context.scene.cycles.device = 'GPU'

    # This will give ground-truth information about the scene and its objects
    # pdb.set_trace()
    scene_struct = {
            'split': output_split,
            'image_index': output_index,
            'image_filename': os.path.basename(output_image),
            'objects': [],
            'directions': {},
    }

    # Put a plane on the ground so we can compute cardinal directions
    bpy.ops.mesh.primitive_plane_add(size=5)
    plane = bpy.context.object

    def rand(L):
        return 2.0 * L * (random.random() - 0.5)

    # Add random jitter to camera position
    if args.camera_jitter > 0:
        for i in range(3):
            bpy.data.objects['Camera'].location[i] += rand(args.camera_jitter)
    
    # Figure out the left, up, and behind directions along the plane and record
    # them in the scene structure
    camera = bpy.data.objects['Camera']
    if clevr_scene_path is not None:
        camera.location = clevr_scene[idx]['camera_location']
        
    plane_normal = plane.data.vertices[0].normal
    
    # cam_behind = camera.matrix_world.to_quaternion() * Vector((0, 0, -1))
    # cam_left = camera.matrix_world.to_quaternion() * Vector((-1, 0, 0))
    # cam_up = camera.matrix_world.to_quaternion() * Vector((0, 1, 0))
    cam_behind = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
    cam_left = camera.matrix_world.to_quaternion() @ Vector((-1, 0, 0))
    cam_up = camera.matrix_world.to_quaternion() @ Vector((0, 1, 0))
    plane_behind = (cam_behind - cam_behind.project(plane_normal)).normalized()
    plane_left = (cam_left - cam_left.project(plane_normal)).normalized()
    plane_up = cam_up.project(plane_normal).normalized()

    
    # Delete the plane; we only used it for normals anyway. The base scene file
    # contains the actual ground plane.
    utils.delete_object(plane)

    # utils.delete_object(bpy.data.objects['Ground'])
    # utils.delete_object(bpy.data.objects['Lamp_Key'])
    # utils.delete_object(bpy.data.objects['Lamp_Fill'])
    # utils.delete_object(bpy.data.objects['Lamp_Back'])
    # utils.delete_object(bpy.data.objects['Area'])

    # set dome feature

    hdri_source = kb.AssetSource.from_manifest(args.hdri_assets, scratch_dir='/home/xingrui/tmp2')
    
    train_backgrounds, test_backgrounds = hdri_source.get_test_split(fraction=0.1)
    # train_backgrounds = [name]
    
    with open('data/HDRI_haven.json', 'r') as f:
        hdri_data = json.load(f)["assets"]
    hdri_ids = [name for name in hdri_data if "outdoor" in hdri_data[name]["metadata"]["categories"]]
    hdri_ids = [name for name in hdri_ids if "high contrast" not in hdri_data[name]["metadata"]["categories"]]
    
    hdri_id = random.choice(hdri_ids)

    print(hdri_id)

    background_hdri = hdri_source.create(asset_id=hdri_id)
    
    # existings = list(bpy.data.objects)
    # bpy.ops.import_scene.obj(filepath="data/dome.obj")
    # added_name = list(set(bpy.data.objects) - set(existings))[0].name
    # bpy.context.view_layer.objects.active = bpy.data.objects[added_name]
    
    utils.set_dome_texture("floor", background_hdri.filename)

    
    # Example usage
    utils._set_ambient_light_hdri(background_hdri.filename)

    # Save all six axis-aligned directions in the scene struct
    scene_struct['hdri_id'] = hdri_id
    scene_struct['directions']['behind'] = tuple(plane_behind)
    scene_struct['directions']['front'] = tuple(-plane_behind)
    scene_struct['directions']['left'] = tuple(plane_left)
    scene_struct['directions']['right'] = tuple(-plane_left)
    scene_struct['directions']['above'] = tuple(plane_up)
    scene_struct['directions']['below'] = tuple(-plane_up)

    # Add random jitter to lamp positions
    # if args.key_light_jitter > 0:
    #     for i in range(3):
    #         bpy.data.objects['Lamp_Key'].location[i] += rand(args.key_light_jitter)
    # if args.back_light_jitter > 0:
    #     for i in range(3):
    #         bpy.data.objects['Lamp_Back'].location[i] += rand(args.back_light_jitter)
    # if args.fill_light_jitter > 0:
    #     for i in range(3):
    #         bpy.data.objects['Lamp_Fill'].location[i] += rand(args.fill_light_jitter)

    # Now make some random objects
    objects, blender_objects = add_random_objects(scene_struct, num_objects, args, camera, idx)

    # Render the scene and dump the scene data structure
    scene_struct['objects'] = objects
    # scene_struct['relationships'] = compute_all_relationships(scene_struct)

    while True:
        try:
            bpy.ops.render.render(write_still=True)
            break
        except Exception as e:
            print(e)
            

    with open(output_scene, 'w') as f:
        # json.dump(scene_struct, f, indent=2)
        json.dump(scene_struct, f)

    if output_blendfile is not None:
        bpy.ops.wm.save_as_mainfile(filepath=output_blendfile)
        

def add_random_objects(scene_struct, num_objects, args, camera, idx=-1):
    """
    Add random objects to the current blender scene
    """

    positions = []
    objects = []
    blender_objects = []
    obj_pointer = []
    if idx>=0:
        cob = clevr_scene[idx]['objects']
        num_objects = len(cob)
    
    print('adding', num_objects, 'objects.')
    
    first_flag = True if idx >= 0 else False
    for i in range(num_objects):
        if idx >= 0 and args.load_scene:
            sf = cob[i] 
            theta = sf['rotation']
            obj_name = sf['shape']
            obj_pth = obj_info['info_pth'][obj_name]
            size_name = sf['size']
            r = {a[0]: a[1] for a in size_mapping}[size_name]
            x, y = sf['3d_coords'][:2]
        else:
            # Choose a random size
            size_name, r = random.choice(size_mapping)

            # Choose random shape
            if shape_dist is None:
                obj_name, obj_pth = random.choice(list(obj_info['info_pth'].items()))
            else:
                obj_name = np.random.choice(shape_dist['names'], p=shape_dist['dist'])
                obj_pth = obj_info['info_pth'][obj_name]
            
            # 
            # Try to place the object, ensuring that we don't intersect any existing
            # objects and that we are more than the desired margin away from all existing
            # objects along all cardinal directions.
            num_tries = 0
            while True:
                # If we try and fail to place an object too many times, then delete all
                # the objects in the scene and start over.
                num_tries += 1
                print(i, num_tries)
                if num_tries > args.max_retries:
                    for obj in blender_objects:
                        utils.delete_object(obj)
                    return add_random_objects(scene_struct, num_objects, args, camera)
                
                # to loading xyz and size only at the first time
                if first_flag:
                    sf = cob[i] 
                    theta = sf['rotation']
                    size_name = sf['size']
                    r = {a[0]: a[1] for a in size_mapping}[size_name]
                    x, y = sf['3d_coords'][:2]
                    obj_name = sf['shape']
                    obj_pth = obj_info['info_pth'][obj_name]
                else:
                    x = random.uniform(-3, 3)
                    y = random.uniform(-3, 3)
                    # Choose random orientation for the object.
                    theta = 360.0 * random.random()
                
                # Check to make sure the new object is further than min_dist from all
                # other objects, and further than margin along the four cardinal directions
                dists_good = True
                margins_good = True
                
                def dist_map(x,y,t):
                    theta = t / 180. * math.pi
                    dx1 = x * math.cos(theta) - y * math.sin(theta)
                    dy1 = x * math.sin(theta) + y * math.cos(theta)
                    dx2 = x * math.cos(theta) + y * math.sin(theta)
                    dy2 = x * math.sin(theta) - y * math.cos(theta)
                    return dx1, dy1, dx2, dy2
                
                def ccw(A,B,C):
                    # return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)
                    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

                # Return true if line segments AB and CD intersect
                def intersect(A,B,C,D):
                    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
                
                
                def check(xx,yy,box_xx,box_yy,rr,tt,x,y,box_x,box_y,r,theta):
                    xx1, yy1, xx2, yy2 = dist_map(box_xx/2*rr, box_yy/2*rr, tt)
                    AA = (xx+xx1, yy+yy1)
                    BB = (xx+xx2, yy+yy2)
                    CC = (xx-xx1, yy-yy1)
                    DD = (xx-xx2, yy-yy2)
                    x1, y1, x2, y2 = dist_map(box_x/2*r, box_y/2*r, theta)
                    A = (x+x1, y+y1)
                    B = (x+x2, y+y2)
                    C = (x-x1, y-y1)
                    D = (x-x2, y-y2)
                    for (p1, p2) in [(AA, BB), (BB, CC), (CC, DD), (DD, AA), (AA, CC), (BB, DD)]:
                        for (p3, p4) in [(A, B), (B, C), (C, D), (D, A), (A, C), (B, D)]:
                            if intersect(p1, p2, p3, p4):
                                return True
                    return False
                    
                    
                for (objobj, xx, yy, rr, tt) in positions:
                    box_x, box_y, _ = obj_info['info_box'][obj_name]
                    box_xx, box_yy, _ = obj_info['info_box'][objobj]
                    if check(xx,yy,box_xx,box_yy,rr*1.1,tt,x,y,box_x,box_y,r*1.1,theta):
                        margins_good = False
                        break

                if dists_good and margins_good:
                    break
                else:
                    first_flag = False


        # Actually add the object to the scene
        loc = (x, y, -r*obj_info['info_z'][obj_name])
        
        if idx >= 0 and args.load_scene:
            color_name = sf['color']
        else:
            color_name, rgba = random.choice(list(color_name_to_rgba.items()))

        current_obj = utils.add_object_with_texture(args.model_dir, obj_name, obj_pth, color_name, r, loc, theta=theta)
        obj = bpy.context.object
        blender_objects.append(obj)
        positions.append((obj_name, x, y, r, theta))

        texture = None
        # Attach a random color
        # rgba=(1,0,0,1)
        # if idx >= 0 and args.load_scene:
        #     mat_name_out = sf['material']
        #     mat_name = {a[1]: a[0] for a in material_mapping}[mat_name_out]
        #     color_name = sf['color']
        #     rgba = color_name_to_rgba[color_name]
        #     texture = sf.get('texture', random.choice(textures_mapping))
        # else:
        #     if mat_dist is None:
        #         mat_name, mat_name_out = random.choice(material_mapping)
        #     else:
        #         mat_name_out = np.random.choice(mat_dist['names'], p=mat_dist['dist'])
        #         mat_name = {a[1]: a[0] for a in material_mapping}[mat_name_out]
                
        #     if shape_color_co_dist is not None:
        #         _dist = shape_color_co_dist['dist'][shape_color_co_dist['shape_idx_map'][obj_name]]
        #         color_name = np.random.choice(shape_color_co_dist['colors'], p=_dist)
        #         rgba = color_name_to_rgba[color_name]
        #     elif color_dist is None:
        #         color_name, rgba = random.choice(list(color_name_to_rgba.items()))
        #     else:
        #         color_name = np.random.choice(color_dist['names'], p=color_dist['dist'])
        #         rgba = color_name_to_rgba[color_name]
        #     texture = random.choice(textures_mapping)
        mat_freq = {"large":60, "small":30}[size_name]
        # if texture=='checkered':
        #     mat_freq = mat_freq / 2
        # utils.modify_color(current_obj, material_name=mat_name, mat_list=obj_info['info_material'][obj_name], 
        #                    color=rgba,
        #                    texture=texture, mat_freq=mat_freq)
        # import ipdb; ipdb.set_trace()
        # utils.modify_real_color(current_obj, material_name=mat_name, mat_list=obj_info['info_material'][obj_name], 
        #                    color=rgba,
        #                    texture=texture, mat_freq=mat_freq)     

        # Record data about the object in the scene data structure
        pixel_coords = utils.get_camera_coords(camera, obj.location)
        objects.append({
            'shape': obj_name,
            'size': size_name,
            '3d_coords': tuple(obj.location),
            'rotation': theta,
            'pixel_coords': pixel_coords,
            'color': color_name,
            'material': None,
            'texture': None
        })
        
        obj_pointer.append(current_obj)


    if idx >= 0 and args.load_scene:
        return objects, blender_objects


    return objects, blender_objects
    



if __name__ == '__main__':
    argv = utils.extract_args()
    # import ipdb; ipdb.set_trace()
    args = parser.parse_args(argv)
    main(args)