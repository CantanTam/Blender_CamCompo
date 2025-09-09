import bpy,math
from mathutils import Vector
from .background import draw_background
from .icons import draw_icon
from . import icons
from . import variables

class CI_OT_camera_it_invoke(bpy.types.Operator):
    bl_idname = "view3d.cam_it_invoke"
    bl_label = "快速设置摄像机"
    bl_description = "快速设置摄像机"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(bpy.context.selected_objects) > 1 and bpy.context.active_object.type == 'CAMERA' and bpy.context.mode == 'OBJECT'

    def execute(self, context):
        variables.camera_object = context.active_object

        bpy.context.scene.camera = context.active_object

        for i in bpy.context.selected_objects:
            variables.target_location = variables.target_location + i.matrix_world.translation

        variables.target_location = variables.target_location - bpy.context.active_object.matrix_world.translation
        variables.target_location = variables.target_location / (len(bpy.context.selected_objects) - 1)

        bpy.ops.object.empty_add(type='SPHERE', radius=1.0, align='WORLD', location=variables.target_location)

        variables.target_object = context.active_object
        variables.target_object.name = variables.camera_object.name + "_TARGET"

        bpy.ops.mesh.primitive_cube_add(size=2.0, align='WORLD', location=variables.target_location)

        bpy.ops.view3d.camera_to_view_selected()

        bpy.data.objects.remove(bpy.context.active_object, do_unlink=True)

        bpy.ops.object.select_all(action='DESELECT')
        variables.camera_object.select_set(True)
        bpy.context.view_layer.objects.active = variables.camera_object

        variables.camera_object.rotation_euler[0] = math.radians(90)
        variables.camera_object.rotation_euler[1] = math.radians(0)

        move_z = variables.target_object.matrix_world.translation.z - variables.camera_object.matrix_world.translation.z
        variables.camera_object.location.z += move_z

        variables.camera_object.parent = variables.target_object

        #最后去除注释
        #bpy.ops.view3d.view_camera('INVOKE_DEFAULT')

        bpy.ops.view3d.cam_it('INVOKE_DEFAULT')
        return {'FINISHED'}


class CI_OT_camera_it(bpy.types.Operator):
    bl_idname = "view3d.cam_it"
    bl_label = "快速设置摄像机"
    bl_description = "快速设置摄像机"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        
        self.handle_backgroud = bpy.types.SpaceView3D.draw_handler_add(draw_background, (self,context), 'WINDOW', 'POST_PIXEL')
        draw_icon()

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type =='NUMPAD_5' and event.value == 'PRESS':
            icons.num_five = not icons.num_five
            draw_icon()
            return {'RUNNING_MODAL'}
        
        
        # 鼠标移动直接 回到 modal
        if event.type not in {'MOUSEMOVE','NUMPAD_5','ESC','NUMPAD_0'}:
            return {'RUNNING_MODAL'}
        
        elif event.type == 'ESC':
            #bpy.data.objects.remove(variables.target_object, do_unlink=True)
            bpy.types.SpaceView3D.draw_handler_remove(self.handle_backgroud, 'WINDOW')

            # 最后去除注释
            #bpy.ops.view3d.view_camera('INVOKE_DEFAULT')

            # 每次退出需要清零 matrix_world
            variables.target_location = Vector((0.0, 0.0, 0.0))
            variables.camera_location = Vector((0.0, 0.0, 0.0))
            variables.target_object = None
            variables.camera_object = None


            # 清理残留图片纹理
            if icons.camera_statu:
                icons.camera_statu.cleanup()
                icons.camera_statu = None


            return {'FINISHED'}
            

        return {'PASS_THROUGH'}
