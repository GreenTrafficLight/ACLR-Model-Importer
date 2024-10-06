from ..utilities import *

class Header:

    def __init__(self) -> None:
        self.offsets = []
        self.sizes = []

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
        pointerCount = br.readUShort()
        skipZeros = 96 - pointerCount * 4
        for pointer in range(pointerCount):
            self.offsets.append(self.pointersOffset + br.readUInt())
        br.seek(skipZeros, 1)
        for size in range(pointerCount):
            self.sizes.append(br.readUInt())

class Material:

    def __init__(self, start) -> None:
        self.start = start
        self.name = ""

    def read(self, br, materialInformation):
        pass

class SubMeshHeader:

    def __init__(self, startPos) -> None:
        self.startPos = startPos
        
    def read(self, br, subMeshes):
        br.seek(48, 1)
        unk0x30 = br.readShort()
        unk0x32 = br.readShort()
        unk0x34 = br.readShort()
        unk0x36 = br.readShort()
        unk0x38 = br.readShort()
        unkCount0x3A = br.readUShort()
        unkOffset0x3C = self.startPos + br.readUInt()
        vertexBufferCount = br.readUInt() # Vertex buffer count
        unkOffset0x44 = self.startPos + br.readUInt()
        unk0x48 = br.readUShort()
        unk0x4A = br.readUShort()
        unkOffset0x4C = self.startPos + br.readUInt()
        unkOffset0x50 = self.startPos + br.readUInt()
        unk0x54 = br.readUInt()
        unkSize0x58 = br.readUInt()
        unk0x5A = br.readUInt()

        savePos = br.tell()

        br.seek(unkOffset0x44)
        subMesh = SubMesh(self.startPos)
        subMesh.read(br, vertexBufferCount)
        subMeshes.append(subMesh)

        br.seek(savePos)

class SubMesh:
    def __init__(self, startPos) -> None:
        self.startPos = startPos
        self.vertexBuffers = []
        
    def read(self, br, vertexBufferCount):
        br.readUShort()
        br.readUByte()
        br.readUByte()
        unkOffset0x4 = self.startPos + br.readUInt()
        unkOffset0x8 = self.startPos + br.readUInt() # Vertex Buffer Offset ?
        unkOffset0xC = self.startPos + br.readUInt()
        unkOffset0x10 = self.startPos + br.readUInt()
        unkOffset0x14 = self.startPos + br.readUInt()
        unkOffset0x18 = self.startPos + br.readUInt()

        br.seek(unkOffset0x8)
        for i in range(vertexBufferCount - 1):
            print(br.tell())
            vertexBuffer = VertexBuffer(self.startPos)
            vertexBuffer.read(br)
            self.vertexBuffers.append(vertexBuffer)

class VertexBuffer:

    def __init__(self, startPos) -> None:
        self.startPos = startPos
        self.buffer = {"positions": [], "flags":[], "colors": []}

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
            self.buffer["positions"].append([br.readShort() / 32767, br.readShort() / 32767, br.readShort() / 32767])
            self.buffer["flags"].append(br.readUShort())
            br.seek(unkBufferOffset0x10  + i * 3)
            br.seek(unkBufferOffset0x14)
            br.seek(colorBufferOffset  + i * 4)
            self.buffer["colors"].append([br.readUByte(), br.readUByte(), br.readUByte(), br.readUByte()])


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
        unkOffset0x14 = self.startPos + br.readUInt()
        unkOffset0x18 = self.startPos + br.readUInt()
        unkOffset0x1C = self.startPos + br.readUInt()
       
        # br.seek(self.startPos + meshHeaderSize + 0x30)
        # materialInformations = []
        # for i in range(materialCount):
        #     materialInformation = {"nameOffset" : self.startPos + br.readUInt(), "unkOffset0x4" : self.startPos + br.readUInt(), "unkOffset0x8" : self.startPos + br.readUInt()}
        #     br.seek(4, 1) # zeros ?
        #     materialInformations.append(materialInformation)

        br.seek(unkOffset0x1C)
        for i in range(unkCount0x12):
            subMeshHeader = SubMeshHeader(self.startPos)
            subMeshHeader.read(br, self.subMeshes)


class ACLR:

    def __init__(self) -> None:
        self.header = None
        self.mesh = None

    def read(self, filepath):
        file = open(filepath, "rb")
        br = BinaryReader(file)

        self.header = Header()
        self.header.read(br)

        # Mesh data
        br.seek(self.header.offsets[4])
        self.mesh = Mesh(br)
        self.mesh.read(br)

        print("Finished")

