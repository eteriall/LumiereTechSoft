import json
import sys
import time

import bpy
from tests import send_socket_message

chosen_drone = "drone_10"
sce = bpy.context.scene

drone = bpy.data.objects[chosen_drone]
drone_mesh = drone.data
print(drone.location)
ob = drone
res = {}
print(ob.active_material, ob.active_material.name, ob.active_material.animation_data)
for f in ob.animation_data.action.fcurves:
    for k in f.keyframe_points:
        fr = k.co[0]
        bpy.context.scene.frame_set(fr)
        print(fr)
        pos = ob.location
        res[int(fr)] = {"strength": ob.active_material.node_tree.nodes["Emission"].inputs[1].default_value,
                        "pos": tuple(pos)}

