import maya.cmds as mc
import pymel.core.datatypes as dt

def getPosTable(mesh, **kwargs):
    '''
    returns dictionary
    {vertId : dt.Point(x,y,z)}
    '''
    
    vertCount = mc.polyEvaluate(mesh, v=True)
    
    retDict = {}
    
    for vertId in range(vertCount):
        
        retDict[vertId] = dt.Point(*mc.pointPosition('%s.vtx[%d]' % (mesh, vertId), **kwargs))
        
    return retDict
    

def comparePosTables(table1, table2, tol=0.001):
    '''
    returns list of vertIds that have different position values
    '''
    retList = []
    
    for vertId, pos in table1.items():
        
        if vertId in table2.keys():
            
            if not pos.isEquivalent(table2[vertId], tol):
                
                retList.append(vertId)
                
    return retList