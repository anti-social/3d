import cadquery as cq


bed_height = 8.9
clip_thickness = 1.6
clip_height = bed_height + clip_thickness
clip_base_thickness = 2
clip_width = 20
clip_length = 12
clip_chamfer = 0.4
clip_protrusion_length = 2
clip_protrusion_height = 0.4
clip_handle_length = 18
clip_handle_offset = 5


clip = (
    cq.Workplane("XY")
    .moveTo(clip_handle_offset, 0)
    .lineTo(-clip_base_thickness, clip_height / 2 - clip_base_thickness)
    .lineTo(-clip_handle_length, clip_height / 2 - clip_base_thickness)
    .lineTo(-clip_handle_length, clip_height / 2)
    .lineTo(clip_length, clip_height / 2)
    .lineTo(clip_length, clip_height / 2 - clip_thickness)
    .sagittaArc(
        (clip_length - clip_protrusion_length, clip_height / 2 - clip_thickness),
        clip_protrusion_height
    )
    .lineTo(0, clip_height / 2 - clip_thickness)
    .lineTo(clip_handle_offset + clip_base_thickness, clip_base_thickness / 2)
    .lineTo(clip_handle_offset + clip_base_thickness, 0)
    .mirrorX()
    .extrude(clip_width)
    .edges(">Y or <Y")
    .chamfer(clip_chamfer)
)

cq.exporters.export(clip, "clip.stl")