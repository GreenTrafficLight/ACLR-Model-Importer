import bpy
import bmesh
import os

from ...formats.aclr import *
from ...utilities import *

def buildFaceList(subMesh):
    faces = []

    faceIndex = 0

    for vertexBuffer in subMesh.vertexBuffers:
        
        skip_ff_for_next_special = False

        for idx, value in enumerate(vertexBuffer.buffer["flags"]):
            if idx < 2:
                # First two items just get their indices
                faces.append(faceIndex)
                faceIndex += 1
            else:
                if value == 0x8000 or value == 0xA000:
                    if skip_ff_for_next_special:
                        # If we need to skip the 0xFF because the previous was 0xA0 or 0x80
                        skip_ff_for_next_special = False
                        faces.append(faceIndex)  # Add a number instead of 0xFF
                        faceIndex += 1
                    else:
                        faces.append(0xFFFF)  # Add 0xFF for 0x80 or 0xA0
                        faces.append(faceIndex)  # Add a number instead of 0xFF
                        faceIndex += 1
                        # Set the flag to skip the next special case if the next value is the counterpart
                        skip_ff_for_next_special = True
                else:
                    faces.append(faceIndex)  # Append current index
                    faceIndex += 1  # Increment index only when appending a number

        faces.append(0xFFFF)

    return StripToTriangle(faces)
            

def buildMesh(model):

    subMeshIndex = 0

    for subMesh in model.mesh.subMeshes:

        mesh = bpy.data.meshes.new("test" + str(subMeshIndex))
        obj = bpy.data.objects.new("test" + str(subMeshIndex), mesh)

        sceneCollection = bpy.context.scene.collection  # Get the default collection
        sceneCollection.objects.link(obj)

        bm = bmesh.new()
        bm.from_mesh(mesh)

        vertexList = {}
        facesList = []

        faces = buildFaceList(subMesh)

        vertexIndex = 0

        for vertexBuffer in subMesh.vertexBuffers:

            # # Set vertices
            for j in range(len(vertexBuffer.buffer["positions"])):
                vertex = bm.verts.new(vertexBuffer.buffer["positions"][j])
                
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

        subMeshIndex += 1

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