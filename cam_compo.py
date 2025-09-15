import bpy,math
from mathutils import Vector,Matrix
from . import variables

from .background import draw_background
from .icons_move_rotate import draw_move_rotate
from . import icons_move_rotate
from .icons_lens_dist_aper import draw_lens_dist_aper
from . import icons_lens_dist_aper
from .icons_unlock_lock import draw_unlock_lock
from . import icons_unlock_lock
from .camera_info import draw_camera_info
from . import camera_info
from .icons_snap_unsnap import draw_snap_unsnap
from . import icons_snap_unsnap
from .icons_snap_unsnap import draw_snap_unsnap

from .cam_track_target import track_to_target

from . import snapshot_detect


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

class CC_OT_cam_compo_invoke(bpy.types.Operator):
    bl_idname = "view3d.cam_compo_invoke"
    bl_label = "快速设置摄像机"
    bl_description = "快速设置摄像机"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object.type == 'CAMERA' and bpy.context.mode == 'OBJECT' and not is_camera_view()

    def execute(self, context):
        variables.camera_object = context.active_object
        variables.camera_lens = context.active_object.data.lens
        variables.camera_distance = context.active_object.data.dof.focus_distance
        variables.camera_aperture = context.active_object.data.dof.aperture_fstop

        context.active_object.data.dof.use_dof = True

        bpy.context.scene.camera = context.active_object

        variables.camcompo_statu = True

        if len(context.selected_objects) == 1:
            variables.single_camera = True
        else:
            variables.single_camera = False

        if not variables.single_camera:

            objs = [obj for obj in bpy.context.selected_objects if obj != bpy.context.active_object]

            min_corner = Vector((float('inf'), float('inf'), float('inf')))
            max_corner = Vector((float('-inf'), float('-inf'), float('-inf')))

            for obj in objs:
                for corner in obj.bound_box:
                    world_corner = obj.matrix_world @ Vector(corner)
                    min_corner.x = min(min_corner.x, world_corner.x)
                    min_corner.y = min(min_corner.y, world_corner.y)
                    min_corner.z = min(min_corner.z, world_corner.z)
                    max_corner.x = max(max_corner.x, world_corner.x)
                    max_corner.y = max(max_corner.y, world_corner.y)
                    max_corner.z = max(max_corner.z, world_corner.z)

            variables.target_location = (min_corner + max_corner) / 2

            # 取最大长度
            variables.target_object_size = max((max_corner.x - min_corner.x), (max_corner.y - min_corner.y), (max_corner.z - min_corner.z))

            bpy.ops.object.empty_add(type='SPHERE', radius=1.0, align='WORLD', location=variables.target_location)

            variables.target_object = context.active_object
            variables.target_object.name = variables.camera_object.name + "_TARGET"

            bpy.ops.mesh.primitive_cube_add(size=variables.target_object_size, align='WORLD', location=variables.target_location)

            variables.camera_object.rotation_euler[0] = math.radians(90)
            variables.camera_object.rotation_euler[1] = math.radians(0)
            variables.camera_object.rotation_euler[2] = math.radians(0)

            #需要完全新建完mesh之后才能对准
            bpy.app.timers.register(lambda: (bpy.ops.view3d.camera_to_view_selected('INVOKE_DEFAULT'), None)[1], first_interval=0.01)

            bpy.app.timers.register(lambda: (bpy.data.objects.remove(bpy.context.active_object, do_unlink=True), None)[1], first_interval=0.01)

            variables.cam_target_distance = round((variables.camera_object.location - variables.target_object.location).length, 3)

            variables.cam_target_distance_factor = variables.cam_target_distance * 0.01

            variables.camera_object.parent = variables.target_object

            #最后去除注释
            bpy.ops.view3d.view_camera('INVOKE_DEFAULT')

            bpy.ops.view3d.cam_compo_multi('INVOKE_DEFAULT')

        else:
            bpy.ops.view3d.view_camera('INVOKE_DEFAULT')

            bpy.ops.view3d.cam_compo_single('INVOKE_DEFAULT')
        
        return {'FINISHED'}


class CC_OT_cam_compo_multi(bpy.types.Operator):
    bl_idname = "view3d.cam_compo_multi"
    bl_label = "有参照物设置摄像机"
    bl_description = "有参照物设置摄像机"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        
        self.handle_backgroud = bpy.types.SpaceView3D.draw_handler_add(draw_background, (self,context), 'WINDOW', 'POST_PIXEL')
        draw_move_rotate()
        draw_lens_dist_aper()
        draw_unlock_lock()
        draw_camera_info()
        bpy.app.timers.register(draw_snap_unsnap,first_interval=0.01)

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
            track_to_target()
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
            track_to_target()
            draw_snap_unsnap()    
            return {'RUNNING_MODAL'}

        elif event.type == 'NUMPAD_ASTERIX':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += variables.camera_object.matrix_basis.to_quaternion() @ Vector((0, 0, variables.cam_target_distance_factor))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += variables.camera_object.matrix_basis.to_quaternion() @ Vector((0, 0, 10 * variables.cam_target_distance_factor))
            track_to_target()
            draw_snap_unsnap() 
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_8':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, 0.1 * variables.cam_target_distance_factor))
                    track_to_target()
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(-1))
            elif event.value == 'RELEASE' and event.ctrl:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, variables.cam_target_distance_factor))
                    track_to_target()
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(-10))
            draw_snap_unsnap() 
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_2':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, -0.1 * variables.cam_target_distance_factor))
                    track_to_target()
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(1))
            elif event.value == 'RELEASE' and event.ctrl:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, -variables.cam_target_distance_factor))
                    track_to_target()
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(10))
            draw_snap_unsnap() 
            return {'RUNNING_MODAL'}

        elif event.type == 'NUMPAD_6':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.target_object.rotation_euler.z += math.radians(1)
            elif event.value == 'RELEASE' and event.ctrl:
                variables.target_object.rotation_euler.z += math.radians(15)
            draw_snap_unsnap() 
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_4':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.target_object.rotation_euler.z += math.radians(-1)
            elif event.value == 'RELEASE' and event.ctrl:
                variables.target_object.rotation_euler.z += math.radians(-15)
            draw_snap_unsnap() 
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_7':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(-1))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(-15))
            draw_snap_unsnap() 
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_9':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(1))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(15))
            draw_snap_unsnap() 
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_1':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((-variables.cam_target_distance_factor, 0, 0)))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((-5 * variables.cam_target_distance_factor, 0, 0)))
            draw_snap_unsnap() 
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_3':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((variables.cam_target_distance_factor, 0, 0)))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((5 * variables.cam_target_distance_factor, 0, 0)))
            draw_snap_unsnap() 
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
                    else:
                        lens_steps = [
                            12, 14, 16, 18, 20, 21, 24, 28, 30, 35,
                            40, 45, 50, 55, 58, 70, 75, 80, 85, 90,
                            100, 105, 135, 150, 180, 200, 300, 400,
                            500, 600, 800, 1200
                        ]
                        # 找到大于当前焦距的第一个档位
                        for lens in lens_steps:
                            if variables.camera_lens < lens:
                                variables.camera_object.data.lens = lens
                                break

                    # 更新变量
                    variables.camera_lens = variables.camera_object.data.lens

                elif variables.num_zero == 1:
                    variables.camera_object.data.dof.focus_distance = variables.camera_distance + 10
                    variables.camera_distance = variables.camera_object.data.dof.focus_distance

                elif variables.num_zero == 2:
                    variables.camera_object.data.dof.aperture_fstop = variables.camera_aperture + 5
                    variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop

            draw_camera_info()
            draw_snap_unsnap() 
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
                if variables.num_zero == 0:
                    if variables.camera_lens <= 12:
                        variables.camera_object.data.lens = max(1, variables.camera_lens - 1)
                    else:
                        # 焦距档位列表，按升序排列
                        lens_steps = [
                            12, 14, 16, 18, 20, 21, 24, 28, 30, 35,
                            40, 45, 50, 55, 58, 70, 75, 80, 85, 90,
                            100, 105, 135, 150, 180, 200, 300, 400,
                            500, 600, 800, 1200
                        ]
                        # 从大到小找第一个小于当前焦距的档位
                        for lens in reversed(lens_steps):
                            if variables.camera_lens > lens:
                                variables.camera_object.data.lens = lens
                                break
                        else:
                            # 如果小于最小档位，直接减1
                            variables.camera_object.data.lens = variables.camera_lens - 1

                    # 更新变量
                    variables.camera_lens = variables.camera_object.data.lens

                elif variables.num_zero == 1:
                    variables.camera_object.data.dof.focus_distance = variables.camera_distance - 10
                    variables.camera_distance = variables.camera_object.data.dof.focus_distance

                elif variables.num_zero == 2:
                    variables.camera_object.data.dof.aperture_fstop = variables.camera_aperture - 5
                    variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop
            
            draw_camera_info()
            draw_snap_unsnap() 
            return {'RUNNING_MODAL'}
        
        elif event.type in {'UP_ARROW','DOWN_ARROW','LEFT_ARROW','RIGHT_ARROW'} and event.value == 'RELEASE':
            variables.camera_object.parent = None

            variables.target_object.rotation_euler[0] = math.radians(0)
            variables.target_object.rotation_euler[1] = math.radians(0)
            variables.target_object.rotation_euler[2] = math.radians(0)

            variables.camera_object.rotation_euler[0] = math.radians(90)
            variables.camera_object.rotation_euler[1] = math.radians(0)
            variables.camera_object.rotation_euler[2] = math.radians(0)

            bpy.ops.mesh.primitive_cube_add(size=variables.target_object_size, align='WORLD', location=variables.target_location)

            bpy.app.timers.register(lambda: (bpy.ops.view3d.camera_to_view_selected('INVOKE_DEFAULT'), None)[1], first_interval=0.01)

            bpy.app.timers.register(lambda: (bpy.data.objects.remove(bpy.context.active_object, do_unlink=True), None)[1], first_interval=0.01)

            variables.camera_object.parent = variables.target_object

            # 右视图
            if event.type == 'RIGHT_ARROW':
                variables.target_object.rotation_euler[2] = math.radians(90)

            elif event.type == 'LEFT_ARROW':
                variables.target_object.rotation_euler[2] = math.radians(-90)

            elif event.type == 'UP_ARROW':
                variables.target_object.rotation_euler[2] = math.radians(180)   

            draw_snap_unsnap() 
            return {'RUNNING_MODAL'}
        
        elif event.type in {'NUMPAD_ENTER','RET'} and event.value == 'RELEASE':
            if snapshot_detect.can_snapshot():
                bpy.ops.view3d.restore_snapshot()
            return {'RUNNING_MODAL'}
        
        # 鼠标移动直接 回到 modal
        elif event.type not in {'MOUSEMOVE','ESC','WHEELUPMOUSE','WHEELDOWNMOUSE','HOME','LEFTMOUSE','N'}:
            return {'RUNNING_MODAL'}
                
        elif event.type == 'ESC':
            # 先临时保存当前摄像机的 matrix_world ，删除target_object 之后再赋值给活动摄像头
            temp_matrix = variables.camera_object.matrix_world.copy()

            bpy.data.objects.remove(variables.target_object, do_unlink=True)

            variables.camera_object.matrix_world = temp_matrix

            bpy.types.SpaceView3D.draw_handler_remove(self.handle_backgroud, 'WINDOW')

            # 每次退出需要清零 matrix_world
            variables.target_object_size = 0
            variables.target_location = Vector((0.0, 0.0, 0.0))
            variables.camera_location = Vector((0.0, 0.0, 0.0))
            variables.cam_target_distance = 0
            variables.cam_target_distance_factor = 0
            variables.target_object = None
            variables.camera_object = None

            variables.origin_camera_location = None

            variables.camcompo_statu = False

            # 最后去除注释
            bpy.ops.view3d.view_camera('INVOKE_DEFAULT')

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

            # 测试成功后删除注释
            if camera_info.camera_info_statu:
                camera_info.camera_info_statu.cleanup()
                camera_info.camera_info_statu = None

            if icons_snap_unsnap.snap_unsnap_statu:
                icons_snap_unsnap.snap_unsnap_statu.cleanup()
                icons_snap_unsnap.snap_unsnap_statu = None


            return {'FINISHED'}
            

        return {'PASS_THROUGH'}










class CC_OT_cam_compo_single(bpy.types.Operator):
    bl_idname = "view3d.cam_compo_single"
    bl_label = "无参照物设置摄像机"
    bl_description = "无参照物设置摄像机"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        
        self.handle_backgroud = bpy.types.SpaceView3D.draw_handler_add(draw_background, (self,context), 'WINDOW', 'POST_PIXEL')
        draw_move_rotate()
        draw_lens_dist_aper()
        draw_unlock_lock()
        draw_camera_info()
        bpy.app.timers.register(draw_snap_unsnap,first_interval=0.01)
        

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type =='NUMPAD_5':
            if event.value == 'RELEASE':
                variables.num_five = not variables.num_five
            draw_move_rotate()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_0':
            if event.value == 'RELEASE':
                variables.num_zero = (variables.num_zero + 1) % 3
            draw_lens_dist_aper()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_SLASH':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += variables.camera_object.matrix_basis.to_quaternion() @ Vector((0, 0, -0.1))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += variables.camera_object.matrix_basis.to_quaternion() @ Vector((0, 0, -1))
            draw_snap_unsnap()
            return {'RUNNING_MODAL'}
        

        elif event.type == 'NUMPAD_ASTERIX':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += variables.camera_object.matrix_basis.to_quaternion() @ Vector((0, 0, 0.1))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += variables.camera_object.matrix_basis.to_quaternion() @ Vector((0, 0, 1))
            draw_snap_unsnap()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_8':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, 0.1))
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(-1))
            elif event.value == 'RELEASE' and event.ctrl:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, 1))
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(-10))
            draw_snap_unsnap()
            return {'RUNNING_MODAL'}
        
        
        elif event.type == 'NUMPAD_2':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, -0.1))
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(1))
            elif event.value == 'RELEASE' and event.ctrl:
                if variables.num_five:
                    variables.camera_object.location += Vector((0, 0, -1))
                else:
                    variables.camera_object.rotation_euler.rotate_axis("X", math.radians(10))
            draw_snap_unsnap()
            return {'RUNNING_MODAL'}


        elif event.type == 'NUMPAD_6':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.rotation_euler.rotate(Matrix.Rotation(math.radians(1), 4, 'Z'))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.rotation_euler.rotate(Matrix.Rotation(math.radians(15), 4, 'Z'))
            draw_snap_unsnap()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_4':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.rotation_euler.rotate(Matrix.Rotation(math.radians(-1), 4, 'Z'))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.rotation_euler.rotate(Matrix.Rotation(math.radians(-15), 4, 'Z'))
            draw_snap_unsnap()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_7':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(-1))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(-15))
            draw_snap_unsnap()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_9':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(1))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.rotation_euler.rotate_axis("Z", math.radians(15))
            draw_snap_unsnap()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_1':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((-0.1, 0, 0)))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((-0.5, 0, 0)))
            draw_snap_unsnap()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'NUMPAD_3':
            if event.value == 'PRESS' and not event.ctrl and not event.shift and not event.alt:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((0.1, 0, 0)))
            elif event.value == 'RELEASE' and event.ctrl:
                variables.camera_object.location += (variables.camera_object.matrix_basis.to_quaternion() @ Vector((0.5, 0, 0)))
            draw_snap_unsnap()
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
                    else:
                        lens_steps = [
                            12, 14, 16, 18, 20, 21, 24, 28, 30, 35,
                            40, 45, 50, 55, 58, 70, 75, 80, 85, 90,
                            100, 105, 135, 150, 180, 200, 300, 400,
                            500, 600, 800, 1200
                        ]
                        # 找到大于当前焦距的第一个档位
                        for lens in lens_steps:
                            if variables.camera_lens < lens:
                                variables.camera_object.data.lens = lens
                                break

                    # 更新变量
                    variables.camera_lens = variables.camera_object.data.lens

                elif variables.num_zero == 1:
                    variables.camera_object.data.dof.focus_distance = variables.camera_distance + 10
                    variables.camera_distance = variables.camera_object.data.dof.focus_distance

                elif variables.num_zero == 2:
                    variables.camera_object.data.dof.aperture_fstop = variables.camera_aperture + 5
                    variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop

            draw_camera_info()
            draw_snap_unsnap()
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
                if variables.num_zero == 0:
                    if variables.camera_lens <= 12:
                        variables.camera_object.data.lens = max(1, variables.camera_lens - 1)
                    else:
                        # 焦距档位列表，按升序排列
                        lens_steps = [
                            12, 14, 16, 18, 20, 21, 24, 28, 30, 35,
                            40, 45, 50, 55, 58, 70, 75, 80, 85, 90,
                            100, 105, 135, 150, 180, 200, 300, 400,
                            500, 600, 800, 1200
                        ]
                        # 从大到小找第一个小于当前焦距的档位
                        for lens in reversed(lens_steps):
                            if variables.camera_lens > lens:
                                variables.camera_object.data.lens = lens
                                break
                        else:
                            # 如果小于最小档位，直接减1
                            variables.camera_object.data.lens = variables.camera_lens - 1

                    # 更新变量
                    variables.camera_lens = variables.camera_object.data.lens

                elif variables.num_zero == 1:
                    variables.camera_object.data.dof.focus_distance = variables.camera_distance - 10
                    variables.camera_distance = variables.camera_object.data.dof.focus_distance

                elif variables.num_zero == 2:
                    variables.camera_object.data.dof.aperture_fstop = variables.camera_aperture - 5
                    variables.camera_aperture = variables.camera_object.data.dof.aperture_fstop
            
            draw_camera_info()
            draw_snap_unsnap()
            return {'RUNNING_MODAL'}
        
        elif event.type in {'NUMPAD_ENTER','RET'} and event.value == 'RELEASE':
            if snapshot_detect.can_snapshot():
                bpy.ops.view3d.restore_snapshot()
            return {'RUNNING_MODAL'}
                
        # 鼠标移动直接 回到 modal
        elif event.type not in {'MOUSEMOVE','ESC','WHEELUPMOUSE','WHEELDOWNMOUSE','HOME','LEFTMOUSE','N'}:
            return {'RUNNING_MODAL'}
                
        elif event.type == 'ESC':
            bpy.types.SpaceView3D.draw_handler_remove(self.handle_backgroud, 'WINDOW')

            # 每次退出需要清零 matrix_world
            variables.camera_object = None

            variables.camcompo_statu = False

            # 最后去除注释
            bpy.ops.view3d.view_camera('INVOKE_DEFAULT')

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

            # 测试成功后删除注释
            if camera_info.camera_info_statu:
                camera_info.camera_info_statu.cleanup()
                camera_info.camera_info_statu = None

            if icons_snap_unsnap.snap_unsnap_statu:
                icons_snap_unsnap.snap_unsnap_statu.cleanup()
                icons_snap_unsnap.snap_unsnap_statu = None


            return {'FINISHED'}
            

        return {'PASS_THROUGH'}
