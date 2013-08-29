import maya.cmds as mc

def selectVertsFromIdList(mesh, idList):
    '''
    '''
    sel = [mesh+'.vtx[%d]'%eachId for eachId in idList]
    mc.select(sel, r=True)