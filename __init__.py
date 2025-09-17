import bpy
import os
from bpy.props import FloatProperty, FloatVectorProperty, CollectionProperty, IntProperty
from .camera_snapshot_sidebar import click_snapshot_action,click_camera_action

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

from .camera_snapshot_list import (
    CameraSnapshot,
    CameraItem,
)

from .camera_snapshot_sidebar import (
    CC_UL_camera_snapshots,
    CC_PT_snapshot_sidebar,
    CC_UL_camera_items,
    CC_PT_cam_switch_sidebar,
    CC_OT_add_camera,
    CC_OT_delete_camera,
    CC_OT_update_camera,
    CC_OT_open_bilibili,
    CC_OT_prev_snapshot,
    CC_OT_next_snapshot,
    CC_OT_restore_snapshot,
    CC_OT_remove_snapshot,
    CC_OT_goto_snapshot,
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
    #update_camera_list()
    bpy.utils.register_class(CC_OT_cam_compo_invoke)
    bpy.utils.register_class(CC_OT_cam_compo_multi)
    bpy.utils.register_class(CC_OT_cam_compo_single)
    bpy.utils.register_class(CameraSnapshot)
    bpy.types.Object.camera_snapshots = CollectionProperty(type=CameraSnapshot)
    bpy.types.Object.camera_snapshots_index = IntProperty(default=0,update=click_snapshot_action)
    bpy.utils.register_class(CameraItem)
    bpy.types.Scene.camera_items = bpy.props.CollectionProperty(type=CameraItem)
    bpy.types.Scene.camera_items_index = bpy.props.IntProperty(default=0,update=click_camera_action)
    bpy.utils.register_class(CC_UL_camera_snapshots)
    bpy.utils.register_class(CC_PT_snapshot_sidebar)
    bpy.utils.register_class(CC_UL_camera_items)
    bpy.utils.register_class(CC_PT_cam_switch_sidebar)
    bpy.utils.register_class(CC_OT_add_camera)
    bpy.utils.register_class(CC_OT_delete_camera)
    bpy.utils.register_class(CC_OT_update_camera)
    bpy.utils.register_class(CC_OT_open_bilibili)
    bpy.utils.register_class(CC_OT_prev_snapshot)
    bpy.utils.register_class(CC_OT_next_snapshot)
    bpy.utils.register_class(CC_OT_restore_snapshot)
    bpy.utils.register_class(CC_OT_remove_snapshot)
    bpy.utils.register_class(CC_OT_goto_snapshot)
    register_keymaps()
    bpy.types.VIEW3D_MT_object_context_menu.append(rightclick_cam_control)
    


def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(rightclick_cam_control)
    unregister_keymaps()

    bpy.utils.unregister_class(CC_OT_goto_snapshot)
    bpy.utils.unregister_class(CC_OT_remove_snapshot)
    bpy.utils.unregister_class(CC_OT_restore_snapshot)
    bpy.utils.unregister_class(CC_OT_next_snapshot)
    bpy.utils.unregister_class(CC_OT_prev_snapshot)
    bpy.utils.unregister_class(CC_OT_open_bilibili)
    bpy.utils.unregister_class(CC_OT_update_camera)
    bpy.utils.unregister_class(CC_OT_delete_camera)
    bpy.utils.unregister_class(CC_OT_add_camera)
    bpy.utils.unregister_class(CC_PT_cam_switch_sidebar)
    bpy.utils.unregister_class(CC_UL_camera_items)
    bpy.utils.unregister_class(CC_PT_snapshot_sidebar)
    bpy.utils.unregister_class(CC_UL_camera_snapshots)
    del bpy.types.Scene.camera_items_index
    del bpy.types.Scene.camera_items
    bpy.utils.unregister_class(CameraItem)
    del bpy.types.Object.camera_snapshots_index
    del bpy.types.Object.camera_snapshots
    bpy.utils.unregister_class(CameraSnapshot)
    bpy.utils.unregister_class(CC_OT_cam_compo_single)
    bpy.utils.unregister_class(CC_OT_cam_compo_multi)
    bpy.utils.unregister_class(CC_OT_cam_compo_invoke)
    #pass





if __name__ == "__main__":
    register()
