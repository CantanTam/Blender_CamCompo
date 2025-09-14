import bpy
from mathutils import Vector

camcompo_statu = False

target_object_size = 0

single_camera = True

target_location = Vector((0.0, 0.0, 0.0))

camera_location = Vector((0.0, 0.0, 0.0))

origin_camera_location = None

cam_target_distance = 0
cam_target_distance_factor = 0

target_object = None
camera_object = None

camera_lens = 0
camera_distance = 0
camera_aperture = 0

num_five = True
num_period = False # True → 追踪；False → 放弃追踪
num_zero = 0 # 0 → lens；1 → distance； 2 → aperture

test_matrix = None

snapshot_statu = False

