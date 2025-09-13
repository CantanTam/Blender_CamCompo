import bpy

def rightclick_cam_control(self, context):
    if bpy.context.active_object.type != 'CAMERA' or bpy.context.mode != 'OBJECT':
        return
    
    layout = self.layout
    layout.separator()
    layout.operator("view3d.cam_compo_invoke",text="进入CamControll", icon='CAMERA_DATA')
    layout.operator("cc.get_matrix", text="test matrix")
    