import bpy
import os.path
from math import radians
import mathutils

from . import utils, node_utils

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
    utils.setData(shadowObject)
    shadowObject.name = object.name + "_shadow"
    shadowObject.is_holdout = True
    
    return shadowPlane, shadowObject

def renderFrame(output):
    
    scene = bpy.context.scene

    # Settings
    scene.render.filepath = output
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.image_settings.file_format='TARGA'
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Standard'
    
    bpy.ops.render.render(write_still = True)

# Call Functions

def makeIcon(object, pos = "FLOOR", render_output = "//"):
    scene = bpy.context.scene

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

    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    
    camera.data.type = "ORTHO"
    scene.camera = camera
    utils.selectObject(object)
    bpy.ops.view3d.camera_to_view_selected()
    camera.data.ortho_scale += 30
    
    objcol = object.users_collection[0]
    
    if objcol == scene.collection:
        tempCol = bpy.data.collections.new("[ICOMAKE] Object Collection")
        utils.setData(tempCol)
        scene.collection.children.link(tempCol)
        tempCol.objects.link(object)
    else:
        tempCol = objcol
        
    if not scene.collection.objects.get(camera.name):
        scene.collection.objects.link(camera)

    tempColSdw = bpy.data.collections.new("[ICOMAKE] Shadow Collection")
    utils.setData(tempColSdw)
    scene.collection.children.link(tempColSdw)
    
    if not pos == "CEIL":
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
    
    # RENDER!
    objectLayer = scene.view_layers.new(name='[ICOMAKE] Object Layer')
    utils.setData(objectLayer)
    bpy.context.window.view_layer = objectLayer
    utils.include_only_one_collection(objectLayer, tempCol)
    
    shadowLayer = scene.view_layers.new(name='[ICOMAKE] Shadow Layer')
    utils.setData(shadowLayer)
    bpy.context.window.view_layer = shadowLayer
    utils.include_only_one_collection(shadowLayer, tempColSdw)
    
    bpy.context.window.view_layer = objectLayer

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

class IM_RenderSelected(bpy.types.Operator):
    """Render model and export icons"""
    bl_idname = "icomake.renderselected"
    bl_label = "Render Selected Object"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(context.selected_objects) > 0 and context.scene.icomake_props.renderselected_output != ""
    
    def execute(self, context):
        scene = context.scene

        object = context.active_object

        utils.cleanUpData("icomake_scenedata")
        utils.cleanUpData("icomake_tempdata")

        setupScene()

        render_output = scene.icomake_props.renderselected_output + os.path.splitext(object.name)[0] + ".tga"
        position = scene.icomake_props.renderselected_position
#        outline = scene.icomake_props.renderselected_outline
        makeIcon(object, position, render_output)

        utils.cleanUpData("icomake_scenedata")
        utils.cleanUpData("icomake_tempdata")

        if not len(object.users_collection) > 0 and scene.collection.objects.get(object.name):
            scene.collection.objects.link(object)
        
        return {'FINISHED'}

class IM_PMShaderTree(bpy.types.Operator):
    """Add PM Shader Tree"""
    bl_idname = "icomake.pmshadertree"
    bl_label = "Add PM Shader Tree"
    
    @classmethod
    def poll(cls, context):
        return context.material is not None
    
    def execute(self, context):
        scene = context.scene

        material = context.material

        # Check for Node Group
        if not bpy.data.node_groups.get("[ICOMAKE] NGPmShader"):
            nodesPMShader()
            
        nodeShader = material.node_tree.nodes.new("ShaderNodeGroup")
        nodeShader.location = (0, 0)
        nodeShader.node_tree = bpy.data.node_groups['[ICOMAKE] NGPmShader']
        
        return {'FINISHED'}

class IM_CleanUp(bpy.types.Operator):
    """Apply PM Shader to selected"""
    bl_idname = "icomake.cleanup"
    bl_label = "Clean Up ICOMAKE Data"
    
    #@classmethod
    #def poll(cls, context):
    #    return True
    
    def execute(self, context):
        utils.cleanUpData("icomake_scenedata")
        utils.cleanUpData("icomake_tempdata")
                
        return {'FINISHED'}