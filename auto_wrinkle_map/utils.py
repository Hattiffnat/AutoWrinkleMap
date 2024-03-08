from typing import Iterable, Generator, Union, Literal

import bpy
from bpy.types import (
    ShaderNode,
    ShaderNodeMix,
    ShaderNodeTree,
    ShaderNodeTexImage,
    NodeSocketColor,
    NodeGroupInput,
    NodeGroupOutput,
    NodeSocketColor,
    NodeSocketFloat,
)

from .settings import settings


def create_node_tree():
    sc_props = bpy.context.scene.wrmap_props

    ### Создаём дерево
    gr_tree = bpy.data.node_groups.new('WrinkleMapGroup', ShaderNodeTree.__name__)
    gr_input_node = gr_tree.nodes.new(NodeGroupInput.__name__)
    gr_output_node = gr_tree.nodes.new(NodeGroupOutput.__name__)

    ## Создаём Mix и Image Texture ноды
    mix_node = gr_tree.nodes.new(ShaderNodeMix.__name__)
    mix_node.data_type = 'RGBA'
    mix_node.inputs.get('Factor').default_value = 0

    img_node = gr_tree.nodes.new(ShaderNodeTexImage.__name__)
    img_node.image = sc_props.wrinkle_image

    # Соединяем Mix и Image Texture
    gr_tree.links.new(mix_node.inputs.get('B'), img_node.outputs.get('Color'))

    # Соединяем вход и выход группы
    inpA = gr_tree.interface.new_socket('A', in_out='INPUT')
    inpA.socket_type = NodeSocketColor.__name__
    outpResult = gr_tree.interface.new_socket('Result', in_out='OUTPUT')
    outpResult.socket_type = NodeSocketColor.__name__

    # Дополнительный вход значения фактора
    inpFactor = gr_tree.interface.new_socket('Factor', in_out='INPUT')
    inpFactor.socket_type = NodeSocketFloat.__name__

    gr_tree.links.new(mix_node.inputs['Factor'], gr_input_node.outputs['Factor'])

    gr_tree.links.new(mix_node.inputs['A'], gr_input_node.outputs['A'])
    gr_tree.links.new(gr_output_node.inputs['Result'], mix_node.outputs['Result'])

    # Размещаем ноды визуально
    ind = settings.INDENT

    gr_input_node.location.x = img_node.location.x - gr_input_node.width - ind
    gr_input_node.location.y = img_node.location.y + gr_input_node.height + ind

    mix_node.location.x = img_node.location.x + img_node.width + ind
    mix_node.location.y = img_node.location.y + mix_node.height + ind

    gr_output_node.location.x = mix_node.location.x + mix_node.width + ind
    gr_output_node.location.y = img_node.location.y

    return gr_tree


def get_wrinkle_node_tree():
    sc_props = bpy.context.scene.wrmap_props
    if not sc_props.node_tree:
        sc_props.node_tree = create_node_tree()
    return sc_props.node_tree.copy()


def nodes_bounds(nodes: Iterable[ShaderNode]) -> tuple[list[float], list[float]]:
    """Определяет границы прямоугольника в котором находятся ноды"""
    range_x = [math.inf, -math.inf]     # x_min, x_max
    range_y = [math.inf, -math.inf]     # y_min, y_max

    for node in nodes:
        if range_x[0] > node.location.x: range_x[0] = node.location.x
        if range_y[0] > node.location.y: range_y[0] = node.location.y

        node_right_border = node.location.x + node.width
        if range_x[1] < node_right_border: range_x[1] = node_right_border
        node_top_border = node.location.y + node.height
        if range_y[1] < node_top_border: range_y[1] = node_bottom_border

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
