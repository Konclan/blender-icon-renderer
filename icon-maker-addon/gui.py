import bpy
import os.path

class IM_GUI_FL_UL_ImportList(bpy.types.UIList):
    """IM_GUI Import List."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        import_icon = 'FILE'
        position_icon = 'OUTLINER_OB_EMPTY'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=os.path.basename(item.name), icon = import_icon)
            layout.label(text=item.position, icon = position_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = import_icon)


class IM_GUI_FL_OT_NewItem(bpy.types.Operator):
    """Add a new file(s) to the list."""

    bl_idname = "icomake_gui_fl.new_item"
    bl_label = "Add a new file"

    files: bpy.props.CollectionProperty(name="File Path",type=bpy.types.OperatorFileListElement,)
    directory: bpy.props.StringProperty(subtype='DIR_PATH',)
    
    filter_glob: bpy.props.StringProperty( default='*.smd;*.obj', options={'HIDDEN'} )

    filename_ext = ""

    def execute(self, context):
        directory = self.directory
        
        for file_elem in self.files:
            file = context.scene.icomake_rendermass_imports.add()
            file.name = file_elem.name
            file.path = os.path.relpath(directory, bpy.path.abspath("//"))
        return {'FINISHED'}

    def invoke(self, context, event):

        context.window_manager.fileselect_add(self) 
        
        return {'RUNNING_MODAL'}  
        # Tells Blender to hang on for the slow user input


class IM_GUI_FL_OT_DeleteItem(bpy.types.Operator):
    """Remove the selected files from the list."""

    bl_idname = "icomake_gui_fl.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.scene.icomake_rendermass_imports

    def execute(self, context):
        filelist = context.scene.icomake_rendermass_imports
        index = context.scene.icomake_rendermass_imports_index

        filelist.remove(index)
        context.scene.icomake_rendermass_imports_index = min(max(0, index - 1), len(filelist) - 1)

        return{'FINISHED'}

class IM_GUI_FL_OT_Clear(bpy.types.Operator):
    """Remove the selected files from the list."""

    bl_idname = "icomake_gui_fl.clear"
    bl_label = "Removes all item"

    @classmethod
    def poll(cls, context):
        return context.scene.icomake_rendermass_imports

    def execute(self, context):        
        context.scene.icomake_rendermass_imports.clear()
        context.scene.icomake_rendermass_imports_index = 0

        return{'FINISHED'}


class IM_GUI_FL_OT_MoveItem(bpy.types.Operator):
    """Move an item in the list."""

    bl_idname = "icomake_gui_fl.move_item"
    bl_label = "Move an item in the list"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        return context.scene.icomake_rendermass_imports

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.scene.icomake_rendermass_imports_index
        list_length = len(bpy.context.scene.icomake_rendermass_imports) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.scene.icomake_rendermass_imports_index = max(0, min(new_index, list_length))

    def execute(self, context):
        filelist = context.scene.icomake_rendermass_imports
        index = context.scene.icomake_rendermass_imports_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        filelist.move(neighbor, index)
        self.move_index()

        return{'FINISHED'}


class IM_GUI_PT_RenderMass(bpy.types.Panel):
    """Icon Maker Mass Render Panel."""

    bl_label = "Icons Maker Mass Render"
    bl_idname = "SCENE_PT_ICOMAKE_GUI_RENDERMASS"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Model List:")
        row = layout.row()
        row.template_list("IM_GUI_FL_UL_ImportList", "ICOMAKE_GUI_FL", scene,
                          "icomake_rendermass_imports", scene, "icomake_rendermass_imports_index")

        row = layout.row()
        row.operator('icomake_gui_fl.new_item', text='ADD')
        row.operator('icomake_gui_fl.delete_item', text='REMOVE')
        row.operator('icomake_gui_fl.move_item', text='MOVE UP').direction = 'UP'
        row.operator('icomake_gui_fl.move_item', text='MOVE DOWN').direction = 'DOWN'
        row.operator('icomake_gui_fl.clear', text='CLEAR')

        if scene.icomake_rendermass_imports_index >= 0 and scene.icomake_rendermass_imports:
            item = scene.icomake_rendermass_imports[scene.icomake_rendermass_imports_index]

            row = layout.row()
            row.prop(item, "name")
            row.prop(item, "path")
            
            row = layout.row()
            row.prop(item, "position")
            row.prop(item, "outline")
        
        layout.label(text="Options:")
        row = layout.row()
        row.prop(scene.icomake_props, "rendermass_output")
        
        layout.label(text="Operators:")
        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.rendermass")

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
        row.prop(scene.icomake_props, "renderselected_outline")

        row = layout.row()
        row.prop(scene.icomake_props, "renderselected_output")

        layout.label(text="Operators:")
        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.materialselected")

        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.renderselected")

        row = layout.row()
        row.scale_y = 2.0
        row.operator("icomake.cleanup")

#class IM_GUI_FL_UL_DataList(bpy.types.UIList):
#    """IM_GUI Data List."""
#
#    def draw_item(self, context, layout, data, item, icon, active_data,
#                  active_propname, index):
#
#        # We could write some code to decide which icon to use here...
#        data_icon = 'RNA'
#
#        # Make sure your code supports all 3 layout types
#        if self.layout_type in {'DEFAULT', 'COMPACT'}:
#            layout.label(text = item.name, icon = data_icon)
#            layout.label(text = item.type)
#
#        elif self.layout_type in {'GRID'}:
#            layout.alignment = 'CENTER'
#            layout.label(text="", icon = data_icon)
#
#class IM_GUI_PT_Data(bpy.types.Panel):
#    """Render Icons GUI."""
#
#    bl_label = "Icon Maker Data"
#    bl_idname = "SCENE_PT_ICOMAKE_GUI_DATA"
#    bl_space_type = 'PROPERTIES'
#    bl_region_type = 'WINDOW'
#    bl_context = "scene"
#
#    def draw(self, context):
#        layout = self.layout
#        scene = context.scene
#
#        row = layout.row()
#        row.template_list("IM_GUI_FL_UL_DataList", "ICOMAKE_GUI_DL", scene,
#                          "icomake_data", scene, "icomake_data_index")

