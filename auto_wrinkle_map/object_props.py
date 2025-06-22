import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import (
    Armature,
    Bone,
    Image,
    Key,
    Material,
    NodeTree,
    Object,
    PropertyGroup,
    Texture,
    TextureSlot,
)

from .utils import (
    BONE_TRANSFORMS,
    add_node_groups,
    delete_node_groups,
    set_node_group_driver,
)


def mat_poll_cb(self, mat):
    return mat in (slot.material for slot in bpy.context.object.material_slots)


def mat_update_cb(self, context):
    if not self.expand: return
    print('mat_update_cb:')

    for mat_slot in context.object.material_slots:
        delete_node_groups(mat_slot.material, self.node_tree)

    for gr in add_node_groups(self.material, self.node_tree):
        set_node_group_driver(gr, self)


def armature_poll_cb(self, arm):
    return arm == bpy.context.object.parent


def bone_enum_cb(self, context):
    if not self.armature:
        return
    for bone in self.armature.data.bones:
        yield bone.name, bone.name, 'Bone'


def shape_key_enum_cb(self, context):
    mesh_obj = context.object
    if mesh_obj.type != 'MESH': return
    for key_block in mesh_obj.data.shape_keys.key_blocks:
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
        poll=mat_poll_cb,
        update=mat_update_cb,
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
