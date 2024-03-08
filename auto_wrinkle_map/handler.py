import bpy
from bpy.app.handlers import persistent

from .utils import get_wrinkle_node_tree


@persistent
def set_tree_handler(_):
    print('init handler...')
    sc_props = bpy.context.scene.wrmap_props
    sc_props.node_tree = get_wrinkle_node_tree()
    print('...ok')
