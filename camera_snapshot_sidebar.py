import bpy,os
from datetime import datetime
from . import snapshot_bar
from . import snapshot_bar_invoke
from . import variables
from . import snapshot_detect
from .icons_snap_unsnap import draw_snap_unsnap
from .camera_info import draw_camera_info

class CC_UL_camera_snapshots(bpy.types.UIList):    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name, icon='BOOKMARKS')

class CC_PT_snapshot_sidebar(bpy.types.Panel):
    bl_label = "构图快照"
    bl_idname = "cc.snapshot_sidebar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CamCompo"

    def draw(self, context):
        camera = context.scene.camera
        if camera is None or context.mode != 'OBJECT':
            return
        
        panel = self.layout

        row2 = panel.row(align=True)
        col1 = row2.column(align=True)

        col1.template_list(
            "CC_UL_camera_snapshots",    # 自定义 UIList
            "",
            camera,                          # 数据源对象
            "camera_snapshots",           # CollectionProperty 名
            camera,                          # active object
            "camera_snapshots_index",     # 活动索引属性
            rows=8,                        # 显示行数
            sort_reverse=True,
            sort_lock=True,
        )

        if camera.camera_snapshots:
            index = camera.camera_snapshots_index
            snapshot = camera.camera_snapshots[index]
            col1.prop(snapshot, "name", text="",icon='GREASEPENCIL')

        row2.separator()

        col2 = row2.column(align=True)
        col2.operator("view3d.restore_snapshot", text="", icon="ADD")
        col2.operator("view3d.remove_snapshot", text="", icon="REMOVE")
        col2.separator()
        col2.operator("view3d.prev_snapshot", text="", icon="TRIA_UP")
        col2.operator("view3d.next_snapshot", text="", icon="TRIA_DOWN")
        col2.separator()
        col2.operator("view3d.cam_compo_invoke", text="", icon="CON_CAMERASOLVER")

class CC_UL_camera_items(bpy.types.UIList):    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.camera_item.name, icon='BOOKMARKS')

class CC_PT_cam_switch_sidebar(bpy.types.Panel):
    bl_label = "相机切换"
    bl_idname = "cc.cam_switch_sidebar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CamCompo"

    def draw(self, context):
        scene = context.scene
        if len(scene.camera_items) == 0 or context.mode != 'OBJECT':
            return
        
        panel = self.layout

        row2 = panel.row(align=True)
        col1 = row2.column()

        col1.template_list(
            "CC_UL_camera_items",    # 自定义 UIList
            "",
            scene,                          # 数据源对象
            "camera_items",           # CollectionProperty 名
            scene,                          # active object
            "camera_items_index",     # 活动索引属性
            rows=8,                        # 显示行数
            sort_reverse=True,
            sort_lock=True,
        )

        if scene.camera_items:
            index = scene.camera_items_index
            cameraitem = scene.camera_items[index]
            col1.prop(cameraitem.camera_item, "name", text="",icon='GREASEPENCIL')

        row2.separator()

        col2 = row2.column(align=True)
        col2.operator("object.camera_add", text="", icon="ADD")
        col2.operator("view3d.remove_snapshot", text="", icon="REMOVE")
        col2.separator()
        col2.operator("view3d.prev_snapshot", text="", icon="TRIA_UP")
        col2.operator("view3d.next_snapshot", text="", icon="TRIA_DOWN")
        col2.separator()
        col2.operator("view3d.cam_compo_invoke", text="", icon="CON_CAMERASOLVER")









class CC_OT_prev_snapshot(bpy.types.Operator):
    bl_idname = "view3d.prev_snapshot"
    bl_label = "跳到上一个快照"
    bl_description = "跳到上一个快照"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.camera.camera_snapshots) > 0 and context.scene.camera.camera_snapshots_index < len(context.scene.camera.camera_snapshots) - 1 

    def execute(self, context):
        context.scene.camera.camera_snapshots_index += 1
        bpy.ops.view3d.goto_snapshot()
        return {'FINISHED'}
    
class CC_OT_next_snapshot(bpy.types.Operator):
    bl_idname = "view3d.next_snapshot"
    bl_label = "跳到下一个快照"
    bl_description = "跳到下一个快照"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.camera.camera_snapshots) > 0 and context.scene.camera.camera_snapshots_index > 0

    def execute(self, context):
        context.scene.camera.camera_snapshots_index -= 1
        bpy.ops.view3d.goto_snapshot()
        return {'FINISHED'}

    
class CC_OT_restore_snapshot(bpy.types.Operator):
    bl_idname = "view3d.restore_snapshot"
    bl_label = "保存快照"
    bl_description = "保存快照"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None and snapshot_detect.can_snapshot()

    def execute(self, context):
        bpy.context.scene.camera.camera_snapshots.add()

        snapshot_name ='snapshot_' + datetime.now().strftime("%m%d%H%M%S")

        bpy.context.scene.camera.camera_snapshots[-1].name = snapshot_name
        bpy.context.scene.camera.camera_snapshots[-1].lens = bpy.context.scene.camera.data.lens
        bpy.context.scene.camera.camera_snapshots[-1].focus_distance = bpy.context.scene.camera.data.dof.focus_distance
        bpy.context.scene.camera.camera_snapshots[-1].aperture_fstop = bpy.context.scene.camera.data.dof.aperture_fstop

        bpy.context.scene.camera.camera_snapshots[-1].matrix_world = [bpy.context.scene.camera.matrix_world[i][j] for j in range(4) for i in range(4)]

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
                t = 0.08 + i * 0.08
                bpy.app.timers.register(lambda image=image: snapshot_bar_invoke.draw_camera_snapshot_invoke(image), first_interval=t)

            bpy.app.timers.register(
                lambda:(
                    snapshot_bar_invoke.camera_snapshot_state_invoke.cleanup(),
                    setattr(snapshot_bar_invoke, "camera_snapshot_state_invoke", None),
                    None
                    )[-1],
                first_interval=0.08 * 34
                )

            bpy.app.timers.register(draw_snap_unsnap, first_interval=0.08 * 25 )
        
        context.scene.camera.camera_snapshots_index = len(context.scene.camera.camera_snapshots) - 1
        return {'FINISHED'}
    
class CC_OT_remove_snapshot(bpy.types.Operator):
    bl_idname = "view3d.remove_snapshot"
    bl_label = "删除快照"
    bl_description = "删除选中快照"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.camera.camera_snapshots) > 0

    def execute(self, context):
        camera = context.scene.camera
        index = camera.camera_snapshots_index

        camera.camera_snapshots.remove(index)

        if camera.camera_snapshots_index > 0:
            camera.camera_snapshots_index -= 1

        if variables.camcompo_statu:
            draw_camera_info()
            draw_snap_unsnap()
        return {'FINISHED'}
    
class CC_OT_goto_snapshot(bpy.types.Operator):
    bl_idname = "view3d.goto_snapshot"
    bl_label = "跳到快照"
    bl_description = "跳到选中快照"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.scene.camera.camera_snapshots) > 0

    def execute(self, context):
        camera = context.scene.camera
        index = camera.camera_snapshots_index

        context.scene.camera.data.lens = camera.camera_snapshots[index].lens
        context.scene.camera.data.dof.focus_distance = camera.camera_snapshots[index].focus_distance
        context.scene.camera.data.dof.aperture_fstop = camera.camera_snapshots[index].aperture_fstop
        context.scene.camera.matrix_world = camera.camera_snapshots[index].matrix_world

        if variables.camcompo_statu:
            variables.camera_lens = variables.camera_object.data.lens
            variables.camera_distance = variables.camera_object.data.dof.focus_distance
            variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop
            draw_camera_info()
            draw_snap_unsnap()

        return {'FINISHED'}


def click_index_action(self, context):
    variables.prev_click_time = variables.last_click_time
    now = datetime.now()
    variables.last_click_time = now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1_000_000
    bpy.app.timers.register(goto_snapshot, first_interval=0.51)


def goto_snapshot():
    if variables.last_click_time - variables.prev_click_time < 0.5:
        bpy.ops.view3d.goto_snapshot()        

# 判定是不是处于相机视图
def is_camera_view():
    for area in bpy.context.screen.areas:
        if area.type != 'VIEW_3D':
            continue
        for space in area.spaces:
            if space.type != 'VIEW_3D':
                continue
            if space.region_3d.view_perspective == 'CAMERA':
                return True
    return False
    
#更新当前场景相机列表
def update_camera_list():
    scene = bpy.context.scene
    scene.camera_items.clear()
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            new_camera = scene.camera_items.add()
            new_camera.camera_item = obj

