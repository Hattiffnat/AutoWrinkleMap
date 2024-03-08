import bpy
from bpy.types import(
    Texture,
    Image,
    TextureSlot,
    PropertyGroup,
    Armature,
    Bone,
    Object,
    NodeTree,
    Key,
    Material,
)
from bpy.props import (
    PointerProperty,
    CollectionProperty,
    EnumProperty,
    StringProperty,
    BoolProperty
)


BONE_TRANSFORMS = (
    ('LOC_X', 'Location X', ''),
    ('LOC_Y', 'Location Y', ''),
    ('LOC_Z', 'Location Z', ''),

    ('ROT_X', 'Rotation X', ''),
    ('ROT_Y', 'Rotation Y', ''),
    ('ROT_Z', 'Rotation Z', ''),
)


def mesh_obj_enum_cb(self, context):
    if not (context.object and context.object.type == 'ARMATURE'): return

    # breakpoint()
    for child in context.object.children:
        if child.type != 'MESH': continue
        yield child.name, child.name, 'Object'


def shape_key_enum_cb(self, context):
    mesh_obj = context.object
    if mesh_obj.type != 'MESH': return
    for key_block in mesh_obj.data.shape_keys.key_blocks:
        yield key_block.name, key_block.name, 'Shape Key'


def shape_key_poll_cb(self, key):
    return True


def mat_poll_cb(self, mat):
    # breakpoint()
    return mat in (slot.material for slot in bpy.context.object.material_slots)


def armature_poll_cb(self, arm):
    # breakpoint()
    return arm == bpy.context.object.parent


def bone_enum_cb(self, context):
    arm = context.scene.wrmap_props.armature
    if not arm: return
    for bone in arm.data.bones:
        yield bone.name, bone.name, 'Bone'


class WrinklePropsScene(PropertyGroup):
    name: StringProperty(
        name='Setup Name',
        default='My wrinkle map'
    )
    wrinkle_image: PointerProperty(
        type=Image,
        name='Normal Map',
        description='Select normal map for mix'
    )
    material: PointerProperty(
        type=Material,
        name='Material',
        description='Select material',
        poll=mat_poll_cb,
    )
    armature: PointerProperty(
        type=Object,
        name='Armature',
        description='Select armature',
        poll=armature_poll_cb,
    )
    bone: EnumProperty(
        name='Bone',
        description='Select bone',
        items=bone_enum_cb,
        default=0,
    )
    bone_transform: EnumProperty(
        name='Bone Property',
        description='Select bone transformation for driver',
        items=BONE_TRANSFORMS,
        default=1
    )
    shape_key: EnumProperty(
        name='Shape Key',
        description='Select shape key',
        items=shape_key_enum_cb,
    )
    node_tree: PointerProperty(
        type=NodeTree,
        name='Node Tree',
    )


class WrinklePropsObject(PropertyGroup):
    expand: BoolProperty(name='Expand', default=False)
    name: StringProperty(
        name='Setup Name',
    )
    wrinkle_image: PointerProperty(
        type=Image,
    )
    material: PointerProperty(
        type=Material,
        poll=mat_poll_cb,
    )
    armature: PointerProperty(
        type=Object,
        poll=armature_poll_cb,
    )
    bone: EnumProperty(
        items=bone_enum_cb,
        default=0,
    )
    bone_transform: EnumProperty(
        name='Bone Property',
        description='Select bone transformation for driver',
        items=BONE_TRANSFORMS,
        default=1
    )
    shape_key: EnumProperty(
        name='Shape Key',
        description='Select shape key',
        items=shape_key_enum_cb,
    )
    node_tree: PointerProperty(
        type=NodeTree,
        name='Node Tree',
    )
