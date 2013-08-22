"""
UI commands for lsDfmTools (i.e. no passing arguments)
Calls function with the same name from lsDfmTools with user input from selection.
"""

import lsDfmTools as dt
import maya.cmds as mc
reload(dt)

def copyMeshShape():
    src, dest = mc.ls(os=True)[:2]
    dt.copyMeshShape(src, dest)

def getClusterFromTransform():
    '''
    return name of cluster deformer from selected transform
    '''
    sel = mc.ls(sl=1)[0]
    dfm = mc.listConnections(sel+'.worldMatrix', type='cluster', destination=True)[0]
    return dfm

def addVertsToDeformer():
    """
    Select verts, shift-select deformer transform, run
    Currently only works with clusters
    """
    selVerts = mc.ls(os=True, fl=True)[:-1]
    selTransform = mc.ls(os=True)[-1]
    selDfm = dt.getClusterFromTransform(selTransform)
    dt.addVertsToDeformer(selVerts, selDfm)
    
def removeVertsFromDeformer():
    '''
    Select verts, shift-select deformer transform, run
    Currently only works with clusters
    '''
    selVerts = mc.ls(os=True, fl=True)[:-1]
    selTransform = mc.ls(os=True)[-1]
    selDfm = dt.getClusterFromTransform(selTransform)
    dt.removeVertsFromDeformer(selVerts, selDfm)
    

def copyVertPos():
    '''
    Select verts, shift-select target to copy to, run
    '''
    srcVerts = mc.ls(os=True, fl=True)[:-1]
    target = mc.ls(os=True)[-1]
    dt.copyVertPos(srcVerts, target)
    
def copyVertPosFrom():
    '''
    Select verts on target mesh, shift-select source mesh
    '''
    destVerts = mc.ls(os=True, fl=True)[:-1]
    source = mc.ls(os=True)[-1]
    target = dt.getMeshName(destVerts[0])
    srcVerts = [vtxName.replace(target, source) for vtxName in destVerts]
    dt.copyVertPos(srcVerts, target)