import bpy

from .props import WrinkleMapProperties
from .opers import AddWrinkleMapOperator
from .settings import settings


bl_info = {
    'name': 'Auto Wrinkle Map',
    'author': 'Hattiffnat',
    'version': (0, 0, 0),
    'blender': (4, 0, 2),
    'location': 'View3D > Sidebar > Edit Tab',
    'description': 'Быстрое смешивание текстур на основе драйвера кости',
    'category': 'Node',
}


class WrinkleMapPanel(bpy.types.Panel):
    bl_idname = f'VIEW3D_PT_{settings.NAME_DEV}'
    bl_category = settings.NAME_HEADER
    bl_label = settings.NAME_HEADER
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        props = context.scene.wrmap_props
        layout = self.layout

        if not(context.object and context.object.type == 'ARMATURE'):
            layout.label(text='Выделите арматуру', icon='ERROR')
            return

        if context.mode != 'POSE':
            layout.label(text='Войдите в Pose Mode', icon='ERROR')
            return

        if not context.selected_pose_bones:
            layout.label(text='Выделите кость(и)', icon='ERROR')
            return

        # Выбор текстуры
        layout.prop(props, 'wrinkle_texture', text='Wrinkle Texture')

        # breakpoint()
        if not props.mesh_object:
            layout.label(text='К арматуре не привязан ни один Mesh', icon='ERROR')
            return

        # Выбор объекта
        layout.prop(props, 'mesh_object', icon='OBJECT_DATA')

        if not props.shape_key:
            layout.label(text='У Mesh`а нету Shape Key', icon='ERROR')
        else:
            # Выбор Shape Key
            layout.prop(props, 'shape_key', icon='SHAPEKEY_DATA')

        # Настройка драйвера
        layout.prop(props, 'bone_transform', icon='DRIVER')

        # Кнопка оператора
        layout.operator(AddWrinkleMapOperator.bl_idname)


classes = (
    WrinkleMapPanel,
    AddWrinkleMapOperator,
    WrinkleMapProperties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.wrmap_props = bpy.props.PointerProperty(type=WrinkleMapProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.wrmap_props
