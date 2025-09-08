import bpy
from .background import draw_background
from .icons import draw_icon
from . import icons


class CI_OT_camera_it(bpy.types.Operator):
    bl_idname = "view3d.cam_it"
    bl_label = "快速设置摄像机"
    bl_description = "快速设置摄像机"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

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
        if event.type not in {'MOUSEMOVE','NUMPAD_5','ESC'}:
            return {'RUNNING_MODAL'}
        
        elif event.type == 'ESC':
            bpy.types.SpaceView3D.draw_handler_remove(self.handle_backgroud, 'WINDOW')

            # 清理残留图片纹理
            if icons.camera_statu:
                icons.camera_statu.cleanup()
                icons.camera_statu = None


            return {'FINISHED'}
            

        return {'PASS_THROUGH'}
