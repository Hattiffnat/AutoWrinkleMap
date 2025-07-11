import bpy

from .object_props import WrinklePropsObject
from .operators import AddWrinkleMapOperator, RemoveWrinkleMapOperator
from .scene_props import WrinklePropsScene
from .ui import WrinkleMapPanel

classes = (
    WrinkleMapPanel,
    AddWrinkleMapOperator,
    RemoveWrinkleMapOperator,
    WrinklePropsScene,
    WrinklePropsObject,
)


def register():
    # breakpoint()
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.wrmap_props = bpy.props.PointerProperty(type=WrinklePropsScene)  # pyright: ignore
    bpy.types.Object.wrinkles = bpy.props.CollectionProperty(type=WrinklePropsObject)  # pyright: ignore


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.wrinkles  # pyright: ignore
    del bpy.types.Scene.wrmap_props  # pyright: ignore
