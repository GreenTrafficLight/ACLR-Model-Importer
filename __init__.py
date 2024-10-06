import bpy

from .blender.operators.OT_Model_Import import *

bl_info = {
	"name": "Armored Core Last Raven Model Importer",
	"author": "GreenTrafficLight",
	"version": (1, 0),
	"blender": (4, 0, 0),
	"location": "File > Import-Export",
	"support": "COMMUNITY",
	"category": "Import-Export"}

classes = [
    ACLR_OT_Model_Import
]

def menu_func_import(self, context):
    self.layout.operator(ACLR_OT_Model_Import.bl_idname, text="Armored Core Last Raven")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
