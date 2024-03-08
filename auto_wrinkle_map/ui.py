import os

import bpy
from bpy.utils import previews

from .opers import AddWrinkleMapOperator, get_wrinkle_node_tree
from .settings import settings

icons_path = os.path.join(os.path.dirname(__file__), 'icons')
ICONS = previews.new()
ICONS.load('wrinkle', os.path.join(icons_path, 'wrinkle_icon.png'), 'IMAGE')
# breakpoint()


class WrinkleMapPanel(bpy.types.Panel):
    bl_idname = f'VIEW3D_PT_{settings.NAME_DEV}'
    bl_category = settings.NAME_HEADER
    bl_label = settings.NAME_HEADER
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw_wrinkle(self, layout, ob_props):
        context = bpy.context
        layout.prop(ob_props, 'name')
        layout.template_image(ob_props, "wrinkle_texture",
                              self.img_node.image_user, compact=True)

        layout.prop(ob_props, 'armature')
        layout.prop(ob_props, 'bone')
        layout.prop(ob_props, 'shape_key')

    def draw(self, context):
        sc_props = context.scene.wrmap_props
        layout = self.layout

        img_node = sc_props.node_tree.nodes.get('Image Texture')

        layout.prop(sc_props, 'name')
        box = layout.box()
        # breakpoint()
        box.template_image(img_node, 'image', img_node.image_user)
        layout.prop(sc_props, 'material')

        arm = context.object.parent
        if not (arm and arm.type == 'ARMATURE'):
            layout.label(text='Объект не привязан к арматуре', icon='ERROR')
        else:
            layout.prop(sc_props, 'armature')
            layout.prop(sc_props, 'bone', icon='BONE_DATA')

        layout.prop(sc_props, 'shape_key', icon='SHAPEKEY_DATA')
        # Настройка драйвера
        layout.prop(sc_props, 'bone_transform', icon='DRIVER')
        # Кнопка оператора
        layout.operator(AddWrinkleMapOperator.bl_idname)

        for wr in context.object.wrinkles:
            self.draw_wrinkle(layout, wr)
