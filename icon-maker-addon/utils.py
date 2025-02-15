import bpy
import tempfile
import itertools as IT
import os

def setData(obj, data_name = "icomake_tempdata", new_data = True):
#    print("Data Name = " + data_name)
#    print("Object = " + object.name)
#    print("Object Type = " + getattr(object, 'type', ''))
#    objType = getattr(object, 'type', '')
    obj[data_name] = new_data
    if ("bpy_types.Object" in str(type(obj)) and 
        obj.data is not None):
#        print("Object Data = " + object.data.name)
        obj.data[data_name] = new_data

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
#            print("Data Type: " + str(type(data)))
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

def deselectAll():
    for obj in bpy.data.objects:
        obj.select_set(False)
    bpy.context.view_layer.objects.active = None

def selectObjects(context, objects):
    deselectAll()
    context.view_layer.objects.active = objects[0]
    for obj in objects:
        obj.select_set(True)

def include_only_one_collection(view_layer: bpy.types.ViewLayer, collection_include: bpy.types.Collection):
    parent_collections = []
    parent_collections.append(collection_include.name)
    get_parent_collection_names(collection_include, parent_collections)
#    print("!!!Collections:")
#    for col in parent_collections:
#        print(col)
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

def group_dimensions(objs):
    
    scd1 = [0,0,0]
    
    minx = 0
    miny = 0
    minz = 0
    
    maxx = 0
    maxy = 0
    maxz = 0
    
    
    c1=0
    
    for o1 in objs:
    
        if o1.type != "MESH":
            pass
    
        else:
            bounds = get_object_bounds(o1)
    
        
            oxmin = bounds[0][0]
            oxmax = bounds[1][0]
        
            oymin = bounds[0][1]
            oymax = bounds[1][1]
        
            ozmin = bounds[0][2]
            ozmax = bounds[1][2]
    
            if  c1 == 0 :
                minx = oxmin
                miny = oymin
                minz = ozmin
    
                maxx = oxmax
                maxy = oymax
                maxz = ozmax
    
         # min 
    
            if oxmin <= minx:
                minx = oxmin
    
            if oymin <= miny:
                miny = oymin
    
            if ozmin <= minz:
                minz = ozmin
    
        # max 
    
            if oxmax >= maxx:
                maxx = oxmax
    
            if oymax >= maxy:
                maxy = oymax
    
            if ozmax >= maxz:
                maxz = ozmax
    
        c1+=1
    
    
    widhtx=(maxx-minx)
    
    widhty=maxy-miny
    
    widhtz=maxz-minz
    
    
    scd = [widhtx ,widhty ,widhtz]
    
    scd1 = scd
    
    return scd1

def get_object_bounds(obj):

    obminx = obj.location.x
    obminy = obj.location.y
    obminz = obj.location.z

    obmaxx = obj.location.x
    obmaxy = obj.location.y
    obmaxz = obj.location.z

    for vertex in obj.bound_box[:]:

        x = obj.location.x + (obj.scale.x * vertex[0])
        y = obj.location.y + (obj.scale.y * vertex[1])
        z = obj.location.z + (obj.scale.z * vertex[2])

        if x <= obminx:
            obminx = x
        if y <= obminy:
            obminy = y
        if z <= obminz:
            obminz = z

        if x >= obmaxx:
            obmaxx = x
        if y >= obmaxy:
            obmaxy = y
        if z >= obmaxz:
            obmaxz = z

    boundsmin = [obminx,obminy,obminz]
    boundsmax = [obmaxx,obmaxy,obmaxz] 

    bounds = [boundsmin,boundsmax]


    return bounds