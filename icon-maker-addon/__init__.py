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

import importlib

from . import renderer, gui, nodes, utils

for module in [renderer, gui, nodes, utils]:
    importlib.reload(module)

class IM_SceneProps(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    
    output_dir: bpy.props.StringProperty(
        name="Render Directory",
        description="Directory renders are saved to",
        default="",
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

    position_options = [
        ("FLOOR", "Floor", "Item is on the floor"),
        ("WALL", "Wall", "Item is on the wall"),
        ("CEIL", "Ceiling", "Item is on the ceiling"),
    ]
    
    position: bpy.props.EnumProperty(
        name="Position",
        items=position_options,
        description="Position of the model in PeTI",
        default="FLOOR",)
    
    outline: bpy.props.IntProperty(
        name="Ouline Thickness",
        description="Thickness of the object outline",
        default=1,)

class IM_SceneData(bpy.types.PropertyGroup):
    pass

class IM_TestOp(bpy.types.Operator):
    """Render models and export icons"""
    bl_idname = "icomake.test"
    bl_label = "MI Test Operator"
    #bl_options = {''}
    
    #@classmethod
    #def poll(cls, context):
    #    return len(context.scene.icomake_imports) > 0 and context.scene.icomake.output_dir != ""
    
    def execute(self, context):
        scene = context.scene
        
        utils.cleanUpBlend()
        
        return {'FINISHED'}
    
def menu_func(self, context):
    self.layout.operator(renderer.IM_MassRender.bl_idname)
    self.layout.operator(IM_TestOp.bl_idname)

_classes = (
    IM_SceneProps,
    IM_Imports,
    IM_SceneData,
    renderer.IM_MassRender,
    gui.IM_GUI_FL_UL_ImportList,
    gui.IM_GUI_FL_OT_NewItem,
    gui.IM_GUI_FL_OT_DeleteItem,
    gui.IM_GUI_FL_OT_Clear,
    gui.IM_GUI_FL_OT_MoveItem,
    gui.IM_GUI_PT,
    IM_TestOp,
)

def register():
    
    def make_pointer(prop_type, prop_name):
        return bpy.props.PointerProperty(name=prop_name,type=prop_type)
    
    for cls in _classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.icomake = make_pointer(IM_SceneProps, "Icon Maker Settings")

    bpy.types.Scene.icomake_imports = bpy.props.CollectionProperty(type = IM_Imports)
    bpy.types.Scene.icomake_imports_index = bpy.props.IntProperty(name = "Icon Maker Import Index",default = 0)
    
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.
        

def unregister():
    for cls in _classes:
        bpy.utils.unregister_class(cls)
        
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    
    del bpy.types.Scene.icomake
    del bpy.types.Scene.icomake_imports
    del bpy.types.Scene.icomake_imports_index

if __name__ == "__main__":
    register()