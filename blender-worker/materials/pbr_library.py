"""
SceneForge AI - PBR Material Library for Blender Automation
Constructs physically accurate Principled BSDF node trees.
"""

from typing import Tuple, Optional

def create_pbr_shader(
    bpy_module,
    name: str,
    base_color: Tuple[float, float, float, float] = (0.9, 0.9, 0.9, 1.0),
    roughness: float = 0.2,
    metallic: float = 0.0,
    transmission: float = 0.0,
    ior: float = 1.45,
    procedural_texture: str = "none"
):
    """
    Constructs a Principled BSDF shader network in Blender 4.x.
    """
    bpy = bpy_module
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    output_node.location = (600, 0)

    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)

    # Base Color & Physical Constants
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic

    # Blender 4.x uses 'Transmission Weight', earlier versions use 'Transmission'
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = transmission

    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = ior

    # Procedural Shader Sub-networks
    if procedural_texture == "teak_stripes":
        # Wave Texture + ColorRamp for teak wood decking planks
        tex_coord = nodes.new(type="ShaderNodeTexCoord")
        tex_coord.location = (-600, 0)
        
        mapping = nodes.new(type="ShaderNodeMapping")
        mapping.location = (-400, 0)
        mapping.inputs["Scale"].default_value = (15.0, 1.0, 1.0)
        
        wave = nodes.new(type="ShaderNodeTexWave")
        wave.location = (-200, 0)
        wave.wave_type = "BANDS"
        wave.bands_direction = "X"
        wave.inputs["Scale"].default_value = 8.0
        wave.inputs["Distortion"].default_value = 0.5
        
        ramp = nodes.new(type="ShaderNodeValToRGB")
        ramp.location = (0, 0)
        ramp.color_ramp.elements[0].position = 0.4
        ramp.color_ramp.elements[0].color = (0.35, 0.20, 0.10, 1.0) # dark seam
        ramp.color_ramp.elements[1].position = 0.6
        ramp.color_ramp.elements[1].color = base_color             # teak plank

        links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
        links.new(wave.outputs["Color"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    links.new(bsdf.outputs["BSDF"], output_node.inputs["Surface"])
    return mat
