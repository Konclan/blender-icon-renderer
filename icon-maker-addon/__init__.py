bl_info = {
	"name": "Icon Maker",
	"author": "Konclan",
	"version": (1, 0, 0),
	"blender": (2, 93, 0),
	"category": "Render",
	"location": "Scene properties",
	"description": "Item icon rendering tool for BEEmod",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
}

import bpy
from . import renderer, gui, node_utils, utils
import importlib

for module in [renderer, gui, node_utils, utils]:
    importlib.reload(module)

position_options = [
    ("FLOOR", "Floor", "Item is on the floor"),
    ("WALL", "Wall", "Item is on the wall"),
    ("CEIL", "Ceiling", "Item is on the ceiling"),
]

class IM_SceneProps(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    
    renderselected_output: bpy.props.StringProperty(
        name="Render Directory",
        description="Directory renders are saved to",
        default="//",
        subtype='DIR_PATH')

    renderselected_position: bpy.props.EnumProperty(
        name="Position",
        items=position_options,
        description="Position of the model in PeTI",
        default="FLOOR",)
    
#    renderselected_outline: bpy.props.IntProperty(
#        name="Ouline Thickness",
#        description="Thickness of the object outline",
#        default=1,)

    rendermass_output: bpy.props.StringProperty(
        name="Render Directory",
        description="Directory renders are saved to",
        default="//",
        subtype='DIR_PATH')

class IM_Imports(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="File",
        description="A name for this file",
        default="Untitled")
    
    path: bpy.props.StringProperty(
        name="Path",
        description="Path of this file reletive to this blend file",
        default="Untitled")
    
    position: bpy.props.EnumProperty(
        name="Position",
        items=position_options,
        description="Position of the model in PeTI",
        default="FLOOR",)
    
#    outline: bpy.props.IntProperty(
#        name="Ouline Thickness",
#        description="Thickness of the object outline",
#        default=1,)

class IM_TestOp_Create(bpy.types.Operator):
    """Test Operator: Create"""
    bl_idname = "icomake.test_create"
    bl_label = "MI Test Create"
    
    def execute(self, context):
        scene = context.scene

        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        cube = bpy.context.active_object
        cube["icomake_data"] = True
        cube.data["icomake_data"] = True

        material = bpy.data.materials.new(name="Test Mat")
        material["icomake_data"] = True

        camera_data = bpy.data.cameras.new("Camera")
        camera = bpy.data.objects.new("Camera", camera_data)
        camera_data["icomake_data"] = True

        image = bpy.data.images.load(filepath="C:/Users/class/Pictures/flushed-face_1f633.png", check_existing=True)
        image["icomake_data"] = True

        armature = bpy.data.armatures.new(name="Test Arma")
        armature["icomake_data"] = True

        collection = bpy.data.collections.new(name="Test Collection")
        collection["icomake_data"] = True

        view_layer = scene.view_layers.new(name='Test Layer')
        view_layer["icomake_data"] = True
        
        return {'FINISHED'}

class IM_TestOp_Remove(bpy.types.Operator):
    """Test Operator: Remove"""
    bl_idname = "icomake.test_remove"
    bl_label = "MI Test Remove"
    
    def execute(self, context):
        scene = context.scene

        utils.cleanUpBlend()
        
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(renderer.IM_RenderSelected.bl_idname)
    self.layout.operator(renderer.IM_MaterialSelected.bl_idname)
    self.layout.operator(renderer.IM_RenderMass.bl_idname)
    self.layout.operator(renderer.IM_CleanUp.bl_idname)
    self.layout.operator(IM_TestOp_Create.bl_idname)
    self.layout.operator(IM_TestOp_Remove.bl_idname)

_classes = (
    IM_SceneProps,
    IM_Imports,
    renderer.IM_RenderSelected,
    renderer.IM_PMShaderTree,
    renderer.IM_RenderMass,
    renderer.IM_CleanUp,
    gui.IM_GUI_FL_UL_ImportList,
    gui.IM_GUI_FL_OT_NewItem,
    gui.IM_GUI_FL_OT_DeleteItem,
    gui.IM_GUI_FL_OT_Clear,
    gui.IM_GUI_FL_OT_MoveItem,
    gui.IM_GUI_PT_RenderMass,
    gui.IM_GUI_PT_RenderSelected,
    IM_TestOp_Create,
    IM_TestOp_Remove,
    gui.IM_ShaderPanel,
)

def register():
    
    def make_pointer(prop_type, prop_name):
        return bpy.props.PointerProperty(name=prop_name,type=prop_type)
    
    for cls in _classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.icomake_props = make_pointer(IM_SceneProps, "Icon Maker Settings")

    bpy.types.Scene.icomake_rendermass_imports = bpy.props.CollectionProperty(name = "Icon Maker Imports", type = IM_Imports)
    bpy.types.Scene.icomake_rendermass_imports_index = bpy.props.IntProperty(name = "Icon Maker Import Index",default = 0)
    
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.
        

def unregister():
    for cls in _classes:
        bpy.utils.unregister_class(cls)
        
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    
    del bpy.types.Scene.icomake_props
    del bpy.types.Scene.icomake_rendermass_imports
    del bpy.types.Scene.icomake_rendermass_imports_index

if __name__ == "__main__":
    register()