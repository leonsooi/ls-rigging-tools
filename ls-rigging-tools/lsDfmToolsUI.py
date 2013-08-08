"""
UI commands for lsDfmTools (i.e. no passing arguments)
Calls function with the same name from lsDfmTools with user input from selection.
"""

import lsDfmTools as dt
import maya.cmds as mc
reload(dt)

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
    