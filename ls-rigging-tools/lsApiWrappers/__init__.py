import maya.OpenMaya as om

def getMObject(objName):
    '''
    return MObject of objName [string]
    '''
    selList = om.MSelectionList()
    selList.add(objName)
    
    obj = om.MObject()

    selList.getDependNode(0, obj)
    
    return obj


def getDagPath(objName):
    '''
    return MDagPath of objName [string]
    '''
    selList = om.MSelectionList()
    selList.add(objName)
    
    dag = om.MDagPath()

    selList.getDagPath(0, dag)
    
    return dag