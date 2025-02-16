import bpy
import os.path

class IM_GUI_PT_RenderActive(bpy.types.Panel):
    """Icon Maker Render Active Panel."""

    bl_label = "Icons Maker Render Active"
    bl_idname = "SCENE_PT_ICOMAKE_GUI_RENDERACTIVE"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Options:")

        row = layout.row()
        row.prop(scene.icomake_props, "render_output")
        
        row = layout.row()
        row.prop(scene.icomake_props, "render_resolution")
        
        row = layout.row()
        row.prop(scene.icomake_props, "render_cleanup")

        layout.label(text="Operators:")

        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.renderactive")

        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.cleanup")

class IM_3DViewport:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

class IM_3DViewPanel(IM_3DViewport, bpy.types.Panel):
    bl_idname = "IM_3DViewPanel"
    bl_label = "ICOMAKE Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Operators:")
        
        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.adddefobject")
        
        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.renderactive")
        
        layout.label(text="Defintion:")


class IM_ShaderEditor:
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        return (context.material is not None)

class IM_ShaderPanel(IM_ShaderEditor, bpy.types.Panel):
    bl_idname = "IM_ShaderPanel"
    bl_label = "ICOMAKE Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Operators:")
        
        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.pmshadertree")