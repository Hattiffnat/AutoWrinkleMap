import bpy
from bpy.app.handlers import persistent

from .utils import get_wrinkle_node_tree


@persistent
def set_tree_handler(_):
    sc_props = bpy.context.scene.wrmap_props
    if not sc_props.node_tree:
        sc_props.node_tree = get_wrinkle_node_tree()
    print('set_tree_handler ... ok!',)
