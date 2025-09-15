import bpy
from datetime import datetime
from . import snapshot_bar
from . import snapshot_bar_invoke
from . import variables

class CC_PT_snapshot_sidebar(bpy.types.Panel):
    bl_label = "构图快照"
    bl_idname = "cc.snapshot_sidebar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CamCompo"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("view3d.prev_snapshot", text="◀")
        row.operator("view3d.restore_snapshot", text="💾") #这里也可以使用文字
        row.operator("view3d.next_snapshot", text="▶")

class CC_OT_prev_snapshot(bpy.types.Operator):
    bl_idname = "view3d.prev_snapshot"
    bl_label = "上一个快照"
    bl_description = "查看上一个快照"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None

    def execute(self, context):
        return {'FINISHED'}
    
class CC_OT_next_snapshot(bpy.types.Operator):
    bl_idname = "view3d.next_snapshot"
    bl_label = "查看下一个快照"
    bl_description = "查看下一个快照"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None 

    def execute(self, context):
        return {'FINISHED'}
    
class CC_OT_restore_snapshot(bpy.types.Operator):
    bl_idname = "view3d.restore_snapshot"
    bl_label = "保存快照"
    bl_description = "保存快照"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None and can_snapshot()

    def execute(self, context):
        bpy.context.scene.camera.camera_snapshots.add()

        snapshot_name ='snapshot_' + datetime.now().strftime("%m%d%H%M%S")

        bpy.context.scene.camera.camera_snapshots[-1].name = snapshot_name
        bpy.context.scene.camera.camera_snapshots[-1].lens = bpy.context.scene.camera.data.lens
        bpy.context.scene.camera.camera_snapshots[-1].focus_distance = bpy.context.scene.camera.data.dof.focus_distance
        bpy.context.scene.camera.camera_snapshots[-1].aperture_fstop = bpy.context.scene.camera.data.dof.aperture_fstop

        bpy.context.scene.camera.camera_snapshots[-1].matrix_world = [bpy.context.scene.camera.matrix_world[i][j] for j in range(4) for i in range(4)]
        #bpy.context.scene.camera.camera_snapshots[-1].matrix_world = bpy.context.scene.camera.matrix_world

        if not variables.camcompo_statu:
            for i in range(25):
                image = f'SNAPSHOT_SAVE_{i}.png'
                t = 0.04 + i * 0.04
                bpy.app.timers.register(lambda image=image: snapshot_bar.draw_camera_snapshot(image), first_interval=t)
                
            bpy.app.timers.register(
                lambda: (
                    snapshot_bar.camera_snapshot_state.cleanup(),
                    setattr(snapshot_bar, "camera_snapshot_state", None),
                    None
                    )[-1],
                first_interval=0.04 * 35
                )

        else:
            for i in range(24):
                image = f'ICON_SNAP_{i+1}.png'
                t = 0.04 + i * 0.04
                bpy.app.timers.register(lambda image=image: snapshot_bar_invoke.draw_camera_snapshot_invoke(image), first_interval=t)

            bpy.app.timers.register(
                lambda:(
                    snapshot_bar_invoke.camera_snapshot_state_invoke.cleanup(),
                    setattr(snapshot_bar_invoke, "camera_snapshot_state_invoke", None),
                    None
                    )[-1],
                first_interval=0.04 * 34
                )

        return {'FINISHED'}
    
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

        current_snap = str(round(camera.data.lens, 2)) + str(round(camera.data.dof.focus_distance, 3)) + str(round(camera.data.dof.aperture_fstop, 2)) + ''.join(str(round(v, 4)) for row in camera.matrix_world for v in row)

        if current_snap not in snap_set:
            return True


    return False
                
