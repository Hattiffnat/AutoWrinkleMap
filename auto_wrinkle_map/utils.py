import math
from typing import Iterable, Generator, Union, Literal

import bpy
from bpy.types import (
    ShaderNode,
    ShaderNodeGroup,
    ShaderNodeMix,
    ShaderNodeTree,
    ShaderNodeTexImage,
    NodeSocketColor,
    NodeGroupInput,
    NodeGroupOutput,
    NodeSocketFloat,
)

from .settings import settings


BONE_TRANSFORMS = (
    ('LOC_X', 'Location X', ''),
    ('LOC_Y', 'Location Y', ''),
    ('LOC_Z', 'Location Z', ''),

    ('ROT_X', 'Rotation X', ''),
    ('ROT_Y', 'Rotation Y', ''),
    ('ROT_Z', 'Rotation Z', ''),
)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            print(f'cls: {cls} exemplar created: {cls._instances[cls]}')
        return cls._instances[cls]


class InfoMsg(metaclass=Singleton):
    _msgs = []

    def __init__(self, oper=None):
        self.oper = oper

    def report(self, lvl, *args, sep=' ', end='\n'):
        if self.oper:
            self.oper.report({lvl}, f'{sep.join(args)}{end}')
        else:
            print(f'{lvl}:', *args, sep=sep, end=end)

    def info(self, *args, **kwargs):
        self.report('INFO', *args, *kwargs)

    def warn(self, *args, **kwargs):
        self.report('WARNING', *args, *kwargs)

    def error(self, *args, **kwargs):
        self.report('ERROR', *args, *kwargs)


INFO = InfoMsg()


def create_node_tree():
    ### Создаём дерево
    gr_tree = bpy.data.node_groups.new('WrinkleMapGroup', ShaderNodeTree.__name__)
    gr_input_node = gr_tree.nodes.new(NodeGroupInput.__name__)
    gr_output_node = gr_tree.nodes.new(NodeGroupOutput.__name__)

    ## Создаём Mix и Image Texture ноды
    mix_node = gr_tree.nodes.new(ShaderNodeMix.__name__)
    mix_node.data_type = 'RGBA'
    mix_node.inputs.get('Factor').default_value = 0

    img_node = gr_tree.nodes.new(ShaderNodeTexImage.__name__)
    # img_node.image = sc_props.wrinkle_image

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
        if range_y[1] < node_top_border: range_y[1] = node_top_border

    return range_x, range_y


def get_connected_sockets(nodes: Union[ShaderNode, Iterable[ShaderNode]],
                          sockets_names: Union[str, Iterable[str]],
                          mode: Literal['inputs', 'outputs']) -> Generator:
    """Получить присоединенные сокеты"""

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
                yield link.from_socket if mode == 'inputs' else link.to_socket


def get_connected_nodes(nodes: Union[ShaderNode, Iterable[ShaderNode]],
                        sockets_names: Union[str, Iterable[str]],
                        mode: Literal['inputs', 'outputs']) -> Generator:
    """Получить присоединенные ноды по имени сокета"""

    for sock in get_connected_sockets(nodes, sockets_names, mode):
        yield sock.node


def add_node_groups(mat, node_tree):
    if not mat.use_nodes:
        INFO.warn(f'Material {mat.name} not using nodes')

    ## Находим Material Output и относительно него ищем куда воткнуть группу
    roots = (m_n for m_n in mat.node_tree.nodes if m_n.type == 'OUTPUT_MATERIAL')

    surface_nodes = get_connected_nodes(roots, 'Surface', 'inputs')
    normal_nodes = get_connected_nodes(surface_nodes,
                                       'Normal', 'inputs')

    range_x, range_y = nodes_bounds(mat.node_tree.nodes)

    for normal_node in normal_nodes:
        gr = mat.node_tree.nodes.new(ShaderNodeGroup.__name__)
        gr.node_tree = node_tree

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

        yield gr


def delete_node_groups(mat, node_tree):
    for node in mat.node_tree.nodes:
        if node.type != 'GROUP': continue
        if node.node_tree != node_tree: continue

        mixRes = normCol = None
        for sock in get_connected_sockets(node, 'A', 'inputs'):
            mixRes = sock
            break
        for sock in get_connected_sockets(node, 'Result', 'outputs'):
            normCol = sock
            break

        mat.node_tree.nodes.remove(node)

        if not (mixRes or normCol): continue
        mat.node_tree.links.new(normCol, mixRes)


def set_node_group_driver(gr, props):
    # Node group драйвер
    fcur = gr.inputs['Factor'].driver_add('default_value')
    fcur.driver.type = 'SCRIPTED'

    var = fcur.driver.variables.new()

    fcur.driver.expression = f'{var.name} + 0.0'
    var.type = 'TRANSFORMS'

    targ = var.targets[0]
    targ.id = props.armature
    targ.bone_target = props.bone
    targ.transform_type = props.bone_transform
    targ.transform_space = 'LOCAL_SPACE'
