import math
from types import SimpleNamespace

import bpy
from bpy.types import (
    Operator,
    ShaderNode,
    ShaderNodeMix,
    ShaderNodeTexImage,
    ShaderNodeGroup,
    ShaderNodeTree,
    NodeSocketColor,
    NodeGroupInput,
    NodeGroupOutput,
    NodeSocketColor,
    NodeSocketFloat,
)

from .settings import settings
from .utils import get_wrinkle_node_tree


class AddWrinkleMapOperator(Operator):
    """Добавить shape key драйвер"""
    bl_idname = 'wrmap.add_wrinkle_map'
    bl_label = 'Add Wrinkle Map'

    @classmethod
    def poll(cls, context):
        return context.object.parent and context.object.parent.type == 'ARMATURE'

    def execute(self, context):
        print('WrinkleMapOperator executed')

        sc_props = context.scene.wrmap_props

        mesh_obj = context.object
        ob_wr_props = mesh_obj.wrinkles.new()
        breakpoint()
        arm_obj = sc_props.armature

        ##### Shape Key драйвер
        if sc_props.shape_key:
            shape_key_block = mesh_obj.data.shape_keys.key_blocks.get(sc_props.shape_key)
            fcur = shape_key_block.driver_add('value')
            fcur.driver.type = 'SCRIPTED'

            var = fcur.driver.variables.new()

            fcur.driver.expression = f'{var.name} + 0.0'
            var.type = 'TRANSFORMS'

            targ = var.targets[0]
            targ.id = arm_obj
            targ.bone_target = context.active_bone.name
            targ.transform_type = sc_props.bone_transform
            targ.transform_space = 'LOCAL_SPACE'

        ##### Материал

        # Проверка наличия материала
        if not mesh_obj.material_slots:
            self.report('ERROR', f'У {mesh_obj.name} нету материала')
            return {'CANCELLED'}

        mat = mesh_obj.material_slots[0].material

        if not mat.use_nodes:
            self.report('WARNING', f'Материал {mat.name} не использует ноды')

        ## Находим Material Output и относительно него ищем куда воткнуть группу
        roots = (m_n for m_n in mat.node_tree.nodes if m_n.type == 'OUTPUT_MATERIAL')

        surface_nodes = get_connected_nodes(roots, 'Surface', 'inputs')
        normal_nodes = get_connected_nodes(surface_nodes, 'Normal', 'inputs')

        range_x, range_y = nodes_bounds(mat.node_tree.nodes)

        tree = get_wrinkle_node_tree()
        for normal_node in normal_nodes:
            gr = mat.node_tree.nodes.new(ShaderNodeGroup.__name__)
            gr.node_tree = tree

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

            # Добавляем драйвер
            fcur = gr.inputs['Factor'].driver_add('default_value')
            fcur.driver.type = 'SCRIPTED'

            var = fcur.driver.variables.new()

            fcur.driver.expression = f'{var.name} + 0.0'
            var.type = 'TRANSFORMS'

            targ = var.targets[0]
            targ.id = arm_obj
            targ.bone_target = context.active_bone.name
            targ.transform_type = sc_props.bone_transform
            targ.transform_space = 'LOCAL_SPACE'

        return {'FINISHED'}
