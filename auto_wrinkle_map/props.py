import bpy
from bpy.types import(
    TextureSlot,
    PropertyGroup
)


class WrinkleMapProperties(PropertyGroup):
    wrinkle_texture: TextureSlot()
