import math
from types import SimpleNamespace

import bpy
from bpy.types import (
    Operator,
    ShaderNodeGroup,
)
from bpy.props import PointerProperty

from .object_props import WrinklePropsObject
from .settings import settings
from .utils import get_wrinkle_node_tree, get_connected_nodes, nodes_bounds


class AddWrinkleMapOperator(Operator):
    """Добавить shape key драйвер"""
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
        for ob_props in obj.wrinkles:
            ob_img_node = ob_props.node_tree.nodes.get('Image Texture')
            if ob_props.bone == sc_props.bone:
                self.report({'ERROR'}, 'This bone is used')
                return False
        # TODO доделать сравнение
        return True

    def execute(self, context):
        print('WrinkleMapOperator executed')

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
        mat = ob_props.material
        if not mat.use_nodes:
            self.report({'WARNING'}, f'Material {mat.name} not using nodes')

        ## Находим Material Output и относительно него ищем куда воткнуть группу
        roots = (m_n for m_n in mat.node_tree.nodes if m_n.type == 'OUTPUT_MATERIAL')

        surface_nodes = get_connected_nodes(roots, 'Surface', 'inputs')
        normal_nodes = get_connected_nodes(surface_nodes, 'Normal', 'inputs')

        range_x, range_y = nodes_bounds(mat.node_tree.nodes)

        for normal_node in normal_nodes:
            gr = mat.node_tree.nodes.new(ShaderNodeGroup.__name__)
            gr.node_tree = ob_props.node_tree

            normal_col_sock = normal_node.inputs.get('Color')
            if normal_col_sock.links:
                link = normal_col_sock.links[0]
                col_sock_A = link.from_socket
                mat.node_tree.links.remove(link)

                mat.node_tree.links.new(gr.inputs['A'], col_sock_A)

            mat.node_tree.links.new(normal_col_sock, gr.outputs['Result'])

            # Размещаем группу визуально
            gr.location.y = range_y[0]
            gr.location.x = normal_node.location.x - gr.width - settings.INDENT

            # Node group драйвер
            fcur = gr.inputs['Factor'].driver_add('default_value')
            fcur.driver.type = 'SCRIPTED'

            var = fcur.driver.variables.new()

            fcur.driver.expression = f'{var.name} + 0.0'
            var.type = 'TRANSFORMS'

            targ = var.targets[0]
            targ.id = ob_props.armature
            targ.bone_target = ob_props.bone
            targ.transform_type = ob_props.bone_transform
            targ.transform_space = 'LOCAL_SPACE'

        return {'FINISHED'}


class RemoveWrinkleMapOperator(Operator):
    """Добавить shape key драйвер"""
    bl_idname = 'wrmap.remove_wrinkle_map'
    bl_label = 'Remove Wrinkle Map'

    ob_prop = PointerProperty(type=WrinklePropsObject)

    def execute(self, context): ...
