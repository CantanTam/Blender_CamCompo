import bpy
from bpy.types import PropertyGroup,Object
from bpy.props import FloatProperty, FloatVectorProperty, StringProperty, CollectionProperty, IntProperty,PointerProperty
from mathutils import Matrix


# 定义数组的单个元素
class CameraSnapshot(PropertyGroup):
    name: StringProperty(name="重命名快照")
    lens: FloatProperty(name="Lens")
    focus_distance: FloatProperty(name="Focus Distance")
    aperture_fstop: FloatProperty(name="Aperture f/stop")
    matrix_world: FloatVectorProperty(
        name="Matrix World",
        size=16,               # 4x4 扁平化矩阵
        subtype='MATRIX',
        default=(1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0)
        )

def call_update_camera_list(self,context):
    index = context.scene.camera_items_index
    cameraitem = context.scene.camera_items[index]
    cameraitem.camera_item.name = cameraitem.camera_name
    #pass

class CameraItem(bpy.types.PropertyGroup):
    camera_item: PointerProperty(type=Object)
    camera_name: StringProperty(
        name="重命名相机",
        update=call_update_camera_list
    )