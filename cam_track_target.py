import bpy
from . import variables

def track_to_target():
    if variables.num_period:
        new_track = variables.camera_object.constraints.new(type = 'TRACK_TO')
        new_track.target = variables.target_object
        new_track.track_axis = 'TRACK_NEGATIVE_Z'
        new_track.up_axis = 'UP_Y'
        new_track.name = 'CAM_TO_TARGET'

        bpy.ops.object.select_all(action='DESELECT')
        variables.camera_object.select_set(True)
        bpy.context.view_layer.objects.active = variables.camera_object

        bpy.ops.constraint.apply(constraint=new_track.name, owner='OBJECT', report=False)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None
