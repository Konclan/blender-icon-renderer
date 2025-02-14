bl_info = {
	"name": "Icon Maker",
	"author": "Konclan",
	"version": (2, 0, 0),
	"blender": (4, 3, 2),
	"category": "Render",
	"location": "Scene properties",
	"description": "Item icon rendering tool for BEEmod",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
}

import bpy
from . import renderer, gui, node_utils, utils, im_objs
import importlib

for module in [renderer, gui, node_utils, utils, im_objs]:
    importlib.reload(module)

position_options = [
    ("FLOOR", "Floor", "Item is on the floor"),
    ("WALL", "Wall", "Item is on the wall"),
    ("CEIL", "Ceiling", "Item is on the ceiling"),
]

class IM_SceneProps(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    
    render_output: bpy.props.StringProperty(
        name="Render Directory",
        description="Directory renders are saved to",
        default="//",
        subtype='DIR_PATH')

#    render_position: bpy.props.EnumProperty(
#        name="Position",
#        items=position_options,
#        description="Position of the model in PeTI",
#        default="FLOOR",)


def menu_func(self, context):
    self.layout.operator(renderer.IM_RenderActive.bl_idname)
    self.layout.operator(renderer.IM_CleanUp.bl_idname)
    

_classes = (
    IM_SceneProps,
    renderer.IM_RenderActive,
    renderer.IM_CleanUp,
    gui.IM_GUI_PT_RenderActive,
    gui.IM_3DViewPanel,
    gui.IM_ShaderPanel,
    im_objs.IM_AddDefObject,
    im_objs.IM_PMShaderTree,
)

def register():

    def make_pointer(prop_type, prop_name):
        return bpy.props.PointerProperty(name=prop_name,type=prop_type)
    
    for cls in _classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.icomake_props = make_pointer(IM_SceneProps, "Icon Maker Settings")
    
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.
        

def unregister():
    for cls in _classes:
        bpy.utils.unregister_class(cls)
        
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    
    del bpy.types.Scene.icomake_props

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()