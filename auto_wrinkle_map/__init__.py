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
        layout = self.layout

        if context.object.type != 'ARMATURE':
            layout.label(text='Выделите арматуру')
            return

        if context.mode != 'POSE':
            layout.label(text='Войдите в Pose Mode')
            return

        if not context.selected_pose_bones:
            layout.label(text='Выделите кость(и)')

        layout.template_ID_preview()


        layout.operator(AddWrinkleMapOperator.bl_idname)


classes = (
    WrinkleMapPanel,
    AddWrinkleMapOperator,
    WrinkleMapProperties
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.wrmap_props = bpy.props.PointerProperty(type=WrinkleMapProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.wrmap_props
