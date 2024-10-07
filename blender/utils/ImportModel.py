import bpy
import bmesh
import os

import mathutils

from ...formats.aclr import *
from ...utilities import *

def buildFaceList(subMesh):
    faces = []

    faceIndex = 0

    for vertexBuffer in subMesh.vertexBuffers:
        
        skipFF = False

        for idx, value in enumerate(vertexBuffer.buffer["flags"]):
            if idx > 2:
                if value == 0x8000 or value == 0xA000:
                    if skipFF:
                        # If we need to skip the 0xFF because the previous was 0xA0 or 0x80
                        skipFF = False
                    else:
                        faces.append(0xFFFF)  # Add 0xFF for 0x80 or 0xA0
                        # Set the flag to skip the next special case if the next value is the counterpart
                        skipFF = True

            faces.append(faceIndex)  # Append current index
            faceIndex += 1  # Increment index only when appending a number

        faces.append(0xFFFF)

    return StripToTriangle(faces)
            

def buildMesh(mesh, meshIndex):

    subMeshIndex = 0

    for subMesh in mesh.subMeshes:

        mesh = bpy.data.meshes.new(str(meshIndex) + str(subMeshIndex))
        obj = bpy.data.objects.new(str(meshIndex) + str(subMeshIndex), mesh)

        sceneCollection = bpy.context.scene.collection  # Get the default collection
        sceneCollection.objects.link(obj)

        bm = bmesh.new()
        bm.from_mesh(mesh)

        vertexList = {}
        facesList = []
        normals = []

        faces = buildFaceList(subMesh)

        uv_layer = bm.loops.layers.uv.new()

        vertexIndex = 0

        for vertexBuffer in subMesh.vertexBuffers:

            # # Set vertices
            for j in range(len(vertexBuffer.buffer["positions"])): 
                #test = subMesh.header.transformation @ mathutils.Matrix.Translation(vertexBuffer.buffer["positions"][j])
                vertex = bm.verts.new(vertexBuffer.buffer["positions"][j])

                vertex.normal = vertexBuffer.buffer["normals"][j]
                normals.append(vertexBuffer.buffer["normals"][j])
                
                vertex.index = vertexIndex
                
                vertexList[vertexIndex] = vertex 

                vertexIndex += 1

        # Set faces
        for j in range(len(faces)):
            try:
                face = bm.faces.new([vertexList[faces[j][0]], vertexList[faces[j][1]], vertexList[faces[j][2]]])
                face.smooth = True
            except:
                for Face in facesList:
                    if set([vertexList[faces[j][0]], vertexList[faces[j][1]], vertexList[faces[j][2]]]) == set(Face[1]):
                        face = Face[0].copy(verts=False, edges=True)
                        face.normal_flip()
                        face.smooth = True
                        break
                    
            facesList.append([face, [vertexList[faces[j][0]], vertexList[faces[j][1]], vertexList[faces[j][2]]]])

        bm.to_mesh(mesh)
        bm.free()

        if normals != []:
            mesh.normals_split_custom_set_from_vertices(normals)

        subMeshIndex += 1

def importModel(filepath, files, clearScene):
    
    if clearScene == True:
        clear_scene()

    folder = (os.path.dirname(filepath))

    for i, j in enumerate(files):

        path_to_file = (os.path.join(folder, j.name))

        model = ACLR()
        model.read(path_to_file)

        meshIndex = 0
        for mesh in model.meshes:
            buildMesh(mesh, meshIndex)
            meshIndex += 1

        head = os.path.split(path_to_file)[0]

    return {'FINISHED'}