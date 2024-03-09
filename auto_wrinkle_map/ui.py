import os

import bpy
from bpy.utils import previews

from .opers import (
    AddWrinkleMapOperator,
    RemoveWrinkleMapOperator,
    get_wrinkle_node_tree,
)
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

    def draw(self, context):
        sc_props = context.scene.wrmap_props
        layout = self.layout

        img_node = sc_props.node_tree.nodes.get('Image Texture')

        layout.prop(sc_props, 'name')
        box = layout.box()
        # breakpoint()
        box.template_image(
            img_node, 'image',
            img_node.image_user,
            # compact=True
        )
        # box.prop(img_node, 'image')
        layout.prop(sc_props, 'material')
        layout.prop(sc_props, 'armature')
        layout.prop(sc_props, 'bone', icon='BONE_DATA')

        # Настройка драйвера
        layout.prop(sc_props, 'bone_transform', icon='DRIVER')
        layout.prop(sc_props, 'shape_key', icon='SHAPEKEY_DATA')

        # Кнопка оператора
        layout.operator(AddWrinkleMapOperator.bl_idname)
        layout.separator(factor=3)

        for wr in context.object.wrinkles:
            row = layout.row()
            col1, col2 = row.column(align=True), row.column(align=True)
            col1.prop(wr, 'expand', text='',
                     icon='TRIA_DOWN' if wr.expand else 'TRIA_RIGHT')
            col1.operator(RemoveWrinkleMapOperator.bl_idname, text='', icon='PANEL_CLOSE')
            if wr.expand:
                self.draw_wrinkle(col2.box(), wr)
            else:
                col2.box().label(text=wr.name)

    def draw_wrinkle(self, layout, ob_props):
        layout.prop(ob_props, 'name')
        img_node = ob_props.node_tree.nodes.get('Image Texture')
        layout.template_image(img_node, 'image',
                              img_node.image_user)
        layout.prop(ob_props, 'material')
        layout.prop(ob_props, 'armature')
        layout.prop(ob_props, 'bone')
        layout.prop(ob_props, 'bone_transform')
        layout.prop(ob_props, 'shape_key')
