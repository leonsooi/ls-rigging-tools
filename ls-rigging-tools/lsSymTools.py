import maya.cmds as mc
import lsDfmTools as dt
import lsSelectTools as sel

def buildSymTable(mesh):
    symDict = {}
    posDict = {}
    negDict = {}
    
    # store positions in separate positive and negative dictionaries
    vtxCount = mc.polyEvaluate(mesh, v=1)
    for vtxvertId in range(vtxCount):
        posX, posY, posZ = mc.xform('%s.vtx[%d]'%(mesh,vtxvertId), q=1, t=1, os=1)
        if posX > 0:
            posDict[(posX,posY,posZ)] = vtxvertId
        elif posX < 0:
            negDict[(posX,posY,posZ)] = vtxvertId
    
    # match positive to negative verts in symmetry table
    for posKey, vtxvertId in posDict.items():
        negKey = (-posKey[0], posKey[1], posKey[2])
        if negKey in negDict:
            symDict[vtxvertId] = negDict[negKey]
    
    # select assymetrical verts
    asymVerts = ['%s.vtx[%d]'%(mesh, vertId) for vertId in range(vtxCount) if vertId not in symDict.keys() and vertId not in symDict.values()]
    mc.select(asymVerts)

    return symDict

def make2WaySymTable(symDict):
    '''
    '''
    revTable = {}
    
    for leftId, rightId in symDict.items():
        revTable[rightId] = leftId
        
    # add the two dictionaries together
    retTable = dict(symDict.items() + revTable.items())
    
    return retTable

def flipSelection(selVerts, symDict):
    '''
    '''
    symDict2 = make2WaySymTable(symDict)
    selList = []
    
    for eachVert in selVerts:
        vertId = dt.getComponentId(eachVert)
        if vertId in symDict2.keys():
            selList.append(symDict2[vertId])
        else:
            # if this vert is assymetrical (i.e. on the center line)
            # just add it as well...
            selList.append(vertId)
    
    mesh = dt.getMeshName(selVerts[0])
    sel.selectVertsFromIdList(mesh, selList)
    
    return selList