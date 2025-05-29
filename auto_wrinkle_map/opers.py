import bpy
from bpy.types import (
    Operator,
    ShaderNodeGroup,
)
from bpy.props import IntProperty

from .utils import (
    InfoMsg,
    get_wrinkle_node_tree,
    delete_node_groups,
    add_node_groups, set_node_group_driver,
)


class AddWrinkleMapOperator(Operator):
    """Add driver and node group"""
    bl_idname = 'wrmap.add_wrinkle_map'
    bl_label = 'Add Wrinkle Map'

    @classmethod
    def poll(cls, context):
        sc_props = context.scene.wrmap_props

        return all((
            sc_props.material,
            sc_props.armature,
            sc_props.bone,
            sc_props.bone_transform,
            sc_props.shape_key,
        ))

    def check_props(self, obj):
        sc_props = bpy.context.scene.wrmap_props
        sc_img_node = sc_props.node_tree.nodes.get('Image Texture')
        if not sc_img_node.image:
            self.log.error('Texture is not selected!')
            return False

        for ob_props in obj.wrinkles:
            ob_img_node = ob_props.node_tree.nodes.get('Image Texture')
            if ob_props.bone == sc_props.bone:
                self.log.error('This bone is used')
                return False
        return True

    def execute(self, context):
        print('WrinkleMapOperator executed')
        self.log = InfoMsg(self)
        sc_props = context.scene.wrmap_props

        mesh_obj = context.object
        if not self.check_props(mesh_obj):
            return {'CANCELLED'}

        # breakpoint()
        #### Копируем свойства в объект
        ob_props = mesh_obj.wrinkles.add()
        ob_props.node_tree = get_wrinkle_node_tree()
        ob_props.name = sc_props.name
        ob_props.armature = sc_props.armature
        ob_props.shape_key = sc_props.shape_key
        ob_props.bone = sc_props.bone
        ob_props.bone_transform = sc_props.bone_transform
        ob_props.material = sc_props.material
        ob_props.bone_transform = sc_props.bone_transform

        # Настройка дерева
        ob_props.node_tree.name = ob_props.name

        # Настройка изображения
        ob_props.node_tree.nodes['Image Texture'].image.colorspace_settings.name\
            = 'Non-Color'

        ##### Shape Key драйвер
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

        ##### Материал
        for gr in add_node_groups(ob_props.material, ob_props.node_tree):
            set_node_group_driver(gr, ob_props)

        return {'FINISHED'}


class RemoveWrinkleMapOperator(Operator):
    """Remove drivers"""
    bl_idname = 'wrmap.remove_wrinkle_map'
    bl_label = 'Remove Wrinkle Map'

    ob_prop_i: IntProperty()

    def execute(self, context):
        frame = context.scene.frame_current
        context.scene.frame_set(0)

        ob_prop = context.object.wrinkles[self.ob_prop_i]
        mesh_obj = context.object

        shape_key_block = mesh_obj.data.shape_keys.key_blocks.get(ob_prop.shape_key)
        shape_key_block.driver_remove('value')

        delete_node_groups(ob_prop.material, ob_prop.node_tree)

        if ob_prop.node_tree.users < 1:
            bpy.data.node_groups.remove(ob_prop.node_tree)

        context.object.wrinkles.remove(self.ob_prop_i)
        context.scene.frame_set(frame)
        return {'FINISHED'}


class GenerateJsonOperator(Operator):
    """Generate operator"""
    bl_idname = 'wrmap.generate_json'
    bl_label = 'Generate JSON'

    def execute(self, context):
        return {'FINISHED'}

