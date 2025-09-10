import bpy,gpu,os
from gpu_extras.batch import batch_for_shader
from . import variables

# 全局控制变量
lens_dist_aper_statu = None



class DrawLensDistAper:
    def __init__(self,):
        if variables.num_zero == 0 :
            self.image_path = 'ICON_LENS.png'
        elif variables.num_zero == 1:
            self.image_path = 'ICON_DIST.png'
        else:
            self.image_path = 'ICON_APER.png'
        self.handler = None
        #self.needs_redraw = False

        # 使用固定 notices 文件夹
        if not os.path.isabs(self.image_path):
            script_dir = os.path.dirname(os.path.realpath(__file__))
            script_dir = os.path.normpath(script_dir)
            self.image_path = os.path.normpath(
                os.path.join(script_dir, "icons", self.image_path)
            )

        self.image = bpy.data.images.load(self.image_path)
        self.texture = gpu.texture.from_image(self.image)

        if bpy.app.version <= (4, 0, 0):
            self.shader = gpu.shader.from_builtin('2D_IMAGE')
        else:
            self.shader = gpu.shader.from_builtin('IMAGE')

        self.vertices = {
            "pos": [
                ((bpy.context.region.width - 595) * 0.5, 0),
                ((bpy.context.region.width + 595) * 0.5, 0),
                ((bpy.context.region.width + 595) * 0.5, 85),
                ((bpy.context.region.width - 595) * 0.5, 85)
            ],
            "texCoord": [(0, 0), (1, 0), (1, 1), (0, 1)],
        }
        self.batch = batch_for_shader(self.shader, 'TRI_FAN', self.vertices)

        self.handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, (), 'WINDOW', 'POST_PIXEL')


    def draw(self):
        self.batch = batch_for_shader(self.shader, 'TRI_FAN', self.vertices)
        gpu.state.blend_set('ALPHA')
        self.shader.bind()
        self.shader.uniform_sampler("image", self.texture)
        self.batch.draw(self.shader)
        gpu.state.blend_set('NONE')


    def cleanup(self):
        if self.handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')
            self.handler = None

        if getattr(self, 'texture', None):
            self.texture = None  # 删除引用，让 Blender 内部回收 GPU 资源

        if getattr(self, 'image', None):
            bpy.data.images.remove(self.image)



def draw_lens_dist_aper():
    global lens_dist_aper_statu
    if lens_dist_aper_statu:
        lens_dist_aper_statu.cleanup()
        lens_dist_aper_statu = None
    
    lens_dist_aper_statu = DrawLensDistAper()
    return lens_dist_aper_statu


