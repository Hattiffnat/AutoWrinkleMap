import bpy


class AddWrinkleMapOperator(bpy.types.Operator):
    """Добавить shapekey драйвер"""
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

        ##### Настройка материала

        # Проверка наличия материала
        if not mesh_obj.material_slots:
            self.report('ERROR', f'У {mesh_obj.name} нету материала')
            return {'CANCELLED'}

        mat = mesh_obj.material_slots[0].material

        if not mat.use_nodes:
            self.report('WARNING', f'Материал {mat.name} не использует ноды')

        ### Парсинг нодового графа
        # Находим выходы
        roots = (m_n for m_n in mat.node_tree if m_n.type == 'OUTPUT_MATERIAL')

        # Находим ноды шейдеров
        shaders = ()

        return {'FINISHED'}
