import bpy
import tempfile
import itertools as IT
import os

def setData(object, data_name = "icomake_tempdata"):
    #print("Data Name = " + data_name)
    #print("Object = " + object.name)
    #print("Object Type = " + str(type(object)))
    object[data_name] = True
    if "bpy_types.Object" in str(type(object)):
        #print("Object Data = " + object.data.name)
        object.data[data_name] = True

def getData(data_name):
    data = []
    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.lights,
            bpy.data.cameras,
            bpy.data.materials,
            bpy.data.images,
            bpy.data.armatures,
            bpy.data.collections,
    ):
        for id_data in bpy_data_iter:
            if id_data.get(data_name, False):
                data.append(id_data)

    for scene in bpy.data.scenes:
        for view_layer in scene.view_layers:
            if view_layer.get(data_name, False):
                data.append(view_layer)

    return data

# Cleanup our file of garbage
def cleanUpData(data_name):
    for data in getData(data_name):
        try: 
            #print("Data Type: " + str(type(data)))
            if "bpy_types.Object" in str(type(data)) and bpy.data.objects.get(data.name):
                bpy.data.objects.remove(bpy.data.objects[data.name], do_unlink=True)
            elif "bpy_types.Mesh" in str(type(data)) and bpy.data.meshes.get(data.name):
                bpy.data.meshes.remove(bpy.data.meshes[data.name], do_unlink=True)
            elif "bpy.types.Camera" in str(type(data)) and bpy.data.cameras.get(data.name):
                bpy.data.cameras.remove(bpy.data.cameras[data.name], do_unlink=True)
            elif "bpy.types.SunLight" in str(type(data)) and bpy.data.lights.get(data.name):
                bpy.data.lights.remove(bpy.data.lights[data.name], do_unlink=True)
            elif "bpy.types.Material" in str(type(data)) and bpy.data.materials.get(data.name):
                bpy.data.materials.remove(bpy.data.materials[data.name], do_unlink=True)
            elif "bpy.types.Image" in str(type(data)) and bpy.data.images.get(data.name):
                bpy.data.images.remove(bpy.data.images[data.name], do_unlink=True)
            elif "bpy.types.Armature" in str(type(data)) and bpy.data.armatures.get(data.name):
                bpy.data.armatures.remove(bpy.data.armatures[data.name], do_unlink=True)
            elif "bpy_types.Collection" in str(type(data)) and bpy.data.collections.get(data.name):
                bpy.data.collections.remove(bpy.data.collections[data.name], do_unlink=True)
            elif "bpy.types.ViewLayer" in str(type(data)):
                for scene in bpy.data.scenes:
                    if scene.view_layers.get(data.name):
                        scene.view_layers.remove(data)
        except Exception as e:
            print(e)

def appendObject(object, type, file):
    
    directory = file + type

    bpy.ops.wm.append(
        filepath=directory + object, 
        filename=object,
        directory=directory)

def deselectAll():
    for obj in bpy.data.objects:
        obj.select_set(False)
    bpy.context.view_layer.objects.active = None

def selectObject(object):
    deselectAll()
    bpy.context.view_layer.objects.active = object
    object.select_set(True)

def importObj(path):
    bpy.ops.import_scene.obj(filepath=path, use_edges=True, use_smooth_groups=True, use_split_objects=True, use_split_groups=False, use_groups_as_vgroups=False, use_image_search=True, split_mode='ON', global_clamp_size=0.0, axis_forward='-X', axis_up='Z')
    object = bpy.context.selected_objects[0]
    
    return object
    
def importSourceModel(path):   
    
    bpy.ops.import_scene.smd(filepath=path, append="NEW_ARMATURE")
    
    object = bpy.context.active_object.children[0]

    collection = object.users_collection[0]
    setData(collection)
    
    selectObject(object)
    
    # Apply Armature Modifier
    for modifier in object.modifiers:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    
    # Remove Armature
    objs = bpy.data.objects
    objs.remove(objs[object.parent.name], do_unlink=True)
    bpy.data.meshes.remove(bpy.data.meshes["smd_bone_vis"])
    
    return object

def get_parent_collection_names(collection, parent_collections):
    for parent_collection in bpy.data.collections:
        if collection.name in parent_collection.children.keys():
            parent_collections.append(parent_collection.name)
            get_parent_collection_names(parent_collection, parent_collections)
            return

def include_only_one_collection(view_layer: bpy.types.ViewLayer, collection_include: bpy.types.Collection):
    parent_collections = []
    parent_collections.append(collection_include.name)
    get_parent_collection_names(collection_include, parent_collections)
    #print("!!!Collections:")
    #for col in parent_collections:
    #    print(col)
    for layer_collection in view_layer.layer_collection.children:
        if not layer_collection.collection.name in parent_collections:
            layer_collection.exclude = True
        else:
            layer_collection.exclude = False

def uniquify(path, sep = ''):
    def name_sequence():
        count = IT.count()
        yield ''
        while True:
            yield '{s}{n:d}'.format(s = sep, n = next(count))
    orig = tempfile._name_sequence 
    with tempfile._once_lock:
        tempfile._name_sequence = name_sequence()
        path = os.path.normpath(path)
        dirname, basename = os.path.split(path)
        filename, ext = os.path.splitext(basename)
        fd, filename = tempfile.mkstemp(dir = dirname, prefix = filename, suffix = ext)
        tempfile._name_sequence = orig
    return filename