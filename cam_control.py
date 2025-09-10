import bpy,math
from mathutils import Vector
from .background import draw_background
from .icons_move_rotate import draw_move_rotate
from . import icons_move_rotate
from .icons_lens_dist_aper import draw_lens_dist_aper
from . import icons_lens_dist_aper
from .icons_unlock_lock import draw_unlock_lock
from . import icons_unlock_lock

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
        variables.camera_lens = context.active_object.data.lens
        variables.camera_distance = context.active_object.data.dof.focus_distance
        variables.camera_aperture = context.active_object.data.dof.aperture_fstop

        context.active_object.data.dof.use_dof = True

        bpy.context.scene.camera = context.active_object

        for i in bpy.context.selected_objects:
            variables.target_location = variables.target_location + i.matrix_world.translation

        variables.target_location = variables.target_location - bpy.context.active_object.matrix_world.translation
        variables.target_location = variables.target_location / (len(bpy.context.selected_objects) - 1)

        bpy.ops.object.empty_add(type='SPHERE', radius=1.0, align='WORLD', location=variables.target_location)

        variables.target_object = context.active_object
        variables.target_object.name = variables.camera_object.name + "_TARGET"

        bpy.ops.mesh.primitive_cube_add(size=2.0, align='WORLD', location=variables.target_location)

        #variables.refer_object = context.active_object

        #需要完全新建完mesh之后才能对准
        bpy.app.timers.register(lambda: (bpy.ops.view3d.camera_to_view_selected('INVOKE_DEFAULT'), None)[1], first_interval=0.01)

        bpy.app.timers.register(lambda: (bpy.data.objects.remove(bpy.context.active_object, do_unlink=True), None)[1], first_interval=0.01)

        #bpy.ops.object.select_all(action='DESELECT')
        #variables.camera_object.select_set(True)
        #bpy.context.view_layer.objects.active = variables.camera_object

        variables.camera_object.rotation_euler[0] = math.radians(90)
        variables.camera_object.rotation_euler[1] = math.radians(0)
        variables.camera_object.rotation_euler[2] = math.radians(90)

        move_z = variables.target_object.matrix_world.translation.z - variables.camera_object.matrix_world.translation.z
        variables.camera_object.location.z += move_z

        cam_target_x = variables.camera_object.matrix_world.translation.x - variables.target_object.matrix_world.translation.x
        cam_target_y = variables.camera_object.matrix_world.translation.y - variables.target_object.matrix_world.translation.y

        variables.cam_target_distance = round(math.hypot(cam_target_x, cam_target_y), 3)
        variables.cam_target_distance_factor = variables.cam_target_distance * 0.01

        variables.camera_object.parent = variables.target_object

        #最后去除注释
        bpy.ops.view3d.view_camera('INVOKE_DEFAULT')

        bpy.ops.view3d.cam_it('INVOKE_DEFAULT')
        return {'FINISHED'}


class CI_OT_camera_it(bpy.types.Operator):
    bl_idname = "view3d.cam_it"
    bl_label = "快速设置摄像机"
    bl_description = "快速设置摄像机"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        
        self.handle_backgroud = bpy.types.SpaceView3D.draw_handler_add(draw_background, (self,context), 'WINDOW', 'POST_PIXEL')
        draw_move_rotate()
        draw_lens_dist_aper()
        draw_unlock_lock()

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type =='NUMPAD_5':
            if event.value == 'RELEASE':
                variables.num_five = not variables.num_five
            draw_move_rotate()
            return {'RUNNING_MODAL'}
        
        elif event.type =='NUMPAD_PERIOD':
            if event.value == 'RELEASE':
                variables.num_period = not variables.num_period
            draw_unlock_lock()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_0':
            if event.value == 'RELEASE':
                variables.num_zero = (variables.num_zero + 1) % 3
            draw_lens_dist_aper()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_SLASH':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += variables.camera_object.matrix_basis.to_quaternion() @ Vector((0, 0, -1 * variables.cam_target_distance_factor))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += variables.camera_object.matrix_basis.to_quaternion() @ Vector((0, 0, -10 * variables.cam_target_distance_factor))
            return {'RUNNING_MODAL'}
        

        elif event.type == 'NUMPAD_ASTERIX':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += variables.camera_object.matrix_basis.to_quaternion() @ Vector((0, 0, variables.cam_target_distance_factor))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += variables.camera_object.matrix_basis.to_quaternion() @ Vector((0, 0, 10 * variables.cam_target_distance_factor))
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_8':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, 0.1 * variables.cam_target_distance_factor))
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(-1))
            elif event.value == 'RELEASE' and event.ctrl:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, variables.cam_target_distance_factor))
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(-10))
            return {'RUNNING_MODAL'}
        
        
        elif event.type == 'NUMPAD_2':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, -0.1 * variables.cam_target_distance_factor))
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(1))
            elif event.value == 'RELEASE' and event.ctrl:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, -variables.cam_target_distance_factor))
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(10))
            return {'RUNNING_MODAL'}


        elif event.type == 'NUMPAD_6':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.target_object.rotation_euler.z += math.radians(1)
            elif event.value == 'RELEASE' and event.ctrl:
                variables.target_object.rotation_euler.z += math.radians(10)
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_4':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.target_object.rotation_euler.z += math.radians(-1)
            elif event.value == 'RELEASE' and event.ctrl:
                variables.target_object.rotation_euler.z += math.radians(-10)
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_7':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(-1))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(-10))
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_9':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(1))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(10))
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_1':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((-variables.cam_target_distance_factor, 0, 0)))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((-5 * variables.cam_target_distance_factor, 0, 0)))
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_3':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((variables.cam_target_distance_factor, 0, 0)))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((5 * variables.cam_target_distance_factor, 0, 0)))
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_PLUS':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                if variables.num_zero == 0:
                    if variables.camera_lens <= 135:
                        variables.camera_object.data.lens = variables.camera_lens + 1
                    elif variables.camera_lens <= 200:
                        variables.camera_object.data.lens = variables.camera_lens + 5
                    elif variables.camera_lens < 1200:
                        variables.camera_object.data.lens = variables.camera_lens + 10
                    elif variables.camera_lens >= 1200:
                        pass

                    variables.camera_lens = variables.camera_object.data.lens

                elif variables.num_zero == 1:
                    variables.camera_object.data.dof.focus_distance = variables.camera_distance + 1
                    variables.camera_distance = variables.camera_object.data.dof.focus_distance

                elif variables.num_zero == 2:
                    variables.camera_object.data.dof.aperture_fstop = variables.camera_aperture + 1
                    variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop
            
            elif event.value == 'RELEASE' and event.alt:
                if variables.num_zero == 0:
                    if variables.camera_lens < 1200:
                        variables.camera_object.data.lens = variables.camera_lens + 1

                    variables.camera_lens = variables.camera_object.data.lens

                elif variables.num_zero == 1:
                    variables.camera_object.data.dof.focus_distance = variables.camera_distance + 0.1
                    variables.camera_distance = variables.camera_object.data.dof.focus_distance

                elif variables.num_zero == 2:
                    variables.camera_object.data.dof.aperture_fstop = variables.camera_aperture + 0.1
                    variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop

            elif event.value == 'RELEASE' and event.ctrl:
                if variables.num_zero == 0:
                    if variables.camera_lens < 12:
                        variables.camera_object.data.lens = variables.camera_lens + 1
                    elif variables.camera_lens < 14:
                        variables.camera_object.data.lens = 14
                    elif variables.camera_lens < 16:
                        variables.camera_object.data.lens = 16
                    elif variables.camera_lens < 18:
                        variables.camera_object.data.lens = 18
                    elif variables.camera_lens < 20:
                        variables.camera_object.data.lens = 20
                    elif variables.camera_lens < 21:
                        variables.camera_object.data.lens = 21
                    elif variables.camera_lens < 24:  
                        variables.camera_object.data.lens = 24
                    elif variables.camera_lens < 28:
                        variables.camera_object.data.lens = 28
                    elif variables.camera_lens < 30:
                        variables.camera_object.data.lens = 30
                    elif variables.camera_lens < 35:
                        variables.camera_object.data.lens = 35
                    elif variables.camera_lens < 40:
                        variables.camera_object.data.lens = 40
                    elif variables.camera_lens < 45:
                        variables.camera_object.data.lens = 45
                    elif variables.camera_lens < 50:
                        variables.camera_object.data.lens = 50
                    elif variables.camera_lens < 55:
                        variables.camera_object.data.lens = 55
                    elif variables.camera_lens < 58:
                        variables.camera_object.data.lens = 58
                    elif variables.camera_lens < 70: 
                        variables.camera_object.data.lens = 70
                    elif variables.camera_lens < 75:
                        variables.camera_object.data.lens = 75
                    elif variables.camera_lens < 80:
                        variables.camera_object.data.lens = 80
                    elif variables.camera_lens < 85:
                        variables.camera_object.data.lens = 85
                    elif variables.camera_lens < 90:
                        variables.camera_object.data.lens = 90
                    elif variables.camera_lens < 100:
                        variables.camera_object.data.lens = 100
                    elif variables.camera_lens < 105:
                        variables.camera_object.data.lens = 105
                    elif variables.camera_lens < 135:
                        variables.camera_object.data.lens = 135
                    elif variables.camera_lens < 150:  # 添加了150mm
                        variables.camera_object.data.lens = 150
                    elif variables.camera_lens < 180:
                        variables.camera_object.data.lens = 180
                    elif variables.camera_lens < 200:
                        variables.camera_object.data.lens = 200
                    elif variables.camera_lens < 300:
                        variables.camera_object.data.lens = 300
                    elif variables.camera_lens < 400:
                        variables.camera_object.data.lens = 400
                    elif variables.camera_lens < 500:
                        variables.camera_object.data.lens = 500
                    elif variables.camera_lens < 600:
                        variables.camera_object.data.lens = 600
                    elif variables.camera_lens < 800:
                        variables.camera_object.data.lens = 800
                    elif variables.camera_lens < 1200:
                        variables.camera_object.data.lens = 1200
                    
                    variables.camera_lens = variables.camera_object.data.lens

                elif variables.num_zero == 1:
                    variables.camera_object.data.dof.focus_distance = variables.camera_distance + 10
                    variables.camera_distance = variables.camera_object.data.dof.focus_distance

                elif variables.num_zero == 2:
                    variables.camera_object.data.dof.aperture_fstop = variables.camera_aperture + 5
                    variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop

            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_MINUS':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                if variables.num_zero == 0:
                    if variables.camera_lens > 200 and variables.camera_lens <= 1200:
                        variables.camera_object.data.lens = variables.camera_lens - 10
                    elif variables.camera_lens > 135 and variables.camera_lens <= 200:
                        variables.camera_object.data.lens = variables.camera_lens - 5
                    elif variables.camera_lens > 0 and variables.camera_lens <= 135:
                        variables.camera_object.data.lens = variables.camera_lens - 1
                    # lens <= 0 不做处理
                    variables.camera_lens = variables.camera_object.data.lens

                elif variables.num_zero == 1:
                    variables.camera_object.data.dof.focus_distance = variables.camera_distance - 1
                    variables.camera_distance = variables.camera_object.data.dof.focus_distance

                elif variables.num_zero == 2:
                    variables.camera_object.data.dof.aperture_fstop = variables.camera_aperture - 1
                    variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop

            elif event.value == 'RELEASE' and event.alt:
                if variables.num_zero == 0:
                    if variables.camera_lens > 0:
                        variables.camera_object.data.lens = variables.camera_lens - 1
                        variables.camera_lens = variables.camera_object.data.lens

                elif variables.num_zero == 1:
                    variables.camera_object.data.dof.focus_distance = variables.camera_distance - 0.1
                    variables.camera_distance = variables.camera_object.data.dof.focus_distance

                elif variables.num_zero == 2:
                    variables.camera_object.data.dof.aperture_fstop = variables.camera_aperture - 0.1
                    variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop

            elif event.value == 'RELEASE' and event.ctrl:
                if variables.num_five == 0:
                    if variables.camera_lens > 1200:
                        variables.camera_object.data.lens = 1200
                    elif variables.camera_lens > 800:
                        variables.camera_object.data.lens = 800
                    elif variables.camera_lens > 600:
                        variables.camera_object.data.lens = 600
                    elif variables.camera_lens > 500:
                        variables.camera_object.data.lens = 500
                    elif variables.camera_lens > 400:
                        variables.camera_object.data.lens = 400
                    elif variables.camera_lens > 300:
                        variables.camera_object.data.lens = 300
                    elif variables.camera_lens > 200:
                        variables.camera_object.data.lens = 200
                    elif variables.camera_lens > 180:
                        variables.camera_object.data.lens = 180
                    elif variables.camera_lens > 150:
                        variables.camera_object.data.lens = 150
                    elif variables.camera_lens > 135:
                        variables.camera_object.data.lens = 135
                    elif variables.camera_lens > 105:
                        variables.camera_object.data.lens = 105
                    elif variables.camera_lens > 100:
                        variables.camera_object.data.lens = 100
                    elif variables.camera_lens > 90:
                        variables.camera_object.data.lens = 90
                    elif variables.camera_lens > 85:
                        variables.camera_object.data.lens = 85
                    elif variables.camera_lens > 80:
                        variables.camera_object.data.lens = 80
                    elif variables.camera_lens > 75:
                        variables.camera_object.data.lens = 75
                    elif variables.camera_lens > 70:
                        variables.camera_object.data.lens = 70
                    elif variables.camera_lens > 58:
                        variables.camera_object.data.lens = 58
                    elif variables.camera_lens > 55:
                        variables.camera_object.data.lens = 55
                    elif variables.camera_lens > 50:
                        variables.camera_object.data.lens = 50
                    elif variables.camera_lens > 45:
                        variables.camera_object.data.lens = 45
                    elif variables.camera_lens > 40:
                        variables.camera_object.data.lens = 40
                    elif variables.camera_lens > 35:
                        variables.camera_object.data.lens = 35
                    elif variables.camera_lens > 30:
                        variables.camera_object.data.lens = 30
                    elif variables.camera_lens > 28:
                        variables.camera_object.data.lens = 28
                    elif variables.camera_lens > 24:
                        variables.camera_object.data.lens = 24
                    elif variables.camera_lens > 21:
                        variables.camera_object.data.lens = 21
                    elif variables.camera_lens > 20:
                        variables.camera_object.data.lens = 20
                    elif variables.camera_lens > 18:
                        variables.camera_object.data.lens = 18
                    elif variables.camera_lens > 16:
                        variables.camera_object.data.lens = 16
                    elif variables.camera_lens > 14:
                        variables.camera_object.data.lens = 14
                    elif variables.camera_lens > 12:
                        variables.camera_object.data.lens = 12
                    elif variables.camera_lens > 1:
                        variables.camera_object.data.lens = variables.camera_lens - 1

                    variables.camera_lens = variables.camera_object.data.lens

                elif variables.num_zero == 1:
                    variables.camera_object.data.dof.focus_distance = variables.camera_distance - 10
                    variables.camera_distance = variables.camera_object.data.dof.focus_distance

                elif variables.num_zero == 2:
                    variables.camera_object.data.dof.aperture_fstop = variables.camera_aperture - 5
                    variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop

            return {'RUNNING_MODAL'}
        
        # 鼠标移动直接 回到 modal
        elif event.type not in {'MOUSEMOVE','NUMPAD_5','ESC','NUMPAD_0','WHEELUPMOUSE','WHEELDOWNMOUSE','HOME'}:
            return {'RUNNING_MODAL'}
                
        elif event.type == 'ESC':
            #bpy.data.objects.remove(variables.target_object, do_unlink=True)
            bpy.types.SpaceView3D.draw_handler_remove(self.handle_backgroud, 'WINDOW')

            # 最后去除注释
            bpy.ops.view3d.view_camera('INVOKE_DEFAULT')

            # 每次退出需要清零 matrix_world
            variables.target_location = Vector((0.0, 0.0, 0.0))
            variables.camera_location = Vector((0.0, 0.0, 0.0))
            variables.cam_target_distance = 0
            variables.cam_target_distance_factor = 0
            variables.target_object = None
            variables.camera_object = None


            # 清理残留图片纹理
            if icons_move_rotate.move_rotate_statu:
                icons_move_rotate.move_rotate_statu.cleanup()
                icons_move_rotate.move_rotate_statu = None

            if icons_lens_dist_aper.lens_dist_aper_statu:
                icons_lens_dist_aper.lens_dist_aper_statu.cleanup()
                icons_lens_dist_aper.lens_dist_aper_statu = None

            if icons_unlock_lock.unlock_lock_statu:
                icons_unlock_lock.unlock_lock_statu.cleanup()
                icons_unlock_lock.unlock_lock_statu = None


            return {'FINISHED'}
            

        return {'PASS_THROUGH'}
