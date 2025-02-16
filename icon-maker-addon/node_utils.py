import bpy
from . import utils

def nodesCleanMat(material):
    material.use_nodes = True
    
    for node in material.node_tree.nodes:
        material.node_tree.nodes.remove(node)
        
def nodesPMShader():    
    nodeGroup = bpy.data.node_groups.new(type="ShaderNodeTree", name="[ICOMAKE] NGPmShader")
    nodeGroup.interface.new_socket('Color', in_out='INPUT', socket_type='NodeSocketColor')
    nodeGroup.interface.new_socket('Emission Strength', in_out='INPUT', socket_type='NodeSocketFloat')
    nodeGroup.interface.new_socket('Output', in_out='OUTPUT', socket_type='NodeSocketShader')
    
    utils.setData(nodeGroup, "icomake_nodedata")

    nodeInputs = nodeGroup.nodes.new('NodeGroupInput')
    nodeInputs.location = (0, 0)
    nodeOutputs = nodeGroup.nodes.new('NodeGroupOutput')
    nodeOutputs.location = (2200, 0)

    nodeEmission1 = nodeGroup.nodes.new('ShaderNodeEmission')
    nodeEmission1.location = (200, 0)
    nodeShaderRGB1 = nodeGroup.nodes.new('ShaderNodeShaderToRGB')
    nodeShaderRGB1.location = (400, 0)

    nodeBsdfPrincipled = nodeGroup.nodes.new('ShaderNodeBsdfPrincipled')
    nodeBsdfPrincipled.location = (200, -200)

    nodeShaderRGB2 = nodeGroup.nodes.new('ShaderNodeShaderToRGB')
    nodeShaderRGB2.location = (500, -200)
    nodeSeparateHSV = nodeGroup.nodes.new('ShaderNodeSeparateHSV')
    nodeSeparateHSV.location = (700, -400)
    nodeCombineXYZ = nodeGroup.nodes.new('ShaderNodeCombineXYZ')
    nodeCombineXYZ.location = (900, -400)
    nodeColorRamp = nodeGroup.nodes.new('ShaderNodeValToRGB')
    nodeColorRamp.location = (1100, -400)
    nodeColorRamp.color_ramp.elements.new(0.25)
    nodeColorRamp.color_ramp.elements.new(0.375)
    nodeColorRamp.color_ramp.elements.new(0.5)
    nodeColorRamp.color_ramp.elements.new(0.625)
    nodeColorRamp.color_ramp.elements.new(0.75)
    nodeColorRamp.color_ramp.elements[0].color = (0.0512695, 0.0578054, 0.0595113, 1)
    nodeColorRamp.color_ramp.elements[1].color = (0.0512695, 0.0578054, 0.0595113, 1)
    nodeColorRamp.color_ramp.elements[2].color = (0.114435, 0.116971, 0.111932, 1)
    nodeColorRamp.color_ramp.elements[3].color = (0.283094, 0.286361, 0.287214, 1)
    nodeColorRamp.color_ramp.elements[4].color = (0.473532, 0.473532, 0.428691, 1)
    nodeColorRamp.color_ramp.elements[5].color = (0.508881, 0.508882, 0.514918, 1)
    nodeColorRamp.color_ramp.elements[6].color = (0.395988, 0.397621, 0.401066, 1)

    nodeMultiplyRGB = nodeGroup.nodes.new('ShaderNodeMixRGB')
    nodeMultiplyRGB.location = (1400, -200)
    nodeMultiplyRGB.blend_type = "MULTIPLY"
    nodeEmission2 = nodeGroup.nodes.new('ShaderNodeEmission')
    nodeEmission2.location = (1600, -200)
    nodeEmission2.inputs[1].default_value = 18
    nodeShaderRGB3 = nodeGroup.nodes.new('ShaderNodeShaderToRGB')
    nodeShaderRGB3.location = (1800, -200)

    nodeMixRGB = nodeGroup.nodes.new('ShaderNodeMixRGB')
    nodeMixRGB.location = (2000, 0)

    # Connections

    nodeGroup.links.new(nodeInputs.outputs[0], nodeEmission1.inputs[0])
    nodeGroup.links.new(nodeInputs.outputs[1], nodeEmission1.inputs[1])
    nodeGroup.links.new(nodeEmission1.outputs[0], nodeShaderRGB1.inputs[0])
    nodeGroup.links.new(nodeShaderRGB1.outputs[0], nodeMixRGB.inputs[1])
    nodeGroup.links.new(nodeInputs.outputs[0], nodeBsdfPrincipled.inputs[0])
    nodeGroup.links.new(nodeBsdfPrincipled.outputs[0], nodeShaderRGB2.inputs[0])
    nodeGroup.links.new(nodeShaderRGB2.outputs[0], nodeMultiplyRGB.inputs[1])
    nodeGroup.links.new(nodeBsdfPrincipled.outputs[0], nodeShaderRGB2.inputs[0])
    nodeGroup.links.new(nodeShaderRGB2.outputs[0], nodeSeparateHSV.inputs[0])
    nodeGroup.links.new(nodeSeparateHSV.outputs[2], nodeCombineXYZ.inputs[0])
    nodeGroup.links.new(nodeCombineXYZ.outputs[0], nodeColorRamp.inputs[0])
    nodeGroup.links.new(nodeColorRamp.outputs[0], nodeMultiplyRGB.inputs[2])
    nodeGroup.links.new(nodeMultiplyRGB.outputs[0], nodeEmission2.inputs[0])
    nodeGroup.links.new(nodeEmission2.outputs[0], nodeShaderRGB3.inputs[0])
    nodeGroup.links.new(nodeShaderRGB3.outputs[0], nodeMixRGB.inputs[2])
    nodeGroup.links.new(nodeMixRGB.outputs[0], nodeOutputs.inputs[0])

def nodesShadowCatcher():
    nodeGroup = bpy.data.node_groups.new(type="ShaderNodeTree", name="[ICOMAKE] NGShadowCatcher")
    nodeGroup.interface.new_socket('Output', in_out='OUTPUT', socket_type='NodeSocketShader')
    
    utils.setData(nodeGroup, "icomake_nodedata")

    nodeOutputs = nodeGroup.nodes.new('NodeGroupOutput')
    nodeOutputs.location = (1200, 0)

    nodeBsdfDiffuse1 = nodeGroup.nodes.new('ShaderNodeBsdfDiffuse')
    nodeBsdfDiffuse1.location = (0, 0)
    nodeBsdfDiffuse2 = nodeGroup.nodes.new('ShaderNodeBsdfDiffuse')
    nodeBsdfDiffuse2.location = (200, 0)
    nodeBsdfDiffuse2.inputs[0].default_value = (0.417885, 0.434154, 0.434154, 1)
    nodeBsdTransparent = nodeGroup.nodes.new('ShaderNodeBsdfTransparent')
    nodeBsdTransparent.location = (400, 0)

    nodeShaderRGB = nodeGroup.nodes.new('ShaderNodeShaderToRGB')
    nodeShaderRGB.location = (600, 0)

    nodeColorRamp = nodeGroup.nodes.new('ShaderNodeValToRGB')
    nodeColorRamp.location = (800, 0)
    nodeColorRamp.color_ramp.elements[1].position = 0.1
    nodeColorRamp.color_ramp.elements[0].color = (1, 1, 1, 1)
    nodeColorRamp.color_ramp.elements[1].color = (0, 0, 0, 1)

    nodeMixShader = nodeGroup.nodes.new('ShaderNodeMixShader')
    nodeMixShader.location = (1000, 0)

    # Connections

    nodeGroup.links.new(nodeBsdfDiffuse1.outputs[0], nodeShaderRGB.inputs[0])
    nodeGroup.links.new(nodeShaderRGB.outputs[0], nodeColorRamp.inputs[0])
    nodeGroup.links.new(nodeColorRamp.outputs[0], nodeMixShader.inputs[0])
    nodeGroup.links.new(nodeBsdTransparent.outputs[0], nodeMixShader.inputs[1])
    nodeGroup.links.new(nodeBsdfDiffuse2.outputs[0], nodeMixShader.inputs[2])
    nodeGroup.links.new(nodeMixShader.outputs[0], nodeOutputs.inputs[0])

def nodesMatModel(material, image):

    nodesCleanMat(material)
    
    # Check for Node Group
    if not bpy.data.node_groups.get("[ICOMAKE] NGPmShader"):
        nodesPMShader()
        
    #print(material.name)

    # Create nodes
    nodeOutput = material.node_tree.nodes.new("ShaderNodeOutputMaterial")
    nodeOutput.location = (500, 0)
    nodeTexImage = material.node_tree.nodes.new("ShaderNodeTexImage")
    nodeTexImage.location = (0, 0)
    nodeTexImage.image = image
    nodeShader = material.node_tree.nodes.new("ShaderNodeGroup")
    nodeShader.location = (300, 0)
    nodeShader.node_tree = bpy.data.node_groups['[ICOMAKE] NGPmShader']

    # Connect our nodes
    material.node_tree.links.new(nodeTexImage.outputs[0], nodeShader.inputs[0])
    material.node_tree.links.new(nodeTexImage.outputs[1], nodeShader.inputs[1])
    material.node_tree.links.new(nodeShader.outputs[0], nodeOutput.inputs[0])
    
def nodesMatShadow(material):
    nodesCleanMat(material)
    
    # Check for Node Group
    if not bpy.data.node_groups.get("[ICOMAKE] NGShadowCatcher"):
        nodesShadowCatcher()
    
    # Create nodes
    nodeOutput = material.node_tree.nodes.new("ShaderNodeOutputMaterial")
    nodeOutput.location = (200, 0)
    nodeShader = material.node_tree.nodes.new("ShaderNodeGroup")
    nodeShader.location = (0, 0)
    nodeShader.node_tree = bpy.data.node_groups['[ICOMAKE] NGShadowCatcher']
    
    # Link nodes
    material.node_tree.links.new(nodeShader.outputs[0], nodeOutput.inputs[0])

def nodesCompositing(objectLayer, shadowLayer, shadows = True):
    bpy.context.scene.use_nodes = True
    compTree = bpy.context.scene.node_tree
    
    for node in compTree.nodes:
        compTree.nodes.remove(node)
    
    comp_node = compTree.nodes.new('CompositorNodeComposite')
    comp_node.location = (600, 0)
    
    layer_node_object = compTree.nodes.new("CompositorNodeRLayers")
    layer_node_object.location = (0, 0)
    layer_node_object.layer = objectLayer.name

    layer_node_shadow = compTree.nodes.new("CompositorNodeRLayers")
    layer_node_shadow.location = (0, -800)
    layer_node_shadow.layer = shadowLayer.name

    comp_node_alphaOver = compTree.nodes.new("CompositorNodeAlphaOver")
    comp_node_alphaOver.location = (400, 0)

    compTree.links.new(layer_node_object.outputs[0], comp_node_alphaOver.inputs[2])
    compTree.links.new(layer_node_shadow.outputs[0], comp_node_alphaOver.inputs[1])
    compTree.links.new(comp_node_alphaOver.outputs[0], comp_node.inputs[0])

def getNodesByType(node_tree, type):
    foundNodes = []
    for node in node_tree.nodes:
        if node.type == type:
            foundNodes.append(node)
            
    return foundNodes