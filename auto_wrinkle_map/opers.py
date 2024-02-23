import bpy


class AddWrinkleMapOperator(bpy.types.Operator):
    """Кнопка"""
    bl_idname = 'wrmap.add_wrinkle_map'
    bl_label = 'Add Wrinkle Map'


    def execute(self, context):
        print('WrinkleMapOperator executed')
