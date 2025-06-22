import os

import bpy
from bpy.utils import previews

from .opers import (
    AddWrinkleMapOperator,
    RemoveWrinkleMapOperator,
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
        layout.template_ID(img_node, 'image', new='image.new', open='image.open')
        layout.prop(sc_props, 'material')
        layout.prop(sc_props, 'armature')
        layout.prop(sc_props, 'bone', icon='BONE_DATA')

        # Настройка драйвера
        layout.prop(sc_props, 'bone_transform', icon='DRIVER')
        layout.prop(sc_props, 'shape_key', icon='SHAPEKEY_DATA')

        # Кнопка оператора
        layout.operator(AddWrinkleMapOperator.bl_idname)

        if context.object.wrinkles:
            layout.separator(factor=2)
            layout.label(text='Wrinkle Maps:')
        for i, wr in enumerate(context.object.wrinkles):
            row = layout.box().row()
            col1, col2 = row.column(align=True), row.column(align=True)
            col1.prop(
                wr, 'expand', text='', icon='TRIA_DOWN' if wr.expand else 'TRIA_RIGHT'
            )
            col1.operator(
                RemoveWrinkleMapOperator.bl_idname, text='', icon='PANEL_CLOSE'
            ).ob_prop_i = i  # pyright: ignore
            if not wr.expand:
                col2.box().label(text=wr.name)
                continue

            box = col2
            box.prop(wr, 'name')
            img_node = wr.node_tree.nodes.get('Image Texture')
            box.template_ID(img_node, 'image', new='image.new', open='image.open')
            box.prop(wr, 'material')
            box.prop(wr, 'armature')
            box.prop(wr, 'bone')
            box.prop(wr, 'bone_transform')
            box.prop(wr, 'shape_key')
