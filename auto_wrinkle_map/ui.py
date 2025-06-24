# pyright: reportMissingModuleSource=false

import os
from typing import Optional

import bpy
from bpy.types import Context, ImagePreview, Object
from bpy.utils import previews

from .operators import (
    AddWrinkleMapOperator,
    RemoveWrinkleMapOperator,
)
from .scene_props import WrinklePropsScene
from .settings import settings


class WrinkleMapPanel(bpy.types.Panel):
    bl_idname = f'VIEW3D_PT_{settings.EXTENSION_ID}'
    bl_category = settings.NAME_HEADER
    bl_label = settings.NAME_HEADER
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = set()

    preview_collection: previews.ImagePreviewCollection = previews.new()
    preview_collection.load(
        'wrinkle', os.path.join(settings.ICONS_PATH, 'wrinkle_icon.png'), 'IMAGE'
    )

    def draw(self, context: Context):
        sc_props: WrinklePropsScene = getattr(context.scene, 'wrmap_props')
        layout = self.layout

        obj: Optional[Object] = getattr(context, 'object')

        obj_is_good = True
        if obj is None:
            obj_is_good = False
        elif obj.type != 'MESH':
            obj_is_good = False
        elif obj.parent is None:
            obj_is_good = False
        elif obj.parent.type != 'ARMATURE':
            obj_is_good = False

        if not obj_is_good:
            layout.label(text='Select any Mesh object with Armature parent')
            return

        layout.prop(sc_props, 'name')
        layout.template_ID(sc_props, 'image', new='image.new', open='image.open')
        layout.prop(sc_props, 'material')

        layout.prop(sc_props, 'armature')
        layout.prop(sc_props, 'bone', icon='BONE_DATA')

        layout.prop(sc_props, 'bone_transform', icon='DRIVER')
        layout.prop(sc_props, 'shape_key', icon='SHAPEKEY_DATA')

        img_preview: ImagePreview = self.preview_collection['wrinkle']  # pyright: ignore
        layout.operator(
            AddWrinkleMapOperator.bl_idname,
            icon_value=img_preview.icon_id,
        )

        if (wrinkles := getattr(obj, 'wrinkles', None)) is None:
            return
        elif len(wrinkles) == 0:
            return

        layout.separator(factor=2)
        layout.label(text='Wrinkle Maps:')

        for i, wr in enumerate(wrinkles):
            row = layout.box().row()
            col1, col2 = row.column(align=True), row.column(align=True)
            col1.prop(
                wr, 'expand', text='', icon='TRIA_DOWN' if wr.expand else 'TRIA_RIGHT'
            )
            oper_props = col1.operator(
                RemoveWrinkleMapOperator.bl_idname, text='', icon='PANEL_CLOSE'
            )

            setattr(oper_props, 'ob_prop_i', i)

            if not wr.expand:
                col2.box().label(text=wr.name)
                continue

            box = col2.box()
            box.enabled = False

            box.prop(wr, 'name')
            img_node = wr.node_tree.nodes.get('Image Texture')
            box.template_ID(img_node, 'image', new='image.new', open='image.open')
            box.prop(wr, 'material')
            box.prop(wr, 'armature')
            box.prop(wr, 'bone')
            box.prop(wr, 'bone_transform')
            box.prop(wr, 'shape_key')
