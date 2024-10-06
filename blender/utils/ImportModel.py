import bpy
import bmesh
import os

from ...formats.aclr import *
from ...utilities import *

def buildMesh(model):

    mesh = bpy.data.meshes.new("test")
    obj = bpy.data.objects.new("test", mesh)

    sceneCollection = bpy.context.scene.collection  # Get the default collection
    sceneCollection.objects.link(obj)

    bm = bmesh.new()
    bm.from_mesh(mesh)

    vertexList = {}

    for subMesh in model.mesh.subMeshes:

        vertexIndex = 0

        for vertexBuffer in subMesh.vertexBuffers:

            # # Set vertices
            for j in range(len(vertexBuffer.buffer["positions"])):
                vertex = bm.verts.new(vertexBuffer.buffer["positions"][j])
                
                vertex.index = vertexIndex
                
                vertexList[vertexIndex] = vertex 

        vertexIndex += len(vertexBuffer.buffer["positions"])

    bm.to_mesh(mesh)
    bm.free()

def importModel(filepath, files, clearScene):
    
    if clearScene == True:
        clear_scene()

    folder = (os.path.dirname(filepath))

    for i, j in enumerate(files):

        path_to_file = (os.path.join(folder, j.name))

        model = ACLR()
        model.read(path_to_file)

        buildMesh(model)

        head = os.path.split(path_to_file)[0]

    return {'FINISHED'}