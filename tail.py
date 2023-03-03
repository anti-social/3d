import math
import operator
from functools import reduce

import cadquery as cq


# Parameters
thickness = 1

feather_amplifier_length = 17
feather_diameter = 54
feather_height = 7.5
feather_num_slices = 15
feather_slice_angle = 0.1
#feather_slice_angle = 0.0
feather_slice_height = feather_height / feather_num_slices
num_feathers = 4
feathers_angle = 360 / (num_feathers * 2)

tail_diameter = 26
tail_inner_diameter = tail_diameter - thickness * 2
tail_cone_height = 65
tail_base_height = 15
tail_height = tail_cone_height + tail_base_height

rim_height = 1.5
rim_width = 0.3
rim_hang_height = 0.1

latch_width = 1
latch_height = 21
latch_diameter = 3
latch_fillet = 1.5

Z_VECTOR = ((0, 0, 0), (0, 0, 1))
X_VECTOR = ((0, 0, 0), (1, 0, 0))


# Alternative way to form a feather
# feather = (
#     cq.Workplane("XY").workplane(invert=True)
#     .rect(feather_diameter - thickness, thickness, forConstruction=True)
# )
# feather_base = feather.toPending()
# for i in range(feather_num_slices):
#     feather = (
#         feather.newObject([
#             feather_base
#             .val()
#             .translate((0, 0, -0.5))
#             .rotate(*Z_VECTOR, feather_slice_angle * i)
#         ])
#         .toPending()
#         .loft()
#     )
#     feather_base = (
#         feather.faces("<Z").wires().toPending()
#     )


feather = (
    cq.Workplane("XY").workplane(invert=True)
    .rect(feather_diameter - thickness / 2, thickness, forConstruction=True)
    .toPending()
    .extrude(
        feather_slice_height
        if feather_slice_angle > 0
        else feather_height
    )
)
if feather_slice_angle > 0:
    for i in range(feather_num_slices - 1):
        feather = (
            feather
            .faces("<Z")
            .wires()
            .toPending()
            .workplane()
            .twistExtrude(feather_slice_height, feather_slice_angle * (i + 1))
        )

feather_amplifier = (
    cq.Workplane("XY")
    .polyline([
        (-feather_amplifier_length, 0, 0),
        (0, feather_amplifier_length, 0),
        (feather_amplifier_length, 0, 0),
    ])
    .close()
    .extrude(thickness)
    .rotate(*X_VECTOR, 90)
    .translate((0, thickness / 2, 0))
)
feather += feather_amplifier

stabilizer = reduce(
    operator.add,
    (
        cq.Workplane("XY").newObject([
            feather.val().rotate((0, 0, 0), (0, 0, 1), feathers_angle * i)
        ])
        for i in range(num_feathers)
    )
)
stabilizer = stabilizer.translate((0, 0, feather_height))

# Circle around feathers
stabilizer += (
    cq.Workplane("XY")
    .circle(feather_diameter / 2)
    .extrude(feather_height)
    .faces(">Z")
    .workplane()
    .hole(feather_diameter - thickness * 2)
)

cone = (
    cq.Workplane("XY").circle(2.5)
    .workplane(offset=tail_cone_height).circle(13)
    .loft(combine=True)
)
tail_base = (
    cone.faces(">Z")
    .circle(tail_diameter / 2)
    .extrude(tail_base_height)
)
tail_shell = tail_base.faces("+Z").shell(-1)

rim = (
    cq.Workplane("YZ")
    .sketch()
    .polygon([
        (0, 0),
        (0, rim_height),
        (rim_width, rim_hang_height),
        (0, 0),
    ])
    .vertices(">X")
    .fillet(rim_hang_height)
    .finalize()
    .revolve(
        360, 
        (tail_inner_diameter / 2, 0, 0),
        (tail_inner_diameter / 2, 1, 0)
    )
    .translate((0, -tail_inner_diameter / 2, tail_height - rim_height))
)
tail_shell += rim

tail = tail_shell + (stabilizer - cone)

latch = (
    cq.Workplane("YZ" )
    .sketch()
    .push([cq.Location((0, -latch_height + latch_diameter / 2))])
    .circle(latch_diameter / 2)
    .push([cq.Location((0, -(latch_height - latch_diameter / 2) / 2))])
    .rect(1, latch_height - latch_diameter / 2)
    .clean()
    .reset()
    .vertices("<Y")
    .fillet(latch_diameter)
    .finalize()
    .extrude(tail_diameter / 2)
    .translate((0, 0, tail_height))
)


for i in range(3):
    tail = tail.cut(latch.rotate(*Z_VECTOR, i * 120))

show_object(tail)

model_name = "tail_plain.stl"
if feather_slice_angle > 0:
    model_name = "tail_curved.stl"
cq.exporters.export(tail, model_name)
