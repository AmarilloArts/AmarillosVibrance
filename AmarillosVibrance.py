bl_info = {
    "name": "Amarillo's Vibrance",
    "author": "Amarillo",
    "version": (4, 0),
    "blender": (4, 4, 0),
    "location": "Node Editor > Add > Color > Amarillo's Vibrance",
    "description": "Applies vibrance with falloff control for saturated areas. RGB-safe, brightness-preserving.",
    "category": "Node",
}

import bpy

def create_vibrance_group():
    name = "Amarillo's Vibrance"
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    group = bpy.data.node_groups.new(name, "CompositorNodeTree")

    # Interface
    group.interface.new_socket("Image", in_out='INPUT', socket_type='NodeSocketColor')
    v = group.interface.new_socket("Vibrance", in_out='INPUT', socket_type='NodeSocketFloat')
    v.default_value = 1.0
    v.min_value = 0.0
    boost = group.interface.new_socket("Saturation Boost", in_out='INPUT', socket_type='NodeSocketFloat')
    boost.default_value = 0.0
    boost.min_value = 0.0
    boost.max_value = 1.0
    f = group.interface.new_socket("Fac", in_out='INPUT', socket_type='NodeSocketFloat')
    f.default_value = 1.0
    f.min_value = 0.0
    f.max_value = 1.0
    group.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')

    input = group.nodes.new("NodeGroupInput")
    input.location = (-1000, 0)
    output = group.nodes.new("NodeGroupOutput")
    output.location = (1000, 0)

    # Separate RGB
    sep = group.nodes.new("CompositorNodeSeparateXYZ")
    sep.location = (-800, 0)

    # Luminance (gray)
    avg1 = group.nodes.new("CompositorNodeMath")
    avg1.operation = 'ADD'
    avg1.location = (-600, 100)

    avg2 = group.nodes.new("CompositorNodeMath")
    avg2.operation = 'ADD'
    avg2.location = (-400, 100)

    div3 = group.nodes.new("CompositorNodeMath")
    div3.operation = 'DIVIDE'
    div3.inputs[1].default_value = 3.0
    div3.location = (-200, 100)

    # Diff from gray
    diff_r = group.nodes.new("CompositorNodeMath")
    diff_r.operation = 'SUBTRACT'
    diff_r.location = (-600, -100)

    diff_g = group.nodes.new("CompositorNodeMath")
    diff_g.operation = 'SUBTRACT'
    diff_g.location = (-600, -150)

    diff_b = group.nodes.new("CompositorNodeMath")
    diff_b.operation = 'SUBTRACT'
    diff_b.location = (-600, -200)

    # Saturation estimate: max - min
    max1 = group.nodes.new("CompositorNodeMath")
    max1.operation = 'MAXIMUM'
    max1.location = (-800, -300)

    max2 = group.nodes.new("CompositorNodeMath")
    max2.operation = 'MAXIMUM'
    max2.location = (-600, -300)

    min1 = group.nodes.new("CompositorNodeMath")
    min1.operation = 'MINIMUM'
    min1.location = (-800, -350)

    min2 = group.nodes.new("CompositorNodeMath")
    min2.operation = 'MINIMUM'
    min2.location = (-600, -350)

    sat = group.nodes.new("CompositorNodeMath")
    sat.operation = 'SUBTRACT'
    sat.location = (-400, -325)

    inv_sat = group.nodes.new("CompositorNodeMath")
    inv_sat.operation = 'SUBTRACT'
    inv_sat.inputs[0].default_value = 1.0
    inv_sat.location = (-200, -325)

    curve = group.nodes.new("CompositorNodeMath")
    curve.operation = 'POWER'
    curve.location = (0, -325)

    scaled = group.nodes.new("CompositorNodeMath")
    scaled.operation = 'MULTIPLY'
    scaled.location = (200, -325)

    final_boost = group.nodes.new("CompositorNodeMath")
    final_boost.operation = 'ADD'
    final_boost.inputs[0].default_value = 1.0
    final_boost.location = (400, -325)

    # Adjust RGB: gray + (channel - gray) * boost
    mult_r = group.nodes.new("CompositorNodeMath")
    mult_r.operation = 'MULTIPLY'
    mult_r.location = (200, -100)

    add_r = group.nodes.new("CompositorNodeMath")
    add_r.operation = 'ADD'
    add_r.location = (400, -100)

    mult_g = group.nodes.new("CompositorNodeMath")
    mult_g.operation = 'MULTIPLY'
    mult_g.location = (200, -150)

    add_g = group.nodes.new("CompositorNodeMath")
    add_g.operation = 'ADD'
    add_g.location = (400, -150)

    mult_b = group.nodes.new("CompositorNodeMath")
    mult_b.operation = 'MULTIPLY'
    mult_b.location = (200, -200)

    add_b = group.nodes.new("CompositorNodeMath")
    add_b.operation = 'ADD'
    add_b.location = (400, -200)

    combine = group.nodes.new("CompositorNodeCombineXYZ")
    combine.location = (600, -150)

    mix = group.nodes.new("CompositorNodeMixRGB")
    mix.blend_type = 'MIX'
    mix.location = (800, 0)

    # Wiring
    group.links.new(input.outputs["Image"], sep.inputs[0])

    # Gray
    group.links.new(sep.outputs[0], avg1.inputs[0])
    group.links.new(sep.outputs[1], avg1.inputs[1])
    group.links.new(avg1.outputs[0], avg2.inputs[0])
    group.links.new(sep.outputs[2], avg2.inputs[1])
    group.links.new(avg2.outputs[0], div3.inputs[0])  # gray

    # Diff
    group.links.new(sep.outputs[0], diff_r.inputs[0])
    group.links.new(div3.outputs[0], diff_r.inputs[1])
    group.links.new(sep.outputs[1], diff_g.inputs[0])
    group.links.new(div3.outputs[0], diff_g.inputs[1])
    group.links.new(sep.outputs[2], diff_b.inputs[0])
    group.links.new(div3.outputs[0], diff_b.inputs[1])

    # Saturation
    group.links.new(sep.outputs[0], max1.inputs[0])
    group.links.new(sep.outputs[1], max1.inputs[1])
    group.links.new(max1.outputs[0], max2.inputs[0])
    group.links.new(sep.outputs[2], max2.inputs[1])
    group.links.new(sep.outputs[0], min1.inputs[0])
    group.links.new(sep.outputs[1], min1.inputs[1])
    group.links.new(min1.outputs[0], min2.inputs[0])
    group.links.new(sep.outputs[2], min2.inputs[1])
    group.links.new(max2.outputs[0], sat.inputs[0])
    group.links.new(min2.outputs[0], sat.inputs[1])
    group.links.new(sat.outputs[0], inv_sat.inputs[1])
    group.links.new(inv_sat.outputs[0], curve.inputs[0])
    invert_boost = group.nodes.new("CompositorNodeMath")
    invert_boost.operation = 'SUBTRACT'
    invert_boost.inputs[0].default_value = 1.0
    invert_boost.location = (-50, -250)

    remap_boost = group.nodes.new("CompositorNodeMath")
    remap_boost.operation = 'MULTIPLY'
    remap_boost.inputs[1].default_value = 5.0
    remap_boost.location = (100, -250)
    group.links.new(input.outputs["Saturation Boost"], invert_boost.inputs[1])
    group.links.new(invert_boost.outputs[0], remap_boost.inputs[0])
    group.links.new(remap_boost.outputs[0], curve.inputs[1])
    group.links.new(curve.outputs[0], scaled.inputs[0])
    group.links.new(input.outputs["Vibrance"], scaled.inputs[1])
    group.links.new(scaled.outputs[0], final_boost.inputs[1])

    # R
    group.links.new(diff_r.outputs[0], mult_r.inputs[0])
    group.links.new(final_boost.outputs[0], mult_r.inputs[1])
    group.links.new(div3.outputs[0], add_r.inputs[0])
    group.links.new(mult_r.outputs[0], add_r.inputs[1])

    # G
    group.links.new(diff_g.outputs[0], mult_g.inputs[0])
    group.links.new(final_boost.outputs[0], mult_g.inputs[1])
    group.links.new(div3.outputs[0], add_g.inputs[0])
    group.links.new(mult_g.outputs[0], add_g.inputs[1])

    # B
    group.links.new(diff_b.outputs[0], mult_b.inputs[0])
    group.links.new(final_boost.outputs[0], mult_b.inputs[1])
    group.links.new(div3.outputs[0], add_b.inputs[0])
    group.links.new(mult_b.outputs[0], add_b.inputs[1])

    group.links.new(add_r.outputs[0], combine.inputs[0])
    group.links.new(add_g.outputs[0], combine.inputs[1])
    group.links.new(add_b.outputs[0], combine.inputs[2])

    group.links.new(input.outputs["Fac"], mix.inputs[0])
    group.links.new(input.outputs["Image"], mix.inputs[1])
    group.links.new(combine.outputs[0], mix.inputs[2])
    group.links.new(mix.outputs[0], output.inputs["Image"])

    return group

import bpy.app.timers

def safe_create_vibrance_group():
    try:
        create_vibrance_group()
    except:
        return 0.5  # Retry in 0.5 seconds
    return None  # Done

def register():
    bpy.app.timers.register(safe_create_vibrance_group, first_interval=0.1)

def unregister():
    if "Amarillo's Vibrance" in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups["Amarillo's Vibrance"])


if __name__ == "__main__":
    register()
