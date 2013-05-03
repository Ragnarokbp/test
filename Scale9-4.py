import os, struct, sys
from xml.dom import minidom
import Image
#import shutil

g_heightmapSize = 53
g_blendTexSize = 128
#g_posCenter = []
#g_posRange = []

def isChunkInDirectories(x, y, posCenter):
    if (abs(x - posCenter[0]) < 16 and abs(y - posCenter[1]) < 16):
        return False
    return True

# Input: @fileDir "03_yhj/0000ffffo"
# Output: "03_yhj/000xfffx/sep/0000ffffo"
def GetChunkDirectory(fileDir):
    # 000ffff0o
    fileName = fileDir.split('/')[1]
    #print fileName
    # 000xfffx
    dirName = fileName[:3] + 'x' + fileName[4:7] + 'x'
    #print dirName
    # 000xfffx/sep/0000ffffo
    dirName += '/sep/' + fileName
    # 03_yhj/000xfffx/sep/0000ffffo
    return fileDir.split('/')[0] + '/' + dirName


# Extract / Create .cdata file
MAGIC = '\x65\x4e\xa1\x42' # binary section magic number

def pad(size, padding = 4):
    return ((padding-size)%padding)

def extract(fname, dirname):

    f = open(fname, 'rb')
    assert MAGIC == f.read(4)

    # read indeices size
    f.seek(-4, os.SEEK_END)
    index_size = struct.unpack('L', f.read(4))[0]
    assert((index_size % 4) == 0)
    f.seek(-4-index_size, os.SEEK_END)
    # read indices
    readsize = 0
    sec_list = [] # [(name, offset, size), ...]
    calc_size = 0 # calculate the size we get for verification
    calc_size += len(MAGIC) # magic
    while readsize < index_size:
        nums = struct.unpack('L'*6,f.read(4*6))
        readsize += 4*6
        sec_size = nums[0]
        secname_size = nums[5]
        # read secname
        secname = f.read(secname_size)
        readsize += secname_size
        pad_size = pad(secname_size)
        f.read(pad_size) # pad to 4bytes
        readsize += pad_size
        
        sec_list.append((secname, calc_size, sec_size)) #(name, offset, size)
        calc_size += sec_size + pad(sec_size) # sections are also pad to 4bytes

    # print sec_list

    calc_size += index_size
    calc_size += 4 # index_size dword
    # check file size correct
    f.seek(0, os.SEEK_END)
    fsize = f.tell()
    assert fsize == calc_size # check if size match

    # create target dirs
    if os.path.exists(dirname):
        return
    os.makedirs(dirname)
    for name, offset, secsize in sec_list:
        # save each section
        #print 'writing: %s, offset %d, size %d' % (name, offset, secsize)
        f.seek(offset)
        content = f.read(secsize)
        open(dirname+'/'+name, 'wb').write(content)
    
    f.close()

def create(fname, dirname):
    f = open(fname, 'wb')
    f.write(MAGIC) # binsec magic
    
    secnames = []
    for secname in os.listdir(dirname):
        if os.path.isfile(dirname+'/'+secname):
            secnames.append(secname)
        else:
            print 'skipping', secname
    
    sections = [] # [(name, offset, size),...]
    # writing each section contents
    for secname in secnames:
        content = open(dirname+'/'+secname,'rb').read()
        secsize = len(content)
        offset = f.tell()
        assert((offset % 4) == 0) # check padding
        #print 'packing %s, offset %d, size %d' % (secname, offset, secsize)
        f.write(content)
        # add padding
        padsize = pad(secsize)
        f.write('\x00'*padsize)
        
        sections.append((secname, offset, secsize))
        
    # generate index
    index = ''
    for secname, offset, secsize in sections:
        index += struct.pack('L'*6, secsize, 0,0,0,0, len(secname))
        index += secname
        index += '\x00' * pad(len(secname))

    index_size = len(index)
    f.write(index)
    f.write(struct.pack('L', index_size))
    f.close()

# Extract / Creat .cdata file *END*


def getNodeValue(node, index = 0):
    return node.childNodes[index].nodeValue if node else ''
    
def setNodeValue(node, value, index = 0):
    if (node):
        node.childNodes[index].nodeValue = value

def getNode(node, name):
    return node.getElementsByTagName(name) if node else []

'''
def bilinearInterp(s, x, y):
    # 2 3
    # 0 1
    s1 = s[0] * (1 - x) + s[1] * x
    s2 = s[2] * (1 - x) + s[3] * x
    s = s1 * (1 - y) + s2 * y
    return s

def getHeight(x, y, fileName):
    if (x > 100 or y > 100):
        # 03_yhj_new/0000fff8o[TMP]/terrain.tmp
        print fileName
        posX, posY = decodeHex(fileName.split('/')[1])
        if (x > 100):
            posX += 1
            x -= 100
        if (y > 100):
            posY += 1
            y -= 100
        if (fileName.split('/')[1].find('TMP') == -1):
            fileName = fileName.split('/')[0] + '/' + encodeHex(posX, posY) + ('/terrain.tmp')
        else:
            fileName = fileName.split('/')[0] + '/' + encodeHex(posX, posY) + ('TMP/terrain.tmp')
        print x, y, fileName
        #return -2.0
    
    f = open(fileName, 'r')
    contents = f.read().split(' ')
    f.close()

    # [0, 50)
    xInt = int(x * 0.5)
    yInt = int(y * 0.5)
    xFrac = x * 0.5 - xInt
    yFrac = y * 0.5 - yInt
    xInt += 1
    yInt += 1

    indices = []
    indices.append(yInt * g_heightmapSize + xInt)
    indices.append(indices[0] + 1)
    indices.append(indices[0] + g_heightmapSize)
    indices.append(indices[0] + g_heightmapSize + 1)

    heights = []
    heights.append(float(contents[indices[0]]))
    heights.append(float(contents[indices[1]]))
    heights.append(float(contents[indices[2]]))
    heights.append(float(contents[indices[3]]))

    return bilinearInterp(heights, xFrac, yFrac)
'''

def translateMatrix(matrix, x, z):    
    matrix[3][0] = matrix[3][0] * 2.0 / 3.0 + x
    matrix[3][2] = matrix[3][2] * 2.0 / 3.0 + z
    matrix[3][1] = matrix[3][1] * 2.0 / 3.0
    		
def scaleMatrix(matrix, scale = 2.0 / 3.0):
    newmatrix = []
    row0 = []
    for i in range(3):
        row0.append(matrix[0][i] * scale)
    row1 = []
    for i in range(3):
        row1.append(matrix[1][i] * scale)
    row2 = []
    for i in range(3):
        row2.append(matrix[2][i] * scale)
    newmatrix.append(row0)
    newmatrix.append(row1)
    newmatrix.append(row2)
    newmatrix.append(matrix[3])
    return newmatrix

def insertNodeIndent(dom, node, insertNode, indent = 1):
    text = dom.createTextNode('\n' + '\t' * indent)
    node.parentNode.insertBefore(text, node)
    node.parentNode.insertBefore(insertNode, text)

def UpdateTransformMatrix(modelNode, x, z, det, first):
    transformNode = getNode(modelNode, 'transform')
    matrix = []
    row0 = getNode(transformNode[0], 'row0')
    matrix.append([float(value) for value in getNodeValue(row0[0]).split(' ')])
    row1 = getNode(transformNode[0], 'row1')
    matrix.append([float(value) for value in getNodeValue(row1[0]).split(' ')])
    row2 = getNode(transformNode[0], 'row2')
    matrix.append([float(value) for value in getNodeValue(row2[0]).split(' ')])
    row3 = getNode(transformNode[0], 'row3')
    matrix.append([float(value) for value in getNodeValue(row3[0]).split(' ')])

    # Determine whether the object in this chunk
    if (det[0]):
        if (first[0]):
            if (matrix[3][0] < 50.0):
                return False
        elif (matrix[3][0] >= 50.0):
            return False
    if (det[1]):
        if (first[1]):
            if (matrix[3][2] < 50.0):
                return False
        elif (matrix[3][2] >= 50.0):
            return False

    translateMatrix(matrix, x, z)
    matrix = scaleMatrix(matrix)

    row = '\t%.6f %.6f %.6f\t' % (matrix[0][0], matrix[0][1], matrix[0][2])
    setNodeValue(row0[0], row)   
    row = '\t%.6f %.6f %.6f\t' % (matrix[1][0], matrix[1][1], matrix[1][2])
    setNodeValue(row1[0], row)   
    row = '\t%.6f %.6f %.6f\t' % (matrix[2][0], matrix[2][1], matrix[2][2])
    setNodeValue(row2[0], row)   
    row = '\t%.6f %.6f %.6f\t' % (matrix[3][0], matrix[3][1], matrix[3][2])
    setNodeValue(row3[0], row)

    return True   

def UpdateLight(lightNode, x, z, det, first):
    positionNode = getNode(lightNode, 'position')
    pos = [float(value) for value in getNodeValue(positionNode[0]).split(' ')]

    # Determine whether the object in this chunk
    if (det[0]):
        if (first[0]):
            if (pos[0] < 50.0):
                return False
        elif (pos[0] >= 50.0):
            return False
    if (det[1]):
        if (first[1]):
            if (pos[2] < 50.0):
                return False
        elif (pos[2] >= 50.0):
            return False

    pos[0] = pos[0] * 2.0 / 3.0 + x
    pos[2] = pos[2] * 2.0 / 3.0 + z
    pos[1] = pos[1] * 2.0 / 3.0
    setNodeValue(positionNode[0], '\t%.6f %.6f %.6f\t' % (pos[0], pos[1], pos[2])) 

    inRadNode = getNode(lightNode, 'innerRadius') 
    setNodeValue(inRadNode[0], '\t%.6f\t' % (float(getNodeValue(inRadNode[0])) * 2.0 / 3.0)) 
    outRadNode = getNode(lightNode, 'outerRadius') 
    setNodeValue(outRadNode[0], '\t%.6f\t' % (float(getNodeValue(outRadNode[0])) * 2.0 / 3.0)) 

    return True

def UpdateMusic(musicNode, x, z, det, first):
    positionNode = getNode(musicNode, 'position')
    pos = [float(value) for value in getNodeValue(positionNode[0]).split(' ')]

    # Determine whether the object in this chunk
    if (det[0]):
        if (first[0]):
            if (pos[0] < 50.0):
                return False
        elif (pos[0] >= 50.0):
            return False
    if (det[1]):
        if (first[1]):
            if (pos[2] < 50.0):
                return False
        elif (pos[2] >= 50.0):
            return False

    pos[0] = pos[0] * 2.0 / 3.0 + x
    pos[2] = pos[2] * 2.0 / 3.0 + z
    pos[1] = pos[1] * 2.0 / 3.0
    setNodeValue(positionNode[0], '\t%.6f %.6f %.6f\t' % (pos[0], pos[1], pos[2])) 

    radNode = getNode(musicNode, 'radius') 
    setNodeValue(radNode[0], '\t%.6f\t' % (float(getNodeValue(radNode[0])) * 2.0 / 3.0)) 

    return True

def insertDocNodes(doc, insertNodes, lastNode):
    for insertNode in insertNodes:
        insertNodeIndent(doc, lastNode, insertNode)

def getHeightMap(file):
    #global g_heightmapSize
    f = open(file, 'rb')    
    header = f.read(256) # read headers
    version, w, h, spacing, ntex, texnamesize = struct.unpack('LLLfLL', header[:4*6])
    assert(w==h)
    assert(w == g_heightmapSize)
    assert(ntex>0)
    assert(texnamesize==g_blendTexSize)
    #print 'info'
    #print version, w, h, spacing, ntex, texnamesize
    
    texnames = []
    for i in range(ntex): # extract tex names
        texname = f.read(texnamesize)
        texname = texname.replace('\x00','')
        texnames.append(texname)
    #print texnames  
    
    heights = struct.unpack('f'*w*h, f.read(4*w*h))  
    f.close()
    if os.path.exists(file + '.tmp'):
        return heights
    f = open(file + '.tmp','w')
    for value in heights:
        f.write(str(value) + ' ')
    f.close()
    return heights

def calcSurroundingIndex(height, x, y, seq):
    #global g_heightmapSize
    # 7 8 9
    # 4 5 6
    # 1 2 3
    index = []
    index.append(seq * g_heightmapSize * g_heightmapSize + (y - 1) * g_heightmapSize + x - 1)
    index.append(seq * g_heightmapSize * g_heightmapSize + (y - 1) * g_heightmapSize + x)
    index.append(seq * g_heightmapSize * g_heightmapSize + (y - 1) * g_heightmapSize + x + 1)
    index.append(seq * g_heightmapSize * g_heightmapSize +  y      * g_heightmapSize + x - 1)
    index.append(seq * g_heightmapSize * g_heightmapSize +  y      * g_heightmapSize + x)
    index.append(seq * g_heightmapSize * g_heightmapSize +  y      * g_heightmapSize + x + 1)
    index.append(seq * g_heightmapSize * g_heightmapSize + (y + 1) * g_heightmapSize + x - 1)
    index.append(seq * g_heightmapSize * g_heightmapSize + (y + 1) * g_heightmapSize + x)
    index.append(seq * g_heightmapSize * g_heightmapSize + (y + 1) * g_heightmapSize + x + 1)
    heights = []
    heights.append(height[index[0]])
    heights.append(height[index[1]])
    heights.append(height[index[2]])
    heights.append(height[index[3]])
    heights.append(height[index[4]])
    heights.append(height[index[5]])
    heights.append(height[index[6]])
    heights.append(height[index[7]])
    heights.append(height[index[8]])
    return heights

def linearInterp(s):
    # 7 8 9
    # 4 5 6
    # 1 2 3
    return 0.5 * ((s[0] + s[2] + s[6] + s[8]) * 0.0625 + (s[1] + s[3] + s[5] + s[7]) * 0.125 + s[4] * 0.25)

def calcHeightMapChunkIndex(x, y, seq):
    return seq * g_heightmapSize * g_heightmapSize +  y * g_heightmapSize + x

def determineHeightMapChunk(pix, heights, odd): 
    # Chunk order:
    # 3 4
    # 1 2  
    if (not odd[0] and not odd[1]):
        # 0-51
        for y in range(0, g_heightmapSize - 2):
            # [0 - 51)
            for x in range(0, g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x + 1,                   y + 1, 0)]
            # [51 - 76)
            for x in range(g_heightmapSize - 2, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x - g_heightmapSize + 4, y + 1, 1)]
        # 51-76
        for y in range(g_heightmapSize - 2, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
            # [0 - 51)
            for x in range(0, g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x + 1,                   y - g_heightmapSize + 3, 2)]
            # [51 - 76)
            for x in range(g_heightmapSize - 2, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x - g_heightmapSize + 4, y - g_heightmapSize + 3, 3)]

    elif (odd[0] and not odd[1]):
        # 0-51
        for y in range(0, g_heightmapSize - 2):
            # [0-26)
            for x in range(0, (g_heightmapSize - 3) / 2 + 1):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x + (g_heightmapSize - 3) / 2 + 1, y + 1, 0)]
            # [26-76)
            for x in range((g_heightmapSize - 3) / 2 + 1, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x - (g_heightmapSize - 3) / 2 + 1, y + 1, 1)]
        # 51-76
        for y in range(g_heightmapSize - 2, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
            for x in range(0, (g_heightmapSize - 3) / 2 + 1):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x + (g_heightmapSize - 3) / 2 + 1, y - g_heightmapSize + 3, 2)]
            for x in range((g_heightmapSize - 3) / 2 + 1, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x - (g_heightmapSize - 3) / 2 + 1, y - g_heightmapSize + 3, 3)]

    elif (not odd[0] and odd[1]):
        # 0-26
        for y in range(0, (g_heightmapSize - 3) / 2 + 1):
            for x in range(0, g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x + 1,                   y + (g_heightmapSize - 3) / 2 + 1, 0)]
            for x in range(g_heightmapSize - 2, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x - g_heightmapSize + 4, y + (g_heightmapSize - 3) / 2 + 1, 1)]
        # 26-76
        for y in range((g_heightmapSize - 3) / 2 + 1, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
            for x in range(0, g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x + 1,                   y - (g_heightmapSize - 3) / 2 + 1, 2)]
            for x in range(g_heightmapSize - 2, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x - g_heightmapSize + 4, y - (g_heightmapSize - 3) / 2 + 1, 3)]

    elif (odd[0] and odd[1]):
        # 0-26
        for y in range(0, (g_heightmapSize - 3) / 2 + 1):
            for x in range(0, (g_heightmapSize - 3) / 2 + 1):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x + (g_heightmapSize - 3) / 2 + 1, y + (g_heightmapSize - 3) / 2 + 1, 0)]
            for x in range((g_heightmapSize - 3) / 2 + 1, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x - (g_heightmapSize - 3) / 2 + 1, y + (g_heightmapSize - 3) / 2 + 1, 1)]
        # 26-76
        for y in range((g_heightmapSize - 3) / 2 + 1, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
            for x in range(0, (g_heightmapSize - 3) / 2 + 1):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x + (g_heightmapSize - 3) / 2 + 1, y - (g_heightmapSize - 3) / 2 + 1, 2)]
            for x in range((g_heightmapSize - 3) / 2 + 1, (g_heightmapSize - 3) / 2 + g_heightmapSize - 2):
                pix[x, y] = 2.0 / 3.0 * heights[calcHeightMapChunkIndex(x - (g_heightmapSize - 3) / 2 + 1, y - (g_heightmapSize - 3) / 2 + 1, 3)]
    
def scaleHeightMap(dirName, dirName1, dirName2, dirName3, dirName4, odd):
    # Chunk order:
    # 3 4
    # 1 2
    heights = []

    heights += getHeightMap(dirName1 + '/terrain')
    heights += getHeightMap(dirName2 + '/terrain')
    heights += getHeightMap(dirName3 + '/terrain')
    heights += getHeightMap(dirName4 + '/terrain')
'''
    # Fill in image
    im = Image.new('F', (76, 76))
    pix = im.load()
    determineHeightMapChunk(pix, heights, odd)
    # Scale using bilinear
    im = im.resize((g_heightmapSize, g_heightmapSize), Image.BILINEAR)
    pix = im.load()

    # Calc new scaled map
    newHeights = []

    # Boundary
    for width in range(g_heightmapSize):
        newHeights.append(0.0)
    # Append value
    for height in range(g_heightmapSize - 2):
        newHeights.append(0.0)
        for width in range(g_heightmapSize - 2):
            newHeights.append(pix[width, height])
        newHeights.append(0.0)
    # Boundary
    for width in range(g_heightmapSize):
        newHeights.append(0.0)

    assert len(newHeights) == g_heightmapSize * g_heightmapSize
        
    f = open(dirName + '/terrain.tmp', 'w')
    for value in newHeights:
        f.write(str(value) + ' ')
    f.close()
'''
def decodeHex(fileName):
    x = eval('0x' + fileName[0:4])
    y = eval('0x' + fileName[4:8])
    ############hard coding###############
    # Overflow
    if (x > 32767):
        x -= 65536
    if (y > 32767):
        y -= 65536
    return (x, y)

def encodeHex(x, y):
    if (x < 0):
        x += 65536
    if (y < 0):
        y += 65536
    fileName = '%04x%04xo' % (x, y)
    return fileName

def getSurroundingHMap(dirName, x, y, newPosCenter):
    fileNames = []
    fileNames.append(dirName + '/' + encodeHex(x + 1, y - 1))
    fileNames.append(dirName + '/' + encodeHex(x,     y - 1))
    fileNames.append(dirName + '/' + encodeHex(x - 1, y - 1))
    fileNames.append(dirName + '/' + encodeHex(x + 1, y))
    fileNames.append(dirName + '/' + encodeHex(x - 1, y))
    fileNames.append(dirName + '/' + encodeHex(x + 1, y + 1))
    fileNames.append(dirName + '/' + encodeHex(x    , y + 1))
    fileNames.append(dirName + '/' + encodeHex(x - 1, y + 1))

    if (isChunkInDirectories(x + 1, y - 1, newPosCenter)):
        fileNames[0] = GetChunkDirectory(fileNames[0])
    if (isChunkInDirectories(x,     y - 1, newPosCenter)):
        fileNames[1] = GetChunkDirectory(fileNames[1])
    if (isChunkInDirectories(x - 1, y - 1, newPosCenter)):
        fileNames[2] = GetChunkDirectory(fileNames[2])
    if (isChunkInDirectories(x + 1, y    , newPosCenter)):
        fileNames[3] = GetChunkDirectory(fileNames[3])
    if (isChunkInDirectories(x - 1, y    , newPosCenter)):
        fileNames[4] = GetChunkDirectory(fileNames[4])
    if (isChunkInDirectories(x + 1, y + 1, newPosCenter)):
        fileNames[5] = GetChunkDirectory(fileNames[5])
    if (isChunkInDirectories(x    , y + 1, newPosCenter)):
        fileNames[6] = GetChunkDirectory(fileNames[6])
    if (isChunkInDirectories(x - 1, y + 1, newPosCenter)):
        fileNames[7] = GetChunkDirectory(fileNames[7])

    return fileNames

def fulfillHeightBoundary(heights, fileName, t):
    f = open(fileName + '/terrain.tmp', 'r')
    contents = f.read().split(' ')
    f.close()
    if (t == 0):
        # bottom
        for i in range(1, g_heightmapSize - 1):
            heights[i] = float(contents[(g_heightmapSize - 3) * g_heightmapSize + i])
    elif (t == 1):
        # up
        for i in range(1, g_heightmapSize - 1):
            heights[(g_heightmapSize - 1) * g_heightmapSize + i] = float(contents[g_heightmapSize * 2 + i])
            heights[(g_heightmapSize - 2) * g_heightmapSize + i] = float(contents[g_heightmapSize + i])
    elif (t == 2):
        # right
        for i in range(1, g_heightmapSize - 1):
            heights[i * g_heightmapSize + g_heightmapSize - 1] = float(contents[i * g_heightmapSize + 2])
            heights[i * g_heightmapSize + g_heightmapSize - 2] = float(contents[i * g_heightmapSize + 1])
    elif (t == 3):
        # left
        for i in range(1, g_heightmapSize - 1):
            heights[i * g_heightmapSize] = float(contents[i * g_heightmapSize + g_heightmapSize - 3])
    elif (t == 4):
        # bottom right corner
        heights[g_heightmapSize - 1] = float(contents[(g_heightmapSize - 3) * g_heightmapSize + 2])
        heights[g_heightmapSize * 2 - 2] = float(contents[(g_heightmapSize - 2) * g_heightmapSize + 1])
    elif (t == 5):
        # bottom left corner
        heights[0] = float(contents[(g_heightmapSize - 2) * g_heightmapSize - 3])
    elif (t == 6):
        # up right corner
        heights[g_heightmapSize * g_heightmapSize - 1] = float(contents[g_heightmapSize + 2])
        heights[g_heightmapSize * (g_heightmapSize - 1) - 2] = float(contents[g_heightmapSize + 1])
    else:
        # up left corner
        heights[(g_heightmapSize - 1) * g_heightmapSize] = float(contents[g_heightmapSize + g_heightmapSize - 3])
            

def UnionHeightMap(dirName, x, y, xBegin, yBegin, xRange, yRange, oldFile, newPosCenter):
    x = x + xBegin
    y = y + yBegin
    fileDir = dirName + '/' + encodeHex(x, y)
    if (isChunkInDirectories(x, y, newPosCenter)):
        fileDir = GetChunkDirectory(fileDir)
    f = open(fileDir + '/terrain.tmp', 'r')
    heightMap = f.read()
    f.close()    
    heights = [float(value) for value in heightMap[:-1].split(' ')]
    
    # 7 6 5      7 1 6
    # 4   3  =>  3   2
    # 2 1 0      5 0 4
    fileNames = getSurroundingHMap(dirName, x, y, newPosCenter)
    #print fileDir
    # Assert boundary
    if (x - 1 >= xBegin):
        fulfillHeightBoundary(heights, fileNames[4], 3)
        #print 0, fileNames[4]
    if (x + 1 < xBegin + xRange):
        fulfillHeightBoundary(heights, fileNames[3], 2)
        #print 1, fileNames[3]
    if (y - 1 >= yBegin):
        fulfillHeightBoundary(heights, fileNames[1], 0)
        #print 2, fileNames[1]
    if (y + 1 < yBegin + yRange):
        fulfillHeightBoundary(heights, fileNames[6], 1)
        #print 3, fileNames[6]
    if (x - 1 >= xBegin and y - 1 >= yBegin):        
        fulfillHeightBoundary(heights, fileNames[2], 5)
        #print 4, fileNames[2]
    if (x + 1 < xBegin + xRange and y - 1 >= yBegin):  
        fulfillHeightBoundary(heights, fileNames[0], 4)
        #print 5, fileNames[0]
    if (x - 1 >= xBegin and y + 1 < yBegin + yRange):      
        fulfillHeightBoundary(heights, fileNames[7], 7)
        #print 6, fileNames[7]
    if (x + 1 < xBegin + xRange and y + 1 < yBegin + yRange):
        fulfillHeightBoundary(heights, fileNames[5], 6)
        #print 7, fileNames[5]

    # read headers
    f = open(oldFile + 'TMP/terrain', 'rb')    
    header = f.read(256) 
    version, w, h, spacing, ntex, texnamesize = struct.unpack('LLLfLL', header[:4*6])
    #print version, w, h, spacing, ntex, texnamesize
    assert(w==h)
    assert(w>0)
    assert(ntex>0)
    assert(texnamesize==g_blendTexSize)
    header += f.read(texnamesize * ntex) 
    f.close()
    
    # Writeback to terrain file
    f = open(fileDir + '/terrain', 'rb+')
    #f.seek(256+texnamesize*ntex)
    f.write(header)
    f.write(struct.pack('f'*w*h,*heights))
    f.close()

def parseDirectory(dirName):
    xmin = 2048
    xmax = -2048
    ymin = 2048
    ymax = -2048
    for f in os.listdir(dirName):
        if f[-6:] == '.chunk':
            x, y = decodeHex(f)
            if (x > xmax):
                xmax = x
            if (x < xmin):
                xmin = x
            if (y > ymax):
                ymax = y
            if (y < ymin):
                ymin = y
        elif os.path.isfile(dirName + '/' + f) == False:
            if os.path.exists(dirName + '/' + f + '/sep'):
                for f1 in os.listdir(dirName + '/' + f + '/sep'):
                    if f1[-6:] == '.chunk':
                        x, y = decodeHex(f1)
                        if (x > xmax):
                            xmax = x
                        if (x < xmin):
                            xmin = x
                        if (y > ymax):
                            ymax = y
                        if (y < ymin):
                            ymin = y
    return (xmin, xmax, ymin, ymax)

def unionImage(newIm, im, width, height, width1, height1, _width, _height):
    newPix = newIm.load()
    pix = im.load()
    totalwidth, totalheight = im.size
    for y in range(_height):
        for x in range(_width):
            newPix[x + width, y + height] = pix[x + width1, totalheight - y - height1 - 1]  

def splitUnionPNG(newIm, im1, im2, im3, im4, blendTexSizeX, blendTexSizeY, odd):
    # Union 4 PNGs
    # 3 4       1 2
    # 1 2   =>  3 4 (TEX coordinate: up->down | left->right)
    if (not odd[0] and not odd[1]):
        # 64
        # |
        # 0 - 128
        unionImage(newIm, im3, 0, 0, 0, blendTexSizeY / 2, blendTexSizeX, blendTexSizeY / 2)
        #     64
        #     |
        # 0 - 128 - 192
        unionImage(newIm, im4, blendTexSizeX, 0, 0, blendTexSizeY / 2, blendTexSizeX / 2, blendTexSizeY / 2)
        # 192
        # |
        # 64 - 128
        # |
        # 0
        unionImage(newIm, im1, 0,   blendTexSizeY / 2, 0, 0, blendTexSizeX, blendTexSizeY)
        #      192
        #       |
        # 64 - 128 - 192
        # |
        # 0
        unionImage(newIm, im2, blendTexSizeX, blendTexSizeY / 2, 0, 0, blendTexSizeX / 2, blendTexSizeY)

    elif (odd[0] and not odd[1]):
        # 64
        # |
        # 0 - 64
        unionImage(newIm, im3, 0, 0, blendTexSizeX / 2, blendTexSizeY / 2, blendTexSizeX / 2, blendTexSizeY / 2)
        #     64
        #     |
        # 0 - 64 - 192
        unionImage(newIm, im4, blendTexSizeX / 2, 0, 0, blendTexSizeY / 2, blendTexSizeX, blendTexSizeY / 2)
        # 192
        # |
        # 64 - 64
        # |
        # 0
        unionImage(newIm, im1, 0, blendTexSizeY / 2, blendTexSizeX / 2, 0, blendTexSizeX / 2, blendTexSizeY)
        #      192
        #       |
        # 64 - 64 - 192
        # |
        # 0
        unionImage(newIm, im2, blendTexSizeX / 2, blendTexSizeY / 2, 0, 0, blendTexSizeX, blendTexSizeY)

    elif (not odd[0] and odd[1]):
        # 128
        # |
        # 0 - 128
        unionImage(newIm, im3, 0, 0, 0, 0, blendTexSizeX, blendTexSizeY)
        #     128
        #     |
        # 0 - 128 - 192
        unionImage(newIm, im4, blendTexSizeX, 0, 0, 0, blendTexSizeX / 2, blendTexSizeY)
        # 192
        # |
        # 128 - 128
        # |
        # 0
        unionImage(newIm, im1, 0, blendTexSizeY, 0, 0, blendTexSizeX, blendTexSizeY / 2)
        #      192
        #       |
        # 128 - 128 - 192
        # |
        # 0
        unionImage(newIm, im2, blendTexSizeX, blendTexSizeY, 0, 0, blendTexSizeX / 2, blendTexSizeY / 2)

    elif (odd[0] and odd[1]):
        # 128
        # |
        # 0 - 64
        unionImage(newIm, im3, 0, 0, blendTexSizeX / 2, 0, blendTexSizeX / 2, blendTexSizeY)
        #     128
        #     |
        # 0 - 64 - 192
        unionImage(newIm, im4, blendTexSizeX / 2, 0, 0, 0, blendTexSizeX, blendTexSizeY)
        # 192
        # |
        # 128 - 64
        # |
        # 0
        unionImage(newIm, im1, 0, blendTexSizeY, blendTexSizeX / 2, 0, blendTexSizeX / 2, blendTexSizeY / 2)
        #      192
        #       |
        # 128 - 64 - 192
        # |
        # 0
        unionImage(newIm, im2, blendTexSizeX / 2, blendTexSizeY, 0, 0, blendTexSizeX, blendTexSizeY / 2)

def handleOneCData(fileName, fileName1, fileName2, fileName3, fileName4, odd):
    # Chunk order:
    # 3 4
    # 1 2
    # 03_yhj/0000ffffo 
    extract(fileName + '.cdata', fileName)
    extract(fileName1 + '.cdata', fileName1 + 'TMP')
    extract(fileName2 + '.cdata', fileName2 + 'TMP')
    extract(fileName3 + '.cdata', fileName3 + 'TMP')
    extract(fileName4 + '.cdata', fileName4 + 'TMP')

    # Scale height map
    scaleHeightMap(fileName, fileName1 + 'TMP', fileName2 + 'TMP', fileName3 + 'TMP', fileName4 + 'TMP', odd)

    # Uncompress DDS to PNG
    os.chdir(fileName1 + 'TMP')
    #shutil.copyfile('../../texconv.exe', 'texconv.exe')
    os.system('texconv.exe -ft png -nologo blendTex')
    #os.remove('texconv.exe')
    
    # 03_yhj/000xfffx/sep/0000ffffo
    if (len(fileName1.split('/')) > 3):
        os.chdir('../../../../' + fileName2 + 'TMP')
    else:
        os.chdir('../../' + fileName2 + 'TMP')
    #shutil.copyfile('../../texconv.exe', 'texconv.exe')
    os.system('texconv.exe -ft png -nologo blendTex') 
    #os.remove('texconv.exe')
    
    if (len(fileName2.split('/')) > 3):
        os.chdir('../../../../' + fileName3 + 'TMP')
    else:
        os.chdir('../../' + fileName3 + 'TMP')
    #shutil.copyfile('../../texconv.exe', 'texconv.exe')
    os.system('texconv.exe -ft png -nologo blendTex') 
    #os.remove('texconv.exe')
    
    if (len(fileName3.split('/')) > 3):
        os.chdir('../../../../' + fileName4 + 'TMP')
    else:
        os.chdir('../../' + fileName4 + 'TMP')
    #shutil.copyfile('../../texconv.exe', 'texconv.exe')
    os.system('texconv.exe -ft png -nologo blendTex') 
    #os.remove('texconv.exe')
    if (len(fileName4.split('/')) > 3):
        os.chdir('../../../../')
    else:   
        os.chdir('../../')

    im1 = Image.open(fileName1 + 'TMP/blendTex.png')
    im2 = Image.open(fileName2 + 'TMP/blendTex.png')
    im3 = Image.open(fileName3 + 'TMP/blendTex.png')
    im4 = Image.open(fileName4 + 'TMP/blendTex.png')
    blendTexSizeX, blendTexSizeY = im1.size
    
    # Creates a new empty image
    # 128 * 128 => 192 * 192
    newIm = Image.new('RGBA', (blendTexSizeX * 3 / 2, blendTexSizeY * 3 / 2))
    splitUnionPNG(newIm, im1, im2, im3, im4, blendTexSizeX, blendTexSizeY, odd)
    newIm.save(fileName + '/blendTex.png', 'PNG')

    # Linear interpolate & compress PNG to DDS
    os.remove(fileName + '/blendTex')
    os.chdir(fileName)
    #shutil.copyfile('../../texconv.exe', 'texconv.exe')
    os.system('texconv.exe -ft dds -f DXT1 -w %d -h %d -if LINEAR -nologo blendTex.png' % (blendTexSizeX, blendTexSizeY))
    #os.remove('texconv.exe')
    if (len(fileName.split('/')) > 3):
        os.chdir('../../../../')
    else:
        os.chdir('../../')
    os.rename(fileName + '/blendTex.dds', fileName + '/blendTex')

def determineSplit(odd):
    # Determine 4 conditions
    det = []
    if (not odd[0] and not odd[1]):
        offsetX = [0, 100.0 * 2.0 / 3.0, 0, 100.0 * 2.0 / 3.0]
        offsetY = [0, 0, 100.0 * 2.0 / 3.0, 100.0 * 2.0 / 3.0]
        det.append([False, False])
        det.append([True, False])
        det.append([False, True])
        det.append([True, True])
    if (odd[0] and not odd[1]):
        offsetX = [-50.0 * 2.0 / 3.0, 50.0 * 2.0 / 3.0, -50.0 * 2.0 / 3.0, 50.0 * 2.0 / 3.0]
        offsetY = [0, 0, 100.0 * 2.0 / 3.0, 100.0 * 2.0 / 3.0]
        det.append([True, False])
        det.append([False, False])
        det.append([True, True])
        det.append([False, True])
    if (not odd[0] and odd[1]):
        offsetX = [0, 100.0 * 2.0 / 3.0 , 0, 100 * 2.0 / 3.0]
        offsetY = [-50.0 * 2.0 / 3.0, -50.0 * 2.0 / 3.0, 50.0 * 2.0 / 3.0, 50.0 * 2.0 / 3.0]
        det.append([False, True])
        det.append([True, True])
        det.append([False, False])
        det.append([True, False])
    if (odd[0] and odd[1]):
        offsetX = [-50.0 * 2.0 / 3.0, 50.0 * 2.0 / 3.0, -50.0 * 2.0 / 3.0, 50.0 * 2.0 / 3.0]
        offsetY = [-50.0 * 2.0 / 3.0, -50.0 * 2.0 / 3.0, 50.0 * 2.0 / 3.0, 50.0 * 2.0 / 3.0]
        det.append([True, True])
        det.append([False, True])
        det.append([True, False])
        det.append([False, False])

    return offsetX, offsetY, det

def handleOneChunk(fileName, fileName1, fileName2, fileName3, fileName4, odd):    
    # Chunk order:
    # 3 4
    # 1 2

    # Handle CData
    handleOneCData(fileName, fileName1, fileName2, fileName3, fileName4, odd)

    fileName += '.chunk'
    fileName1 += '.chunk'
    fileName2 += '.chunk'
    fileName3 += '.chunk'
    fileName4 += '.chunk'

    # Determine 4 conditions
    offsetX, offsetY, det = determineSplit(odd)

    # Update XML#1 bottom left
    doc1 = minidom.parse(fileName1)
    root1 = doc1.documentElement
    # Update nodes
    particleNodes1 = getNode(root1, 'particles')    
    for i in xrange(len(particleNodes1) - 1, -1, -1):
        if (not UpdateTransformMatrix(particleNodes1[i], offsetX[0], offsetY[0], det[0], odd)):
            particleNodes1.remove(particleNodes1[i])
    lightNodes1 = getNode(root1, 'omniLight')   
    for i in xrange(len(lightNodes1) - 1, -1, -1):
        if (not UpdateLight(lightNodes1[i], offsetX[0], offsetY[0], det[0], odd)):
            lightNodes1.remove(lightNodes1[i])
    musicNodes1 = getNode(root1, 'StaticMusic')
    for i in xrange(len(musicNodes1) - 1, -1, -1):
        if (not UpdateMusic(musicNodes1[i], offsetX[0], offsetY[0], det[0], odd)):
            musicNodes1.remove(musicNodes1[i])
    modelNodes1 = getNode(root1, 'model')    
    for i in xrange(len(modelNodes1) - 1, -1, -1):
        if (not UpdateTransformMatrix(modelNodes1[i], offsetX[0], offsetY[0], det[0], odd)):
            modelNodes1.remove(modelNodes1[i])

    # Update XML#2 bottom right
    doc2 = minidom.parse(fileName2)
    root2 = doc2.documentElement
    # Update node
    particleNodes2 = getNode(root2, 'particles')
    for i in xrange(len(particleNodes2) - 1, -1, -1):    
        if (not UpdateTransformMatrix(particleNodes2[i], offsetX[1], offsetY[1], det[1], odd)):
            particleNodes2.remove(particleNodes2[i])
    lightNodes2 = getNode(root2, 'omniLight')    
    for i in xrange(len(lightNodes2) - 1, -1, -1):   
        if (not UpdateLight(lightNodes2[i], offsetX[1], offsetY[1], det[1], odd)):
            lightNodes2.remove(lightNodes2[i])
    musicNodes2 = getNode(root2, 'StaticMusic')
    for i in xrange(len(musicNodes2) - 1, -1, -1):   
        if (not UpdateMusic(musicNodes2[i], offsetX[1], offsetY[1], det[1], odd)):
            musicNodes2.remove(musicNodes2[i])
    modelNodes2 = getNode(root2, 'model')
    for i in xrange(len(modelNodes2) - 1, -1, -1):
        if (not UpdateTransformMatrix(modelNodes2[i], offsetX[1], offsetY[1], det[1], odd)):
            modelNodes2.remove(modelNodes2[i])
        
    # Update XML#3 up left
    doc3 = minidom.parse(fileName3)
    root3 = doc3.documentElement
    # Update node
    particleNodes3 = getNode(root3, 'particles')    
    for i in xrange(len(particleNodes3) - 1, -1, -1):
        if (not UpdateTransformMatrix(particleNodes3[i], offsetX[2], offsetY[2], det[2], odd)):
            particleNodes3.remove(particleNodes3[i])
    lightNodes3 = getNode(root3, 'omniLight')    
    for i in xrange(len(lightNodes3) - 1, -1, -1):
        if (not UpdateLight(lightNodes3[i], offsetX[2], offsetY[2], det[2], odd)):
            lightNodes3.remove(lightNodes3[i])
    musicNodes3 = getNode(root3, 'StaticMusic')
    for i in xrange(len(musicNodes3) - 1, -1, -1):
        if (not UpdateMusic(musicNodes3[i], offsetX[2], offsetY[2], det[2], odd)):
            musicNodes3.remove(musicNodes3[i])
    modelNodes3 = getNode(root3, 'model')    
    for i in xrange(len(modelNodes3) - 1, -1, -1):
        if (not UpdateTransformMatrix(modelNodes3[i], offsetX[2], offsetY[2], det[2], odd)):
            modelNodes3.remove(modelNodes3[i])
        
    # Update XML#4 up right
    doc4 = minidom.parse(fileName4)
    root4 = doc4.documentElement
    # Update node
    particleNodes4 = getNode(root4, 'particles')   
    for i in xrange(len(particleNodes4) - 1, -1, -1):
        if (not UpdateTransformMatrix(particleNodes4[i], offsetX[3], offsetY[3], det[3], odd)):
            particleNodes4.remove(particleNodes4[i])
    lightNodes4 = getNode(root4, 'omniLight')    
    for i in xrange(len(lightNodes4) - 1, -1, -1):
        if (not UpdateLight(lightNodes4[i], offsetX[3], offsetY[3], det[3], odd)):
            lightNodes4.remove(lightNodes4[i])
    musicNodes4 = getNode(root4, 'StaticMusic')
    for i in xrange(len(musicNodes4) - 1, -1, -1):
        if (not UpdateMusic(musicNodes4[i], offsetX[3], offsetY[3], det[3], odd)):
            musicNodes4.remove(musicNodes4[i])
    modelNodes4 = getNode(root4, 'model')    
    for i in xrange(len(modelNodes4) - 1, -1, -1):
        if (not UpdateTransformMatrix(modelNodes4[i], offsetX[3], offsetY[3], det[3], odd)):
            modelNodes4.remove(modelNodes4[i])

    # Update new XML
    doc = minidom.parse(fileName)
    root = doc.documentElement
    # Insert model before 'terrain'
    boundaryNodes = getNode(root, 'boundary')
    insertDocNodes(doc, particleNodes1, boundaryNodes[0])
    insertDocNodes(doc, particleNodes2, boundaryNodes[0])
    insertDocNodes(doc, particleNodes3, boundaryNodes[0])
    insertDocNodes(doc, particleNodes4, boundaryNodes[0])
    
    insertDocNodes(doc, lightNodes1, boundaryNodes[0])
    insertDocNodes(doc, lightNodes2, boundaryNodes[0])
    insertDocNodes(doc, lightNodes3, boundaryNodes[0])
    insertDocNodes(doc, lightNodes4, boundaryNodes[0])

    insertDocNodes(doc, musicNodes1, boundaryNodes[0])
    insertDocNodes(doc, musicNodes2, boundaryNodes[0])
    insertDocNodes(doc, musicNodes3, boundaryNodes[0])
    insertDocNodes(doc, musicNodes4, boundaryNodes[0])

    insertDocNodes(doc, modelNodes1, boundaryNodes[0])
    insertDocNodes(doc, modelNodes2, boundaryNodes[0])
    insertDocNodes(doc, modelNodes3, boundaryNodes[0])
    insertDocNodes(doc, modelNodes4, boundaryNodes[0])

    # Writeback to chunk file
    f = file(fileName + '.tmp', 'w')
    doc.writexml(f)
    f.close()
    # Get rid of XML head info
    f1 = open(fileName, 'w+')
    f2 = open(fileName + '.tmp', 'r')
    f2.seek(22);
    f1.write(f2.read())
    f1.close()
    f2.close()
    os.remove(fileName + '.tmp')
        
def isOdd(x):
    return (x % 2 == 1)

def HandleDirectories(dirNameNew, dirNameOld):
    xNewMin, xNewMax, yNewMin, yNewMax = parseDirectory(dirNameNew)
    xOldMin, xOldMax, yOldMin, yOldMax = parseDirectory(dirNameOld)
    xNewRange = xNewMax - xNewMin + 1
    yNewRange = yNewMax - yNewMin + 1
    xOldRange = xOldMax - xOldMin + 1
    yOldRange = yOldMax - yOldMin + 1
    #print xOldMin, xOldMax, yOldMin, yOldMax, xOldRange, yOldRange
    #print xNewMin, xNewMax, yNewMin, yNewMax, xNewRange, yNewRange
    assert (xNewRange * 3 == xOldRange * 2)
    assert (yNewRange * 3 == yOldRange * 2)
    oldPosCenter = []
    oldPosCenter.append(xOldMin + xOldRange * 0.5 - 0.5)
    oldPosCenter.append(yOldMin + yOldRange * 0.5 - 0.5)
    newPosCenter = []
    newPosCenter.append(xNewMin + xNewRange * 0.5 - 0.5)
    newPosCenter.append(yNewMin + yNewRange * 0.5 - 0.5)

    # Uncompress all file
    for y in range(yNewRange):
        for x in range(xNewRange):
            posNewX = xNewMin + x
            posNewY = yNewMin + y
            odd = [isOdd(x), isOdd(y)]
            if odd[0]:
                posOldX = xOldMin + 3 * int(x / 2) + 1
            else:
                posOldX = xOldMin + 3 * int(x / 2)
            if odd[1]:
                posOldY = yOldMin + 3 * int(y / 2) + 1
            else:
                posOldY = yOldMin + 3 * int(y / 2)
            #print posNewX, posNewY, posOldX, posOldY

            # 03_yhj/0000ffffo 
            fileName = dirNameNew + '/' + encodeHex(posNewX, posNewY)            
            # Chunk order:
            # 3 4
            # 1 2
            fileName1 = dirNameOld + '/' + encodeHex(posOldX,     posOldY)
            fileName2 = dirNameOld + '/' + encodeHex(posOldX + 1, posOldY)
            fileName3 = dirNameOld + '/' + encodeHex(posOldX,     posOldY + 1)
            fileName4 = dirNameOld + '/' + encodeHex(posOldX + 1, posOldY + 1)
            # File in subdirectory?
            if (isChunkInDirectories(posNewX, posNewY, newPosCenter)):
                fileName = GetChunkDirectory(fileName)
            if (isChunkInDirectories(posOldX, posOldY, oldPosCenter)):
                fileName1 = GetChunkDirectory(fileName1)
            if (isChunkInDirectories(posOldX + 1, posOldY, oldPosCenter)):
                fileName2 = GetChunkDirectory(fileName2)
            if (isChunkInDirectories(posOldX, posOldY + 1, oldPosCenter)):
                fileName3 = GetChunkDirectory(fileName3)
            if (isChunkInDirectories(posOldX + 1, posOldY + 1, oldPosCenter)):
                fileName4 = GetChunkDirectory(fileName4)

            #print fileName, fileName1, fileName2, fileName3, fileName4

            print '---------------------DEALING WITH %s--------------------' % fileName
            handleOneChunk(fileName, fileName1, fileName2, fileName3, fileName4, odd)

    # Scale all heightmaps
    im = Image.new('F', (50 * xOldRange + 1, 50 * yOldRange + 1))
    pix = im.load()
    for y in range(yOldRange):
        for x in range(xOldRange):
            posOldX = xOldMin + x
            posOldY = yOldMin + y
            fileName = dirNameOld + '/' + encodeHex(posOldX, posOldY)
            # File in subdirectory?
            if (isChunkInDirectories(posOldX, posOldY, oldPosCenter)):
                fileName = GetChunkDirectory(fileName)

            f = open(fileName + 'TMP/terrain.tmp', 'r')
            contents = f.read().split(' ')
            f.close()

            pixPosX = x * 50
            pixPosY = y * 50
            for i in range(50):
                for j in range(50):
                    pix[pixPosX + j, pixPosY + i] = 2.0 / 3.0 * float(contents[(i + 1) * g_heightmapSize + j + 1])
                if (x == xOldRange - 1):
                    pix[pixPosX + 50, pixPosY + i] = 2.0 / 3.0 * float(contents[(i + 1) * g_heightmapSize + 51])
            if (y == yOldRange - 1):
                for j in range(50):
                    pix[pixPosX + j, pixPosY + 50] = 2.0 / 3.0 * float(contents[51 * g_heightmapSize + j + 1])
                    if (x == xOldRange - 1):
                        pix[pixPosX + 50, pixPosY + 50] = 2.0 / 3.0 * float(contents[51 * g_heightmapSize + 51])

    im = im.resize((50 * xNewRange + 1, 50 * yNewRange + 1), Image.BILINEAR)
    pix = im.load()

    #  Split all heightmaps
    for y in range(yNewRange):
        for x in range(xNewRange):
            posNewX = xNewMin + x
            posNewY = yNewMin + y
            # 03_yhj/0000ffffo 
            fileName = dirNameNew + '/' + encodeHex(posNewX, posNewY)     
            # File in subdirectory?
            if (isChunkInDirectories(posNewX, posNewY, newPosCenter)):
                fileName = GetChunkDirectory(fileName) 

            odd = [isOdd(x), isOdd(y)]
            if odd[0]:
                posOldX = xOldMin + 3 * int(x / 2) + 1
            else:
                posOldX = xOldMin + 3 * int(x / 2)
            if odd[1]:
                posOldY = yOldMin + 3 * int(y / 2) + 1
            else:
                posOldY = yOldMin + 3 * int(y / 2)                
            oldFile = dirNameOld + '/' + encodeHex(posOldX,     posOldY)
            # File in subdirectory?
            if (isChunkInDirectories(posOldX, posOldY, oldPosCenter)):
                oldFile = GetChunkDirectory(oldFile)

            heights = []
            pixPosX = x * 50
            pixPosY = y * 50
            if (y == 0):
                for j in range(53):
                    heights.append(0.0)
            else:
                if (x == 0):
                    heights.append(0.0)
                else:
                    heights.append(pix[pixPosX - 1, pixPosY - 1])
                for j in range(51):
                    heights.append(pix[pixPosX + j, pixPosY - 1])
                if (x == xNewRange - 1):
                    heights.append(0.0)
                else:
                    heights.append(pix[pixPosX + 51, pixPosY - 1])

            for i in range(51):
                if (x == 0):
                    heights.append(0.0)
                else:
                    heights.append(pix[pixPosX - 1, pixPosY + i])
                for j in range(51):
                    heights.append(pix[pixPosX + j, pixPosY + i])
                if (x == xNewRange - 1):
                    heights.append(0.0)
                else:
                    heights.append(pix[pixPosX + 51, pixPosY + i])

            if (y == yNewRange - 1):
                for j in range(53):
                    heights.append(0.0)
            else:
                if (x == 0):
                    heights.append(0.0)
                else:
                    heights.append(pix[pixPosX - 1, pixPosY + 51])
                for j in range(51):
                    heights.append(pix[pixPosX + j, pixPosY + 51])
                if (x == xNewRange - 1):
                    heights.append(0.0)
                else:
                    heights.append(pix[pixPosX + 51, pixPosY + 51])

            assert (len(heights) == 53 * 53)

            # read headers
            f = open(oldFile + 'TMP/terrain', 'rb')    
            header = f.read(256) 
            version, w, h, spacing, ntex, texnamesize = struct.unpack('LLLfLL', header[:4*6])
            header += f.read(texnamesize * ntex) 
            f.close()
    
            # Writeback to terrain file
            f = open(fileName + '/terrain', 'rb+')
            #f.seek(256+texnamesize*ntex)
            f.write(header)
            f.write(struct.pack('f'*w*h,*heights))
            f.close()

    '''
    # Union terrain gap
    for y in range(yNewRange):
        for x in range(xNewRange):
            odd = [isOdd(x), isOdd(y)]
            if odd[0]:
                posOldX = xOldMin + 3 * int(x / 2) + 1
            else:
                posOldX = xOldMin + 3 * int(x / 2)
            if odd[1]:
                posOldY = yOldMin + 3 * int(y / 2) + 1
            else:
                posOldY = yOldMin + 3 * int(y / 2)
            oldFile = dirNameOld + '/' + encodeHex(posOldX, posOldY)
            if (isChunkInDirectories(posOldX, posOldY, oldPosCenter)):
                oldFile = GetChunkDirectory(oldFile)
            UnionHeightMap(dirNameNew, x, y, xNewMin, yNewMin, xNewRange, yNewRange, oldFile, newPosCenter)
    '''

    # Generate CData
    for y in range(yNewRange):
        for x in range(xNewRange):   
            # Delete temp file in directory
            x1 = x + xNewMin
            y1 = y + yNewMin
            fileDir = dirNameNew + '/' + encodeHex(x1, y1)
            if (isChunkInDirectories(x1, y1, newPosCenter)):
                fileDir = GetChunkDirectory(fileDir)
            os.remove(fileDir + '/blendTex.png')
            create(fileDir + '.cdata', fileDir)

        
if __name__ == "__main__":    
    if len(sys.argv) <> 3:
        print 'usuage: %s new_world_directory old_world_directory' % sys.argv[0]
        exit()

    #print 'set environment. if error occurred, run it again.'        
    #os.system('setx PATH "%%PATH%%;%s"' % os.getcwd())
    newDir, oldDir = sys.argv[1:]
    HandleDirectories(newDir, oldDir)
