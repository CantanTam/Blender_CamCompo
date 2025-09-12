import bpy
import os

bl_info = {
    "name": "CamCompo",
    "author": "Canta Tam",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D",
    "description": "让你无需再记快捷键",
    "category": "3D View",
    "doc_url": "https://www.bilibili.com/video/BV12q4y1t7h9/?spm_id_from=333.1387.upload.video_card.click&vd_source=e4cbc5ec88a2d9cfc7450c34eb007abe", 
    "support": "COMMUNITY"
}

ADDON_NAME = os.path.basename(os.path.dirname(__file__))

addon_keymaps = []

from .cam_compo import (
    CC_OT_cam_compo_invoke,
    CC_OT_cam_compo_multi,
    CC_OT_cam_compo_single,
)

from .right_click import rightclick_cam_control

def register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("view3d.cam_compo_invoke", type='F6', value='RELEASE')
        addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def register():
    bpy.utils.register_class(CC_OT_cam_compo_invoke)
    bpy.utils.register_class(CC_OT_cam_compo_multi)
    bpy.utils.register_class(CC_OT_cam_compo_single)
    register_keymaps()
    bpy.types.VIEW3D_MT_object_context_menu.append(rightclick_cam_control)
    


def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(rightclick_cam_control)
    unregister_keymaps()
    bpy.utils.unregister_class(CC_OT_cam_compo_single)
    bpy.utils.unregister_class(CC_OT_cam_compo_multi)
    bpy.utils.unregister_class(CC_OT_cam_compo_invoke)






if __name__ == "__main__":
    register()
