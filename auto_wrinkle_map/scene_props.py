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

from .utils import BONE_TRANSFORMS


def mesh_obj_enum_cb(self, context):
    if not (context.object and context.object.type == 'ARMATURE'): return

    # breakpoint()
    for child in context.object.children:
        if child.type != 'MESH': continue
        yield child.name, child.name, 'Object'


def shape_key_enum_cb(self, context):
    mesh_obj = context.object
    if (mesh_obj.type != 'MESH') or (mesh_obj.data.shape_keys is None):
        return

    for kb in mesh_obj.data.shape_keys.key_blocks:
        yield (kb.name, kb.name, "Shape Key")


def mat_poll_cb(self, mat):
    # breakpoint()
    return mat in (slot.material for slot in bpy.context.object.material_slots)


def armature_poll_cb(self, arm):
    # breakpoint()
    return arm == bpy.context.object.parent


def bone_enum_cb(self, context):
    if not self.armature:
        return
    for bone in self.armature.data.bones:
        yield bone.name, bone.name, 'Bone'


class WrinklePropsScene(PropertyGroup):
    name: StringProperty(
        name='Setup Name',
        default='My wrinkle map'
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
    )
    bone_transform: EnumProperty(
        name='Bone Transform',
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
