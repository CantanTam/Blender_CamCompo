import bpy,gpu
from gpu_extras.batch import batch_for_shader

def draw_background(self,context):
    bottom_vertices = [(0, 0),(bpy.context.region.width, 0),(bpy.context.region.width, 85),(0, 85)]
    bottom_indices = [(0, 1, 2), (2, 3, 0)]

    top_vertices = [
        (0,bpy.context.region.height - 100),
        (bpy.context.region.width,bpy.context.region.height - 100),
        (bpy.context.region.width,bpy.context.region.height),
        (0,bpy.context.region.height)]
    
    top_indices = [(4, 5 ,6),(6, 7, 4)]

    vertices = top_vertices + bottom_vertices
    indices = top_indices + bottom_indices

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

    gpu.state.blend_set('ALPHA')

    shader.bind()
    shader.uniform_float("color",  (0, 0, 0, 0.35))
    batch.draw(shader)

    gpu.state.blend_set('NONE')
    