import bpy

def rightclick_cam_control(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("view3d.cam_it_invoke",text="进入CamControll", icon='CAMERA_DATA')
    