import bpy
from bpy.types import(
    Texture,
    Image,
    TextureSlot,
    PropertyGroup,
)
from bpy.props import (
    PointerProperty,
    CollectionProperty,
    EnumProperty,
)


def mesh_obj_enum_cb(self, context):
    if not (context.object and context.object.type == 'ARMATURE'): return

    # breakpoint()
    for child in context.object.children:
        if child.type != 'MESH': continue
        yield child.name, child.name, 'Object'


def shape_key_enum_cb(self, context):
    props = context.scene.wrmap_props
    mesh_obj = context.scene.objects.get(props.mesh_object)

    for key_block in mesh_obj.data.shape_keys.key_blocks:
        yield key_block.name, key_block.name, 'Shape Key'


class WrinkleMapProperties(PropertyGroup):
    wrinkle_texture: PointerProperty(
        type=Image,
        name='Normal Map',
        description='Выберите карту нормали для смешивания'
    )
    mesh_object: EnumProperty(
        name='Object',
        description='Выберите объект',
        items=mesh_obj_enum_cb
    )
    shape_key: EnumProperty(
        name='Shape Key',
        description='Выберите Shape Key',
        items=shape_key_enum_cb,
    )
    bone_transform: EnumProperty(
        name='Bone Property',
        description='Выберите трансформацию кости для драйвера',
        items=(
            ('LOC_X', 'Location X', ''),
            ('LOC_Y', 'Location Y', ''),
            ('LOC_Z', 'Location Z', ''),

            ('ROT_X', 'Rotation X', ''),
            ('ROT_Y', 'Rotation Y', ''),
            ('ROT_Z', 'Rotation Z', ''),
        ),
        default=1
    )
