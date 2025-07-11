# pyright: reportMissingModuleSource=false

import bpy
from bpy.props import IntProperty
from bpy.types import (
    Operator,
)

from .scene_props import WrinklePropsScene
from .utils import (
    InfoMsg,
    add_node_groups,
    delete_node_groups,
    get_wrinkle_node_tree,
    set_node_group_driver,
)


class AddWrinkleMapOperator(Operator):
    """Add driver and node group"""
    bl_idname = 'wrmap.add_wrinkle_map'
    bl_label = 'Add Wrinkle Map'

    @classmethod
    def poll(cls, context):
        scene_props = context.scene.wrmap_props  # pyright: ignore
        return not any(
            (
                scene_props.image is None,
                scene_props.material is None,
                scene_props.armature is None,
                scene_props.bone in (None, ''),
                scene_props.bone_transform is None,
                scene_props.shape_key in (None, ''),
            )
        )

    def check_props(self, obj):
        sc_props: WrinklePropsScene = getattr(bpy.context.scene, 'wrmap_props')

        for ob_props in obj.wrinkles:
            if ob_props.bone == sc_props.bone:
                self.log.error('This bone is used')
                return False
        return True

    def execute(self, context):
        print('WrinkleMapOperator executed')
        self.log = InfoMsg(self)
        sc_props = context.scene.wrmap_props  # pyright: ignore

        mesh_obj = context.object  # pyright: ignore
        if not self.check_props(mesh_obj):
            return {'CANCELLED'}

        # Copy properties to the object
        ob_props = mesh_obj.wrinkles.add()
        ob_props.node_tree = get_wrinkle_node_tree().copy()

        ob_props.name = sc_props.name
        ob_props.armature = sc_props.armature
        ob_props.shape_key = sc_props.shape_key
        ob_props.bone = sc_props.bone
        ob_props.bone_transform = sc_props.bone_transform
        ob_props.material = sc_props.material
        ob_props.bone_transform = sc_props.bone_transform

        # Tree setup
        ob_props.node_tree.name = ob_props.name

        # Image setup
        img_node = ob_props.node_tree.nodes['Image Texture']  # pyright: ignore

        img_node.image = sc_props.image
        img_node.image.colorspace_settings.name = 'Non-Color'

        # Shape Key driver setup
        shape_key_block = mesh_obj.data.shape_keys.key_blocks.get(ob_props.shape_key)
        fcur = shape_key_block.driver_add('value')
        fcur.driver.type = 'SCRIPTED'

        var = fcur.driver.variables.new()

        fcur.driver.expression = f'{var.name} + 0.0'
        var.type = 'TRANSFORMS'

        targ = var.targets[0]
        targ.id = ob_props.armature
        targ.bone_target = ob_props.bone
        targ.transform_type = ob_props.bone_transform
        targ.transform_space = 'LOCAL_SPACE'

        # Material setup
        for gr in add_node_groups(ob_props.material, ob_props.node_tree):
            set_node_group_driver(gr, ob_props)

        return {'FINISHED'}


class RemoveWrinkleMapOperator(Operator):
    """Remove drivers and node group"""
    bl_idname = 'wrmap.remove_wrinkle_map'
    bl_label = 'Remove Wrinkle Map'

    ob_prop_i: IntProperty()  # pyright: ignore

    def execute(self, context):
        frame = context.scene.frame_current
        context.scene.frame_set(0)

        ob_prop = context.object.wrinkles[self.ob_prop_i]  # pyright: ignore
        mesh_obj = context.object  # pyright: ignore

        shape_key_block = mesh_obj.data.shape_keys.key_blocks.get(ob_prop.shape_key)
        shape_key_block.driver_remove('value')

        delete_node_groups(ob_prop.material, ob_prop.node_tree)

        if ob_prop.node_tree.users < 1:
            bpy.data.node_groups.remove(ob_prop.node_tree)  # pyright: ignore

        context.object.wrinkles.remove(self.ob_prop_i)  # pyright: ignore
        context.scene.frame_set(frame)
        return {'FINISHED'}
