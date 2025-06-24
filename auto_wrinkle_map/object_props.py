# pyright: reportMissingModuleSource=false, reportInvalidTypeForm=false

from typing import Optional

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import (
    Context,
    Material,
    Mesh,
    NodeTree,
    Object,
    PropertyGroup,
)

from .utils import (
    BONE_TRANSFORMS,
    add_node_groups,
    delete_node_groups,
    set_node_group_driver,
)


def mat_update_cb(self, context: Context):
    if not self.expand:
        return
    print('mat_update_cb:')

    obj: Object = getattr(context, 'object')

    for mat_slot in getattr(obj, 'material_slots'):
        delete_node_groups(mat_slot.material, self.node_tree)

    for gr in add_node_groups(self.material, self.node_tree):
        set_node_group_driver(gr, self)


def bone_enum_cb(self, _: Context):
    if self.armature is None:
        return
    for bone in self.armature.data.bones:
        yield bone.name, bone.name, 'Bone'


def shape_key_enum_cb(self, context: Context):
    mesh_obj: Object = getattr(context, 'object')
    if mesh_obj.type != 'MESH':
        return
    mesh: Mesh = getattr(mesh_obj, 'data')
    for key_block in getattr(mesh.shape_keys, 'key_blocks'):
        yield key_block.name, key_block.name, 'Shape Key'


class WrinklePropsObject(PropertyGroup):
    expand: BoolProperty(name='Expand', default=False)
    name: StringProperty(
        name='Setup Name',
    )
    material: PointerProperty(
        type=Material,
        name='Material',
        description='Select material',
        update=mat_update_cb,
        options={'HIDDEN'}
    )
    armature: PointerProperty(
        type=Object,
        name='Armature',
        description='Select armature',
        options={'HIDDEN'}
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
