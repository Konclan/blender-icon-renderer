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

resolutions = [
    ("16", "16x16", ""),
    ("32", "32x32", ""),
    ("64", "64x64", ""),
    ("128", "128x128", ""),
    ("256", "256x256", ""),
    ("512", "512x512", ""),
    ("1024", "1024x1024", ""),
]

class IM_SceneProps(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    
    render_output: bpy.props.StringProperty(
        name="Render Directory",
        description="Directory renders are saved to",
        default="//",
        subtype='DIR_PATH')
        
    render_resolution: bpy.props.EnumProperty(
        name="Resolution",
        items=resolutions,
        description="Resolution of rendered icon",
        default="256",)
    
    render_cleanup: bpy.props.BoolProperty(
        name="Post Render Cleanup",
        description="Cleanup data after rendering?",
        default=True,)


class IM_ObjectProps(bpy.types.PropertyGroup):
    
    render_position: bpy.props.EnumProperty(
        name="Position",
        items=position_options,
        description="Position of the model in PeTI",
        default="FLOOR",)
    
    


def menu_func(self, context):
    self.layout.operator(renderer.IM_RenderActive.bl_idname)
    self.layout.operator(renderer.IM_CleanUp.bl_idname)
    

_classes = (
    IM_SceneProps,
    IM_ObjectProps,
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
    
    bpy.types.Object.icomake_object_props = make_pointer(IM_ObjectProps, "Icon Maker Object Properties")
    
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.
        

def unregister():
    for cls in _classes:
        bpy.utils.unregister_class(cls)
        
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    
    del bpy.types.Scene.icomake_props
    del bpy.types.Object.icomake_object_props

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()