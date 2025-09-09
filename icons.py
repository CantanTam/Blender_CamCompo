import bpy,gpu,os
from gpu_extras.batch import batch_for_shader
from . import variables

# 全局控制变量
camera_statu = None



class DrawController:
    def __init__(self,):
        if variables.num_five :
            self.image_path = 'NOTICE_A.png'
        else:
            self.image_path = 'NOTICE_B.png'
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
                ((bpy.context.region.width - 550) * 0.5, 0),
                ((bpy.context.region.width + 550) * 0.5, 0),
                ((bpy.context.region.width + 550) * 0.5, 70),
                ((bpy.context.region.width - 550) * 0.5, 70)
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



def draw_icon():
    global camera_statu
    if camera_statu:
        camera_statu.cleanup()
        camera_statu = None
    
    camera_statu = DrawController()
    return camera_statu


