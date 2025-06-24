# pyright: reportMissingModuleSource=false, reportInvalidTypeForm=false

import bpy
from bpy.props import (
    EnumProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import (
    Armature,
    Context,
    Image,
    Material,
    Mesh,
    NodeTree,
    Object,
    PropertyGroup,
)

from .utils import BONE_TRANSFORMS


def mesh_obj_enum_cb(self, context):
    if not (context.object and context.object.type == 'ARMATURE'):
        return

    # breakpoint()
    for child in context.object.children:
        if child.type != 'MESH':
            continue
        yield child.name, child.name, 'Object'


def shape_key_enum_cb(self, context: Context):
    mesh_obj: Object = getattr(context, 'object')
    if mesh_obj.type != 'MESH':
        return

    mesh: Mesh = getattr(mesh_obj, 'data')

    if mesh.shape_keys is None:
        return

    for kb in getattr(mesh.shape_keys, 'key_blocks'):
        yield (kb.name, kb.name, 'Shape Key')


def mat_poll_cb(self, mat: Material):
    return mat in (slot.material for slot in bpy.context.object.material_slots)  # pyright: ignore


def armature_poll_cb_1(self, arm: Armature):
    if bpy.context.object.parent is None:
        return False

    if bpy.context.object.parent.type != 'ARMATURE':
        return False

    return arm == bpy.context.object.parent


def armature_poll_cb_2(self, arm: Object):
    return arm.type == 'ARMATURE'


def bone_enum_cb(self, context: Context):
    if self.armature is None:
        return

    for bone in self.armature.data.bones:
        yield bone.name, bone.name, 'Bone'


class WrinklePropsScene(PropertyGroup):
    name: StringProperty(name='Setup Name', default='My wrinkle map')
    image: PointerProperty(
        name='Wrinkle Map', type=Image, description='Select wrinkle normal map'
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
        poll=armature_poll_cb_2,
    )
    bone: EnumProperty(
        name='Bone',
        description='Select bone',
        items=bone_enum_cb,  # pyright: ignore
    )
    bone_transform: EnumProperty(
        name='Bone Transform',
        description='Select bone transformation for driver',
        items=BONE_TRANSFORMS,
        default=1,  # pyright: ignore
    )
    shape_key: EnumProperty(
        name='Shape Key',
        description='Select shape key',
        items=shape_key_enum_cb,  # pyright: ignore
    )
    node_tree: PointerProperty(
        type=NodeTree,
        name='Node Tree',
    )
