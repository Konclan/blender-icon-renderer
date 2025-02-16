import bpy
from . import utils, node_utils

class IM_AddDefObject(bpy.types.Operator):
    """Add defintion object to active collection"""
    bl_idname = "icomake.adddefobject"
    bl_label = "Add defintion object to active collection"
    
    # Make sure we don't add this to the scene collection
    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.users_collection[0] is not None and
                context.object.users_collection[0] != context.scene.collection and
                context.object.mode == "OBJECT")
    
    def execute(self, context):
        active_collection = context.object.users_collection[0]
        empty = bpy.data.objects.new(active_collection.name + "_icomake_def", None)  # Create new empty object
        active_collection.objects.link(empty)  # Link empty to the current object's collection
        empty.empty_display_type = 'CUBE'
        empty.scale = (64, 64, 64)
        
        utils.setData(empty, "icomake_data")
#        utils.setData(empty, "icomake_object_props.render_position", context.object.icomake_object_props.render_position)
        
        return {'FINISHED'}


def createShadowObjects(context, objs):

    sdw_objs = []
    for obj in objs:
        if obj.type == "MESH":
            sdw_obj = obj.copy()
            sdw_obj.data = obj.data.copy()
            utils.setData(sdw_obj)
            sdw_obj.name = obj.name + "_shadow"
            sdw_obj.is_holdout = True
            sdw_objs.append(sdw_obj)
    
    # Place plane for shadows
    bpy.ops.mesh.primitive_plane_add(size=1000, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    sdw_plane = context.active_object
    sdw_plane.name = "[ICOMAKE] Shadow Catcher"
    utils.setData(sdw_plane)

    # Give plane Shadow Catcher material
    sdw_material = bpy.data.materials.new(name="[ICOMAKE] Shadow Catcher")
    utils.setData(sdw_material)
    sdw_material.use_nodes = True
    sdw_material.blend_method = 'BLEND'
    
    node_utils.nodesMatShadow(sdw_material)
    
    sdw_plane.data.materials.append(sdw_material)
    
    return sdw_plane, sdw_objs

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