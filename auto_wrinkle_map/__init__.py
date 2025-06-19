import bpy

from .scene_props import WrinklePropsScene
from .object_props import WrinklePropsObject
from .opers import AddWrinkleMapOperator, RemoveWrinkleMapOperator
from .ui import WrinkleMapPanel
from .handler import awm_set_tree_handler

# оставлю на всякий случай
# bl_info = {
#     'name': 'Auto Wrinkle Map',
#     'website': 'https://github.com/Hattiffnat/AutoWrinkleMap',
#     'author': 'Hattiffnat',
#     'version': (0, 0, 4),
#     'blender': (4, 4, 0),
#     'location': 'View3D > Sidebar > Auto Wrinkle Map Tab',
#     'description': 'Helps you to create wrinkle maps driven from bones '
#                    '(with shape-keys) in one click',
#     'category': 'Rigging',
# }


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

    bpy.app.handlers.load_post.append(awm_set_tree_handler)
    bpy.app.handlers.version_update.append(awm_set_tree_handler)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.wrinkles
    del bpy.types.Scene.wrmap_props

    bpy.app.handlers.load_post.remove(awm_set_tree_handler)
    bpy.app.handlers.version_update.remove(awm_set_tree_handler)
