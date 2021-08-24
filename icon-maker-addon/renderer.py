import bpy
import os.path
from math import radians
import mathutils

from . import utils, node_utils

def createOutlineObject(object, thickness):
    
    scene = bpy.context.scene

    # Copy model
    utils.selectObject(object)
    outlineObject = object.copy()
    utils.setData(outlineObject)
    outlineObject.data = object.data.copy()
    outlineObject.name = object.name + "_outline"
    outlineObject.data.materials.clear()
    scene.collection.objects.link(outlineObject)
    
    #Outline Material
    outlineMat = bpy.data.materials.new(name="[ICOMAKE] Outline")
    utils.setData(outlineMat)
    outlineMat.use_backface_culling = True
    outlineMat.diffuse_color = (0, 0, 0, 1)
    outlineMat.shadow_method = 'NONE'
    node_utils.nodesMatOutline(outlineMat)
    outlineObject.data.materials.append(outlineMat)
    
    utils.selectObject(outlineObject)
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.transform.shrink_fatten(value=-thickness)
    bpy.ops.object.mode_set()
    
    return outlineObject

def createShadowObject(object):
    utils.selectObject(object)
    # Place plane for shadows
    bpy.ops.mesh.primitive_plane_add(size=1000, enter_editmode=False, align='WORLD', location=(0, 0, -64.5), scale=(1, 1, 1))
    shadowPlane = bpy.context.active_object
    utils.setData(shadowPlane)

    # Give plane Shadow Catcher material
    shadowMat = bpy.data.materials.new(name="[ICOMAKE] Shadow Catcher")
    utils.setData(shadowMat)
    shadowMat.use_nodes = True
    shadowMat.blend_method = 'BLEND'
    
    node_utils.nodesMatShadow(shadowMat)
    
    shadowPlane.data.materials.append(shadowMat)
    
    shadowObject = object.copy()
    shadowObject.data = object.data.copy()
    shadowObject.name = object.name + "_shadow"
    shadowObject.data.materials.clear()
    
    clearMat = bpy.data.materials.new(name="[ICOMAKE] Clear")
    utils.setData(clearMat)
    clearMat.use_nodes = True
    clearMat.blend_method = 'CLIP'
    
    node_utils.nodesMatClear(clearMat)
    
    shadowObject.data.materials.append(clearMat)
    
    return shadowPlane, shadowObject

def renderFrames(name):
    
    scene = bpy.context.scene

    # Settings
    scene.render.filepath = scene.icomake_props.output_dir + name + ".tga"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.image_settings.file_format='TARGA'
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Standard'
    
    bpy.ops.render.render(write_still = True)

# Call Functions

def makeIcon(pgroup):
    scene = bpy.context.scene
    modelpth = os.path.join(bpy.path.abspath("//") + pgroup.path, pgroup.name)
    type = pgroup.position
    
    if "smd" in os.path.splitext(modelpth)[1]:
        object = utils.importSourceModel(modelpth)
    elif "obj" in os.path.splitext(modelpth)[1]:
        object = utils.importObj(modelpth)
        object.rotation_euler = ([radians(a) for a in (0.0, 0.0, 90.0)])
    
    utils.setData(object)

    for material_slot in object.material_slots:
        material = material_slot.material
        utils.setData(material)
        
        # Get image for material
        imagepth = os.path.join(os.path.dirname(modelpth), material.name + ".tga")
        if os.path.exists(imagepth):
            image = bpy.data.images.load(filepath=imagepth)
        else:
            image = bpy.data.images.new(name=material.name + ".tga", width=16, height=16)
            image.generated_color = (1, 0, 0.5, 1)
        utils.setData(image)

    node_utils.nodesMatModel(material, image)

    # camera and object placement
    camera_data = bpy.data.cameras.new("[ICOMAKE] Camera")
    camera = bpy.data.objects.new("[ICOMAKE] Camera", camera_data)
    utils.setData(camera)
    
    # Place cameras
    if type == "FLOOR":
        camera.rotation_euler = ([radians(a) for a in (60.0, 0.0, 330.0)])
    elif type == "WALL":
        camera.rotation_euler = ([radians(a) for a in (330.0, 330.0, 180.0)])
    elif type == "CEIL":
        camera.rotation_euler = ([radians(a) for a in (60.0, 180.0, 390.0)])
    
    camera.data.type = "ORTHO"
    scene.camera = camera
    utils.selectObject(object)
    bpy.ops.view3d.camera_to_view_selected()
    camera.data.ortho_scale += 30
    
    collection = object.users_collection[0]
    
    tempCol = bpy.data.collections.new("[ICOMAKE] Object Collection")
    utils.setData(tempCol)
    scene.collection.children.link(tempCol)
    tempColOut = bpy.data.collections.new("[ICOMAKE] Outline Collection")
    utils.setData(tempColOut)
    scene.collection.children.link(tempColOut)
    tempColSdw = bpy.data.collections.new("[ICOMAKE] Shadow Collection")
    utils.setData(tempColSdw)
    scene.collection.children.link(tempColSdw)
    
    tempCol.objects.link(object)
    tempCol.objects.link(camera)
    
    # Create extra objects for rendering
    outlineObject = createOutlineObject(object, pgroup.outline)
    scene.collection.objects.unlink(outlineObject)
    tempColOut.objects.link(outlineObject)
    
    if not type == "CEIL":
        shadowPlane, shadowObject = createShadowObject(object)
        bpy.context.collection.objects.unlink(shadowPlane)
        tempColSdw.objects.link(shadowPlane)
        tempColSdw.objects.link(shadowObject)
        
    # one blender unit in x-direction
    vec = mathutils.Vector((0.0, 0.0, max(object.dimensions) + 100.0))
    inv = camera.matrix_world.copy()
    inv.invert()
    # vec aligned to local axis in Blender 2.8+
    # in previous versions: vec_rot = vec * inv
    vec_rot = vec @ inv
    camera.location = camera.location + vec_rot
    
    bpy.data.collections.remove(collection)
    
    # RENDER!
    objectLayer = bpy.context.view_layer
    bpy.context.window.view_layer = bpy.context.view_layer
    for collection in bpy.context.layer_collection.children:
        if not collection.name == tempCol.name:
            collection.exclude = True
    
    outlineLayer = scene.view_layers.new(name='[ICOMAKE] Outline Layer')
    utils.setData(outlineLayer)
    bpy.context.window.view_layer = outlineLayer
    for collection in bpy.context.layer_collection.children:
        if not collection.name == tempColOut.name:
            collection.exclude = True
    
    shadowLayer = scene.view_layers.new(name='[ICOMAKE] Shadow Layer')
    utils.setData(shadowLayer)
    bpy.context.window.view_layer = shadowLayer
    for collection in bpy.context.layer_collection.children:
        if not collection.name == tempColSdw.name:
            collection.exclude = True
    
    bpy.context.window.view_layer = objectLayer

    # Compositing
    node_utils.nodesCompositing(objectLayer, outlineLayer, shadowLayer)

    renderFrames(os.path.splitext(pgroup.name)[0])

def setupScene():
    # Sun
    sun_data = bpy.data.lights.new("[ICOMAKE] Sun")
    sun = bpy.data.objects.new("[ICOMAKE] Sun", sun_data)
    utils.setData(sun, "icomake_scenedata")

    sun.rotation_euler = ([radians(a) for a in (45.0, 0.0, 20.0)])

class IM_MassRender(bpy.types.Operator):
    """Render models and export icons"""
    bl_idname = "icomake.massrender"
    bl_label = "Mass Render Icons"
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.icomake_imports) > 0 and context.scene.icomake_props.output_dir != ""
    
    def execute(self, context):
        scene = context.scene

        utils.cleanUpData("icomake_scenedata")
        utils.cleanUpData("icomake_tempdata")

        setupScene

        for pgroup in scene.icomake_imports:
            makeIcon(pgroup)
            utils.cleanUpData("icomake_tempdata")
            
        utils.cleanUpData("icomake_scenedata")
            
        
        return {'FINISHED'}