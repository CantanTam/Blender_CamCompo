import bpy

def can_snapshot():
    camera = bpy.context.scene.camera
    snap_list = bpy.context.scene.camera.camera_snapshots

    if len(snap_list) == 0:
        return True
    else:
        snap_set = {
            str(round(snap.lens, 2))
            + str(round(snap.focus_distance, 3))
            + str(round(snap.aperture_fstop, 2))
            + ''.join(str(round(v, 4)) for row in snap.matrix_world for v in row)
            for snap in snap_list
        }

        current_snap = (
            str(round(camera.data.lens, 2)) + 
            str(round(camera.data.dof.focus_distance, 3)) + 
            str(round(camera.data.dof.aperture_fstop, 2)) + 
            ''.join(str(round(v, 4)) for row in camera.matrix_world for v in row)
        )
        
        if current_snap not in snap_set:
            return True


    return False