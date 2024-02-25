import math
from typing import Iterable, Generator, Union, Literal

from mathutils import Vector
import bpy
from bpy.types import (
    ShaderNode,
    ShaderNodeMix,
    ShaderNodeTexImage,
    ShaderNodeGroup,
    ShaderNodeTree,
    NodeSocketColor,
    NodeGroupInput,
    NodeGroupOutput,
)


class AddWrinkleMapOperator(bpy.types.Operator):
    """Добавить shape key драйвер"""
    bl_idname = 'wrmap.add_wrinkle_map'
    bl_label = 'Add Wrinkle Map'

    def execute(self, context):
        print('WrinkleMapOperator executed')

        props = context.scene.wrmap_props

        arm_obj = context.object
        mesh_obj = context.scene.objects.get(props.mesh_object)

        ##### Shape Key драйвер
        if props.shape_key:
            shape_key_block = mesh_obj.data.shape_keys.key_blocks.get(props.shape_key)
            fcur = shape_key_block.driver_add('value')
            fcur.driver.type = 'SCRIPTED'

            var = fcur.driver.variables.new()

            fcur.driver.expression = f'{var.name} + 0.0'
            var.type = 'TRANSFORMS'

            targ = var.targets[0]
            targ.id = arm_obj
            targ.bone_target = context.active_bone.name
            targ.transform_type = props.bone_transform
            targ.transform_space = 'LOCAL_SPACE'

        ##### Материал

        # Проверка наличия материала
        if not mesh_obj.material_slots:
            self.report('ERROR', f'У {mesh_obj.name} нету материала')
            return {'CANCELLED'}

        mat = mesh_obj.material_slots[0].material

        if not mat.use_nodes:
            self.report('WARNING', f'Материал {mat.name} не использует ноды')

        ### Создаём группу
        gr = mat.node_tree.nodes.new(ShaderNodeGroup.__name__)
        gr_tree = bpy.data.node_groups.new('WrinkleMapGroup', ShaderNodeTree.__name__)
        gr.node_tree = gr_tree
        gr_input_node = gr_tree.nodes.new(NodeGroupInput.__name__)
        gr_output_node = gr_tree.nodes.new(NodeGroupOutput.__name__)

        ## Создаём Mix и Image Texture ноды
        mix_node = gr_tree.nodes.new(ShaderNodeMix.__name__)
        mix_node.data_type = 'RGBA'
        mix_node.inputs.get('Factor').default_value = 0

        img_node = gr_tree.nodes.new(ShaderNodeTexImage.__name__)
        img_node.image = props.wrinkle_texture

        # Соединяем Mix и Image Texture
        gr_tree.links.new(mix_node.inputs.get('B'), img_node.outputs.get('Color'))
        # Соединяем вход и выход группы
        gr_tree.links.new(mix_node.inputs.get('A'), gr_input_node.outputs[0])
        gr_tree.links.new(gr_output_node.inputs[0], mix_node.outputs[0])

        # Размещаем ноды визуально
        indent = 10

        gr_input_node.location.x = img_node.location.x - gr_input_node.width - indent
        gr_input_node.location.y = img_node.location.y + gr_input_node.height + indent

        mix_node.location.x = img_node.location.x + img_node.width + indent
        mix_node.location.y = img_node.location.y + mix_node.height + indent

        gr_output_node.location.x = mix_node.location.x + mix_node.width + indent
        gr_output_node.location.y = img_node.location.y

        # Находим Material Output и относительно него ищем куда воткнуть новую группу
        roots = (m_n for m_n in mat.node_tree if m_n.type == 'OUTPUT_MATERIAL')

        surface_nodes = get_connected_nodes(roots, 'Surface', 'inputs')
        normal_nodes = get_connected_nodes(surface_nodes, 'Normal', 'inputs')

        # Границы существующих нодов
        range_x, range_y = nodes_bounds(mat.node_tree.nodes)

        for normal_node in normal_nodes:
            ...

        return {'FINISHED'}


def nodes_bounds(nodes: Iterable[ShaderNode]) -> tuple[list[float], list[float]]:
    """Определяет границы прямоугольника в котором находятся ноды"""

    range_x = [math.inf, -math.inf]     # x_min, x_max
    range_y = [math.inf, -math.inf]     # y_min, y_max

    for node in nodes:
        if range_x[0] > node.location.x: range_x[0] = node.location.x
        if range_y[0] > node.location.y: range_y[0] = node.location.y

        node_right_border = node.location.x + node.width
        if range_x[1] < node_right_border: range_x[1] = node_right_border
        node_bottom_border = node.location.y + node.height
        if range_y[1] < node_bottom_border: range_y[1] = node_bottom_border

    return range_x, range_y


def get_connected_nodes(nodes: Union[ShaderNode, Iterable[ShaderNode]],
                        sockets_names: Union[str, Iterable[str]],
                        mode: Literal['inputs', 'outputs']) -> Generator:
    """Получить присоединенные ноды по имени сокета"""

    if isinstance(nodes, ShaderNode):
        nodes = (nodes,)

    if isinstance(sockets_names, str):
        sockets_names = (sockets_names,)
    else:
        sockets_names = tuple(sockets_names)

    for node in nodes:
        for socket in getattr(node, mode):
            if socket.name not in sockets_names: continue
            for link in socket.links:
                yield link.from_node if mode == 'inputs' else link.to_node
