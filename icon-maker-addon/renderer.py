import bpy
import os.path
from math import radians
import mathutils

from mathutils import Vector

from . import utils, node_utils, im_objs

def renderFrame(output):
    
    scene = bpy.context.scene

    # Settings
    scene.render.filepath = output
    scene.render.resolution_x = int(scene.icomake_props.render_resolution)
    scene.render.resolution_y = int(scene.icomake_props.render_resolution)
    scene.render.image_settings.file_format='TARGA'
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Standard'
    
    bpy.ops.render.render(write_still = True)

# Call Functions

def makeIcon(context, coll, render_output = "//"):
    scene = context.scene
    
    # Sanity check
    if coll == scene.collection:
        raise ValueError('Collection cannot be Scene Collection')

    objs = coll.all_objects
    
    config = None
    for obj in objs:
        if obj.type != "EMPTY":
            pass
        
        if utils.lookupData(obj, 'icomake_data'):
            config = obj
    
    if config is None:
        raise ValueError('No config object in collection')
    
    pos = config.icomake_object_props.render_position

    # camera and object placement
    camera_data = bpy.data.cameras.new("[ICOMAKE] Camera")
    camera = bpy.data.objects.new("[ICOMAKE] Camera", camera_data)
    utils.setData(camera)
    
    # Place cameras
    if pos == "FLOOR":
        camera.rotation_euler = ([radians(a) for a in (60.0, 0.0, 330.0)])
    elif pos == "WALL":
        camera.rotation_euler = ([radians(a) for a in (330.0, 330.0, 180.0)])
    elif pos == "CEIL":
        camera.rotation_euler = ([radians(a) for a in (60.0, 180.0, 390.0)])

#    scene.render.resolution_x = scene.icomake_props.render_resolution
#    scene.render.resolution_y = scene.icomake_props.render_resolution
    
    camera.data.type = "ORTHO"
    scene.camera = camera
#    utils.selectObjects(context, objs)
#    bpy.ops.view3d.camera_to_view_selected()
    camera.data.ortho_scale = max(config.scale) * 3.09807
        
    if not scene.collection.objects.get(camera.name):
        scene.collection.objects.link(camera)

    tempColSdw = bpy.data.collections.new("[ICOMAKE] Shadow Collection")
    utils.setData(tempColSdw)
    scene.collection.children.link(tempColSdw)
    
    if not pos == "CEIL":
        shadowPlane, shadowObjects = im_objs.createShadowObjects(context, objs)
        shadowPlane.location = config.location - Vector((0.0, 0.0, config.scale.z - 0.5))
        context.collection.objects.unlink(shadowPlane)
        tempColSdw.objects.link(shadowPlane)
        for obj in shadowObjects:
            tempColSdw.objects.link(obj)
    
        
    # one blender unit in x-direction
#    print(max(config.scale))
    vec = Vector((0.0, 0.0, max(config.scale) + 100))
    inv = camera.rotation_euler.to_matrix()
    inv.invert()
    # vec aligned to local axis in Blender 2.8+
    # in previous versions: vec_rot = vec * inv
    vec_rot = vec @ inv
    camera.location = config.location + camera.location + vec_rot
    
    # RENDER!
    objectLayer = scene.view_layers.new(name='[ICOMAKE] Object Layer')
    utils.setData(objectLayer)
    context.window.view_layer = objectLayer
    utils.include_only_one_collection(objectLayer, coll)
    
    shadowLayer = scene.view_layers.new(name='[ICOMAKE] Shadow Layer')
    utils.setData(shadowLayer)
    context.window.view_layer = shadowLayer
    utils.include_only_one_collection(shadowLayer, tempColSdw)
    
    context.window.view_layer = objectLayer

    # Compositing
    node_utils.nodesCompositing(objectLayer, shadowLayer)

    renderFrame(render_output)

def setupScene():
    # Sun
    scene = bpy.context.scene

    sun_data = bpy.data.lights.new("[ICOMAKE] Sun", type="SUN")
    sun = bpy.data.objects.new("[ICOMAKE] Sun", sun_data)
    utils.setData(sun, "icomake_scenedata")

    sun.data.color = (0.603827, 0.603827, 0.603827)
    sun.data.energy = 1
    sun.data.diffuse_factor = 1
    sun.data.specular_factor = 1
    sun.data.volume_factor = 1
    sun.data.angle = 0

#    sun.data.shadow_buffer_bias = 0.002

    sun.rotation_euler = ([radians(a) for a in (45.0, 0.0, 20.0)])

    if not scene.collection.objects.get(sun.name):
        scene.collection.objects.link(sun)

class IM_RenderActive(bpy.types.Operator):
    """Render active collection and export icons"""
    bl_idname = "icomake.renderactive"
    bl_label = "Render Active Collection"
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.users_collection[0] is not None and
                context.object.users_collection[0] != context.scene.collection and
                context.object.mode == "OBJECT" and
                context.scene.icomake_props.render_output != "")
    
    def execute(self, context):
        scene = context.scene

        coll = context.object.users_collection[0]

        utils.cleanUpData("icomake_scenedata")
        utils.cleanUpData("icomake_tempdata")

        setupScene()

        render_output = scene.icomake_props.render_output + os.path.splitext(coll.name)[0] + ".tga"
        position = "FLOOR"
        makeIcon(context, coll, render_output)
        
        if scene.icomake_props.render_cleanup:
            utils.cleanUpData("icomake_scenedata")
            utils.cleanUpData("icomake_tempdata")
        
        return {'FINISHED'}

class IM_CleanUp(bpy.types.Operator):
    """Remove all ICOMAKE Data from scene"""
    bl_idname = "icomake.cleanup"
    bl_label = "Clean Up ICOMAKE Data"
    
    def execute(self, context):
        utils.cleanUpData("icomake_scenedata")
        utils.cleanUpData("icomake_tempdata")
                
        return {'FINISHED'}