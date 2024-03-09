import bpy

from .scene_props import WrinklePropsScene
from .object_props import WrinklePropsObject
from .opers import AddWrinkleMapOperator, RemoveWrinkleMapOperator
from .ui import WrinkleMapPanel
from .handler import set_tree_handler


bl_info = {
    'name': 'Auto Wrinkle Map',
    'author': 'Hattiffnat',
    'version': (0, 0, 1),
    'blender': (4, 0, 2),
    'location': 'View3D > Sidebar > Auto Wrinkle Map Tab',
    'description': 'Быстрое смешивание текстур на основе драйвера кости',
    'category': 'Node',
}


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

    # Свойства сцены для создания
    bpy.types.Scene.wrmap_props = bpy.props.PointerProperty(type=WrinklePropsScene)
    # Свойства в объекте для хранения
    bpy.types.Object.wrinkles = bpy.props.CollectionProperty(type=WrinklePropsObject)

    bpy.app.handlers.load_post.append(set_tree_handler)
    # bpy.app.handlers.load_post.append(set_tree_handler)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.wrinkles
    del bpy.types.Scene.wrmap_props

    bpy.app.handlers.load_post.remove(set_tree_handler)
    # bpy.app.handlers.load_post.remove(set_tree_handler)
