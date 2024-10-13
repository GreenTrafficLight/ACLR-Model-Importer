import mathutils

from ..utilities import *

from enum import Enum

class NodeType:
    LOD0 = 0x3
    LOD1 = 0x4
    LOD2 = 0x5
    Mesh0x7 = 0x7
    Mesh0xB = 0xB
    Mesh0xC = 0xC

class Header:

    def __init__(self) -> None:
        self.pointerCount = 0
        self.offsets = []
        self.sizes = []
        self.nodeTypes = []

    def read(self, br):
        self.fileSize = br.readUInt()
        unk0x4 = br.readUShort()
        unk0x6 = br.readUShort()
        unk0x8 = br.readBytes(4)
        br.seek(0x30)
        self.pointersOffset = br.readUInt()
        br.seek(self.pointersOffset)
        unkSize0x80 = br.readUInt()
        unk0x84 = br.readUByte()
        unk0x85 = br.readUByte()
        self.pointerCount = br.readUShort()
        skipZeros = 96 - self.pointerCount * 4
        for pointer in range(self.pointerCount):
            self.offsets.append(self.pointersOffset + br.readUInt())
        br.seek(skipZeros, 1)
        for size in range(self.pointerCount):
            self.sizes.append(br.readUInt())
        br.seek(skipZeros, 1)
        for nodeType in range(self.pointerCount):
            self.nodeTypes.append(br.readUByte())

class Material:

    def __init__(self, start) -> None:
        self.start = start
        self.name = ""

    def read(self, br, materialInformation):
        pass

class SubMesh:

    def __init__(self, startPos) -> None:
        self.startPos = startPos
        self.parentIndex = -1
        self.childIndex = -1
        self.siblingIndex = -1
        self.vertexBuffers = []
        
    def read(self, br):
        self.translation = mathutils.Vector(br.readVector3f())
        br.readFloat()
        self.rotation = mathutils.Euler(br.readVector3f(), "XYZ")
        br.readFloat()
        self.scale = mathutils.Euler(br.readVector3f())
        br.readFloat()
        self.transformation = mathutils.Matrix.Translation(self.translation) @ self.rotation.to_matrix().to_4x4() @ mathutils.Matrix.Scale(1, 4, self.scale)
        unk0x30 = br.readShort()
        unk0x32 = br.readShort()
        self.parentIndex = br.readShort()
        self.childIndex = br.readShort()
        self.siblingIndex = br.readShort()
        unkCount0x3A = br.readUShort()
        unkOffset0x3C = self.startPos + br.readUInt() # Used for transformation
        vertexBufferCount = br.readUInt() # Vertex buffer count
        subMeshOffset = self.startPos + br.readUInt()
        unk0x48 = br.readUShort()
        unk0x4A = br.readUShort()
        unkOffset0x4C = self.startPos + br.readUInt() # Used for transformation
        unkOffset0x50 = self.startPos + br.readUInt()
        unk0x54 = br.readUInt()
        unkSize0x58 = br.readUInt()
        unk0x5A = br.readUInt()

        savePos = br.tell()

        br.seek(subMeshOffset)
        for i in range(vertexBufferCount):
            vertexBuffer = VertexBuffer(self.startPos)
            vertexBuffer.read(br)
            self.vertexBuffers.append(vertexBuffer)

        br.seek(savePos)

class VertexBuffer:

    def __init__(self, startPos) -> None:
        self.startPos = startPos
        self.buffer = {"positions": [], "flags":[], "normals":[], "uvs":[], "colors": []}

    def read(self, br):
        unk0x0 = br.readUShort()
        unk0x2 = br.readUByte()
        vertexCount = br.readUByte()
        vertexBufferOffset = self.startPos + br.readUInt()
        vertexBufferEnd = self.startPos + br.readUInt()
        positionBufferOffset = self.startPos + br.readUInt()
        unkBufferOffset0x10 = self.startPos + br.readUInt()
        unkBufferOffset0x14 = self.startPos + br.readUInt()
        colorBufferOffset = self.startPos + br.readUInt()

        for i in range(vertexCount):
            br.seek(positionBufferOffset + i * 8)
            self.buffer["positions"].append(mathutils.Vector((br.readShort() / 32767, br.readShort() / 32767, br.readShort() / 32767)))
            self.buffer["flags"].append(br.readUShort())
            br.seek(unkBufferOffset0x10  + i * 3)
            self.buffer["normals"].append([br.readByte() / 127, br.readByte() / 127, br.readByte() / 127])
            br.seek(unkBufferOffset0x14 + i * 4)
            self.buffer["uvs"].append([br.readShort() / 32767, br.readShort() / 32767])
            br.seek(colorBufferOffset  + i * 4)
            self.buffer["colors"].append([br.readUByte() / 255, br.readUByte() / 255, br.readUByte() / 255, br.readUByte() / 255])

        br.seek(vertexBufferEnd)

class Mesh:

    def __init__(self, br) -> None:
        self.startPos = br.tell()
        self.materials = []
        self.subMeshes = []

    def read(self, br):
        unk0x0 = br.readUInt()
        meshHeaderSize = br.readUInt()
        meshDataSize = br.readUInt()
        materialCount = br.readUShort()
        unkCount0xE = br.readUShort()
        unkCount0x10 = br.readUShort()
        unkCount0x12 = br.readUShort()
        unkOffset0x14 = self.startPos + br.readUInt() # used for materials
        unkOffset0x18 = self.startPos + br.readUInt() # used for transformation
        unkOffset0x1C = self.startPos + br.readUInt()
       
        # br.seek(self.startPos + meshHeaderSize + 0x30)
        # materialInformations = []
        # for i in range(materialCount):
        #     materialInformation = {"nameOffset" : self.startPos + br.readUInt(), "unkOffset0x4" : self.startPos + br.readUInt(), "unkOffset0x8" : self.startPos + br.readUInt()}
        #     br.seek(4, 1) # zeros ?
        #     materialInformations.append(materialInformation)

        br.seek(unkOffset0x1C)
        for i in range(unkCount0x12):
            subMesh = SubMesh(self.startPos)
            subMesh.read(br)
            self.subMeshes.append(subMesh)


class ACLR:

    def __init__(self) -> None:
        self.header = None
        self.meshes = []

    def read(self, filepath):
        file = open(filepath, "rb")
        br = BinaryReader(file)

        self.header = Header()
        self.header.read(br)

        for i in range(self.header.pointerCount):
            nodeType = self.header.nodeTypes[i]
            if nodeType == NodeType.LOD0 or nodeType == NodeType.LOD1 or nodeType == NodeType.LOD2 or nodeType == NodeType.Mesh0x7 or nodeType == NodeType.Mesh0xB or nodeType == NodeType.Mesh0xC:
                br.seek(self.header.offsets[i])
                mesh = Mesh(br)
                mesh.read(br)
                self.meshes.append(mesh)

        print("Finished")

