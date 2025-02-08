import bpy
import os.path

class IM_GUI_PT_RenderSelected(bpy.types.Panel):
    """Icon Maker Render Selected Panel."""

    bl_label = "Icons Maker Render Selected"
    bl_idname = "SCENE_PT_ICOMAKE_GUI_RENDERSELECTED"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Options:")
        row = layout.row()
        row.prop(scene.icomake_props, "renderselected_position")

        row = layout.row()
        row.prop(scene.icomake_props, "renderselected_output")

        layout.label(text="Operators:")

        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.renderselected")

        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.cleanup")

class ShaderEditorPanel:
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        return (context.material is not None)

class IM_ShaderPanel(ShaderEditorPanel, bpy.types.Panel):
    bl_idname = "IM_ShaderPanel"
    bl_label = "ICOMAKE Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Operators:")
        
        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.pmshadertree")