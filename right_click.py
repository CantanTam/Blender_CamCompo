import bpy

def rightclick_cam_control(self, context):
    if len(bpy.context.selected_objects) < 2 or bpy.context.active_object.type != 'CAMERA':
        return
    
    layout = self.layout
    layout.separator()
    layout.operator("view3d.cam_it_invoke",text="进入CamControll", icon='CAMERA_DATA')
    