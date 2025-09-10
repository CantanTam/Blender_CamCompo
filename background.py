import bpy,gpu
from gpu_extras.batch import batch_for_shader

def draw_background(self,context):
    vertices = [(0, 0),(bpy.context.region.width, 0),(0, 85),(bpy.context.region.width, 85)]
    indices = [(0, 1, 2), (2, 1, 3)]
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

    gpu.state.blend_set('ALPHA')

    shader.bind()
    shader.uniform_float("color",  (0, 0, 0, 0.35))
    batch.draw(shader)

    gpu.state.blend_set('NONE')