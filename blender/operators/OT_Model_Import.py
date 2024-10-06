import bpy

from bpy.types import Operator
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        CollectionProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

from ..utils.ImportModel import *

class ACLR_OT_Model_Import(Operator, ImportHelper):
        bl_idname = "import_scene.import_aclr_model"
        bl_label = "Import ACLR model"

        # Selected files
        files: CollectionProperty(type=bpy.types.PropertyGroup)

        clear_scene: BoolProperty(
                name="Clear scene",
                description="Clear everything from the scene",
                default=False,
        )

        def execute(self, context):   
                importModel(self.filepath, self.files, self.clear_scene)

                return {'FINISHED'}
