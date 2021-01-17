import bpy

chosen_drone = "drone_1"
sce = bpy.context.scene

drone = bpy.data.objects['drone_1']
drone_mesh = drone.data
print(drone.location)
ob = drone
res = {}
for f in ob.animation_data.action.fcurves:
    for k in f.keyframe_points:
        fr = k.co[0]
        bpy.context.scene.frame_set(fr)
        pos = ob.location
        res[int(fr)] = {"strength": ob.active_material.node_tree.nodes["Emission"].inputs[1].default_value,
                        "pos": tuple(pos)}
print(res)
res = {0.0: {'strength': 0.0, 'pos': (23.893774032592773, 2.9044179916381836, 31.161624908447266)},
       453.0: {'strength': 10.0, 'pos': (11.936285018920898, -9.566575050354004, 16.887611389160156)},
       634.0: {'strength': 10.0, 'pos': (11.936285018920898, -9.566575050354004, 21.581567764282227)}}
