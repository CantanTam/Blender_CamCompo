import bpy,gpu,blf
#from gpu_extras.batch import batch_for_shader
from . import variables

camera_info_statu = None

def get_unit():
    scene = bpy.context.scene
    unit_system = scene.unit_settings.system      # 'NONE', 'METRIC', 'IMPERIAL'
    scale = scene.unit_settings.scale_length      # 缩放比例

    if unit_system == 'METRIC':
        # 根据 scale 决定显示单位
        if scale >= 1.0:
            return '米'
        elif scale >= 0.01:
            return '厘米'
        else:
            return '毫米'
    elif unit_system == 'IMPERIAL':
        # 简单返回英制单位
        if scale >= 1.0:
            return '英尺'
        else:
            return '英寸'
    else:
        # NONE 模式
        return 'BU'  # Blender Unit

class DrawCameraInfo:
    def __init__(self,):
        #blf.size(0, int(25*(bpy.context.preferences.system.dpi/72)))
        self.camera_info = f"焦距:{variables.camera_lens:.1f} mm     |     光圈:f/{variables.camera_aperture:.1f}     |     焦点距离:{variables.camera_distance:.1f} {get_unit()}"

        self.handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, (), 'WINDOW', 'POST_PIXEL')


    def draw(self):
        blf.size(0, int(20*(bpy.context.preferences.system.dpi/72)))
        info_width, _ = blf.dimensions(0, self.camera_info)
        self.camera_info_x = (bpy.context.area.width - info_width)/2
        self.camera_info_y = (bpy.context.area.height - 75)
        gpu.state.blend_set('ALPHA')
        blf.position(0, self.camera_info_x, self.camera_info_y, 0)
        blf.draw(0,self.camera_info)
        gpu.state.blend_set('NONE')

    def cleanup(self):
        if self.handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
            self.handler = None

def draw_camera_info():
    global camera_info_statu
    if camera_info_statu:
        camera_info_statu.cleanup()
        camera_info_statu = None


    camera_info_statu = DrawCameraInfo()
    return camera_info_statu

