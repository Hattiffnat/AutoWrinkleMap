# type: ignore
# pyright: reportMissingModuleSource=false, reportInvalidTypeForm=false

import math
from typing import Generator, Iterable, Literal, Optional, Union

import bpy
from bpy.types import ShaderNodeMix  # pyright: ignore
from bpy.types import (
    NodeGroupInput,
    NodeGroupOutput,
    NodeSocketColor,
    NodeSocketFloat,
    NodeTree,
    Operator,
    ShaderNode,
    ShaderNodeGroup,
    ShaderNodeTexImage,
    ShaderNodeTree,
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

        cls.__init__(cls._instances[cls], *args, **kwargs)
        return cls._instances[cls]


class InfoMsg(metaclass=Singleton):
    """Helper class for outputting message reports using an operator from anywhere in the code"""

    oper = None
    _msgs = []

    @classmethod
    def push_msg(cls, msg):
        cls._msgs.append(msg)

    @classmethod
    def drain_msgs(cls):
        yield from cls._msgs
        cls._msgs.clear()

    def __init__(self, oper: Optional[Operator] = None):
        if oper is not None:
            self.oper = oper
            for lvl, args, sep, end in self.drain_msgs():
                self.oper.report({lvl}, f'{sep.join(args)}{end}')

    def report(self, lvl, *args, sep=' ', end='\n'):
        if self.oper is not None:
            self.oper.report({lvl}, f'{sep.join(args)}{end}')
        else:
            self.push_msg((lvl, args, sep, end))
            print(f'{lvl}:', *args, sep=sep, end=end)

    def info(self, *args, **kwargs):
        self.report('INFO', *args, *kwargs)

    def warn(self, *args, **kwargs):
        self.report('WARNING', *args, *kwargs)

    def error(self, *args, **kwargs):
        self.report('ERROR', *args, *kwargs)


INFO = InfoMsg()


def get_wrinkle_node_tree() -> NodeTree:
    sc_props = getattr(bpy.context.scene, 'wrmap_props')
    if getattr(sc_props, 'node_tree', None) is None:
        sc_props.node_tree = __create_node_tree()
    return sc_props.node_tree


def __create_node_tree():
    # Create a tree
    gr_tree = bpy.data.node_groups.new('WrinkleMapGroup', ShaderNodeTree.__name__)
    gr_input_node = gr_tree.nodes.new(NodeGroupInput.__name__)
    gr_output_node = gr_tree.nodes.new(NodeGroupOutput.__name__)

    # Create Mix and Image Texture nodes
    mix_node = gr_tree.nodes.new(ShaderNodeMix.__name__)
    mix_node.data_type = 'RGBA'
    mix_node.inputs.get('Factor').default_value = 0

    img_node = gr_tree.nodes.new(ShaderNodeTexImage.__name__)

    # Connect Mix and Image Texture
    gr_tree.links.new(mix_node.inputs.get('B'), img_node.outputs.get('Color'))

    # Connect the input and output of the group
    inpA = gr_tree.interface.new_socket('A', in_out='INPUT')
    inpA.socket_type = NodeSocketColor.__name__
    outpResult = gr_tree.interface.new_socket('Result', in_out='OUTPUT')
    outpResult.socket_type = NodeSocketColor.__name__

    # Additional factor value input
    inpFactor = gr_tree.interface.new_socket('Factor', in_out='INPUT')
    inpFactor.socket_type = NodeSocketFloat.__name__

    gr_tree.links.new(mix_node.inputs['Factor'], gr_input_node.outputs['Factor'])

    gr_tree.links.new(mix_node.inputs['A'], gr_input_node.outputs['A'])
    gr_tree.links.new(gr_output_node.inputs['Result'], mix_node.outputs['Result'])

    # Place nodes visually without overlapping
    ind = settings.INDENT

    gr_input_node.location.x = img_node.location.x - gr_input_node.width - ind
    gr_input_node.location.y = img_node.location.y + gr_input_node.height + ind

    mix_node.location.x = img_node.location.x + img_node.width + ind
    mix_node.location.y = img_node.location.y + mix_node.height + ind

    gr_output_node.location.x = mix_node.location.x + mix_node.width + ind
    gr_output_node.location.y = img_node.location.y
    return gr_tree


def __nodes_bounds(nodes: Iterable[ShaderNode]) -> tuple[list[float], list[float]]:
    """Defines the boundaries of the rectangle in which the nodes are located"""
    range_x = [math.inf, -math.inf]  # x_min, x_max
    range_y = [math.inf, -math.inf]  # y_min, y_max

    for node in nodes:
        if range_x[0] > node.location.x:
            range_x[0] = node.location.x
        if range_y[0] > node.location.y:
            range_y[0] = node.location.y

        node_right_border = node.location.x + node.width
        if range_x[1] < node_right_border:
            range_x[1] = node_right_border
        node_top_border = node.location.y + node.height
        if range_y[1] < node_top_border:
            range_y[1] = node_top_border

    return range_x, range_y


def get_connected_sockets(
    nodes: Union[ShaderNode, Iterable[ShaderNode]],
    sockets_names: Union[str, Iterable[str]],
    mode: Literal['inputs', 'outputs'],
) -> Generator:
    """Get attached sockets"""
    if isinstance(nodes, ShaderNode):
        nodes = (nodes,)

    if isinstance(sockets_names, str):
        sockets_names = (sockets_names,)
    else:
        sockets_names = tuple(sockets_names)

    for node in nodes:
        for socket in getattr(node, mode):
            if socket.name not in sockets_names:
                continue
            for link in socket.links:
                yield link.from_socket if mode == 'inputs' else link.to_socket


def get_connected_nodes(
    nodes: Union[ShaderNode, Iterable[ShaderNode]],
    sockets_names: Union[str, Iterable[str]],
    mode: Literal['inputs', 'outputs'],
) -> Generator:
    """Get attached nodes by socket name"""
    for sock in get_connected_sockets(nodes, sockets_names, mode):
        yield sock.node


def add_node_groups(mat, node_tree):
    if not mat.use_nodes:
        INFO.warn(f'Material {mat.name} not using nodes')

    sc_props = bpy.context.scene.wrmap_props

    # Find the Material Output and look for where to insert the group relative to it
    roots = (m_n for m_n in mat.node_tree.nodes if m_n.type == 'OUTPUT_MATERIAL')

    surface_nodes = get_connected_nodes(roots, 'Surface', 'inputs')
    normal_nodes = get_connected_nodes(surface_nodes, 'Normal', 'inputs')

    range_x, range_y = __nodes_bounds(mat.node_tree.nodes)

    for normal_node in normal_nodes:
        gr = mat.node_tree.nodes.new(ShaderNodeGroup.__name__)
        gr.node_tree = node_tree
        gr.name = sc_props.name

        normal_col_sock = normal_node.inputs.get('Color')
        if normal_col_sock.links:
            link = normal_col_sock.links[0]
            col_sock_A = link.from_socket
            mat.node_tree.links.remove(link)

            mat.node_tree.links.new(gr.inputs['A'], col_sock_A)

        mat.node_tree.links.new(normal_col_sock, gr.outputs['Result'])

        # Place the group visually
        gr.location.y = range_y[0]
        gr.location.x = normal_node.location.x - gr.width - settings.INDENT

        yield gr


def delete_node_groups(mat, node_tree):
    for node in mat.node_tree.nodes:
        if node.type != 'GROUP':
            continue
        if node.node_tree != node_tree:
            continue

        mixRes = normCol = None
        for sock in get_connected_sockets(node, 'A', 'inputs'):
            mixRes = sock
            break
        for sock in get_connected_sockets(node, 'Result', 'outputs'):
            normCol = sock
            break

        mat.node_tree.nodes.remove(node)

        if not (mixRes or normCol):
            continue
        mat.node_tree.links.new(normCol, mixRes)


def set_node_group_driver(gr, props):
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
