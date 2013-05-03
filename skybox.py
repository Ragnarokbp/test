import os, struct, sys
from xml.dom import minidom

def HandleSkyboxFile(fileName):
    # Update XML
    doc = minidom.parse(fileName)
    root = doc.documentElement
    # Update nodes
    positionNode = getNode(root, 'position')    
    pos = [float(value) for value in getNodeValue(positionNode[0]).split(' ')]
    pos[0] = pos[0] * 0.5 + 50
    pos[2] = pos[2] * 0.5 + 50
    pos[1] = pos[1] * 0.5
    setNodeValue(positionNode[0], '\t%.6f %.6f %.6f\t' % (pos[0], pos[1], pos[2])) 

    radNode = getNode(root, 'radius') 
    setNodeValue(radNode[0], '\t%.6f\t' % (float(getNodeValue(radNode[0])) * 0.5)) 

    distNode = getNode(root, 'fogDistance') 
    setNodeValue(distNode[0], '\t%.6f\t' % (float(getNodeValue(distNode[0])) * 0.5)) 

    dofNode = getNode(root, 'dofFarField') 
    setNodeValue(dofNode[0], '\t%.6f\t' % (float(getNodeValue(dofNode[0])) * 0.5)) 
    dofNode = getNode(root, 'dofNearField') 
    setNodeValue(dofNode[0], '\t%.6f\t' % (float(getNodeValue(dofNode[0])) * 0.5)) 
    dofNode = getNode(root, 'dofFocalField') 
    setNodeValue(dofNode[0], '\t%.6f\t' % (float(getNodeValue(dofNode[0])) * 0.5)) 
    dofNode = getNode(root, 'dofFocus') 
    setNodeValue(dofNode[0], '\t%.6f\t' % (float(getNodeValue(dofNode[0])) * 0.5))

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

def HandleDirectories(skyboxDir):	
    for f in os.listdir(skyboxDir):
        if os.path.isfile(skyboxDir + '/' + f):
        	if f[-4:] == '.xml':
        		HandleSkyboxFile(skyboxDir + '/' + f)

if __name__ == "__main__":    
    if len(sys.argv) <> 2:
        print 'usuage: %s skybox_directory' % sys.argv[0]
        exit()

    #print 'set environment. if error occurred, run it again.'        
    #os.system('setx PATH "%%PATH%%;%s"' % os.getcwd())
    skyboxDir = sys.argv[1]
    HandleDirectories(skyboxDir)
