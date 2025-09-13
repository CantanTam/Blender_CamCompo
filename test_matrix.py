import bpy
from . import variables

class CC_OT_test_matrix(bpy.types.Operator):
    bl_idname = "cc.test_matrix"
    bl_label = "测试matrix"
    bl_description = "测试matrix"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        variables.test_matrix = variables.camera_object.matrix_world.copy()
        return {'FINISHED'}
    
class CC_OT_get_matrix(bpy.types.Operator):
    bl_idname = "cc.get_matrix"
    bl_label = "获取matrix"
    bl_description = "获取matrix"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.active_object.matrix_world = variables.test_matrix
        return {'FINISHED'}