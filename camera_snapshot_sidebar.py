import bpy
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
        return context.active_object.type == 'CAMERA'

    def execute(self, context):
        return {'FINISHED'}
    
class CC_OT_next_snapshot(bpy.types.Operator):
    bl_idname = "view3d.next_snapshot"
    bl_label = "查看下一个快照"
    bl_description = "查看下一个快照"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'CAMERA'

    def execute(self, context):
        return {'FINISHED'}
    
class CC_OT_restore_snapshot(bpy.types.Operator):
    bl_idname = "view3d.restore_snapshot"
    bl_label = "保存快照"
    bl_description = "保存快照"
    bl_options = {'REGISTER', 'UNDO'}

    #@classmethod
    #def poll(cls, context):
    #    return context.active_object.type == 'CAMERA'

    def execute(self, context):
        if not variables.camcompo_statu:
            for i in range(26):
                image = f'SNAPSHOT_SAVE_{i}.png'
                t = 0.04 + i * 0.04
                bpy.app.timers.register(lambda image=image: snapshot_bar.draw_camera_snapshot(image), first_interval=t)

        else:
            for i in range(25):
                image = f'ICON_SNAP_{i+1}.png'
                t = 0.04 + i * 0.04
                bpy.app.timers.register(lambda image=image: snapshot_bar_invoke.draw_camera_snapshot_invoke(image), first_interval=t)
        
        #bpy.app.timers.register(lambda: icons_snapshot_statu.draw_camera_snapshot('SNAPSHOT_SAVE_0.png') , first_interval=1.0)
        #bpy.app.timers.register(lambda: icons_snapshot_statu.draw_camera_snapshot('SNAPSHOT_SAVE_1.png') , first_interval=2.0)
        #bpy.app.timers.register(lambda: icons_snapshot_statu.draw_camera_snapshot('SNAPSHOT_SAVE_2.png') , first_interval=3.0)
        #bpy.app.timers.register(lambda: icons_snapshot_statu.draw_camera_snapshot('SNAPSHOT_SAVE_3.png') , first_interval=4.0)
        #bpy.app.timers.register(lambda: icons_snapshot_statu.draw_camera_snapshot('SNAPSHOT_SAVE_4.png') , first_interval=5.0)



        return {'FINISHED'}